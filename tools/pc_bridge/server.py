"""PC bridge: an MCP server on the user's PC for a Claude Code cloud session (5.10.2026).

The cloud session edits the repo in its own clone and pushes a branch; this server, reached over
an ngrok tunnel, does on the PC what needs the PC: checks the branch out into its own worktree,
copies a mod into the live folder Documents/.../Victoria 3/mod, runs tools/run_vic3_sandbox.ps1
(the game takes the screen) and gives back logs, screenshots and the output of the repo's
Python tools. Files are readable only under the roots below; nothing here writes outside the
worktree, the live mod folder and the runs folder.

Every request must carry "Authorization: Bearer <token>", the token being _bridge/token.txt
(made on the first start). Run it in the user's desktop session, not as a service: a service
lives in session 0 and the game script cannot see the screen from there.

    _bridge/venv/Scripts/python.exe tools/pc_bridge/server.py      (start.ps1 also starts ngrok)
"""
import collections
import datetime
import fnmatch
import hmac
import io
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
from pathlib import Path

import uvicorn
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.transport_security import TransportSecuritySettings

REPO = Path(__file__).resolve().parents[2]            # vic3_mods (main checkout, never switched)
BRIDGE = REPO.parent / "_bridge"                      # not in git: token, worktree, runs, log
WT = BRIDGE / "wt"                                    # worktree for the cloud's branches
RUNS = BRIDGE / "runs"
DOCS = Path.home() / "Documents" / "Paradox Interactive" / "Victoria 3"
GAME = Path(r"C:\games\steam\steamapps\common\Victoria 3")
ORIG = REPO.parent / "vic3_mods_out"
WORKSHOP = Path(r"C:\games\steam\steamapps\workshop\content\529340")
ROOTS = {"docs": DOCS, "game": GAME, "runs": RUNS, "wt": WT, "orig": ORIG, "workshop": WORKSHOP}
PORT = int(os.environ.get("PC_BRIDGE_PORT", "8080"))
PY_TOOLS = {"parse_eflog": "tools/parse_eflog.py", "save_money_check": "tools/save_money_check.py",
            "save_ownership": "tools/save_ownership.py", "save_ownership_transfers": "tools/save_ownership_transfers.py",
            "save_construction_goods": "tools/save_construction_goods.py", "save_measure_ef": "tools/save_measure_ef.py"}
PY_TOOL_GLOBS = ("regen_*.py", "build_addon*.py", "pair_matrix.py", "content_holes.py", "check_*.py", "scan_*.py",
                 "stale_bodies.py", "replace_audit.py", "loc_dead_overrides.py", "list_lawgroups_diff.py")
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

BRIDGE.mkdir(exist_ok=True)
RUNS.mkdir(exist_ok=True)
TOKEN_FILE = BRIDGE / "token.txt"
if not TOKEN_FILE.exists():
    TOKEN_FILE.write_text(secrets.token_urlsafe(32), encoding="utf-8")
TOKEN = TOKEN_FILE.read_text(encoding="utf-8").strip()

_runs = {}            # run id -> Popen of this server's lifetime
_lock = threading.Lock()


def log(msg):
    with open(BRIDGE / "bridge.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")


def sh(args, cwd=None, timeout=300):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=timeout, creationflags=NO_WINDOW)
    if p.returncode:
        raise RuntimeError(f"{' '.join(map(str, args))} -> {p.returncode}\n{p.stdout}\n{p.stderr}")
    return p.stdout.strip()


def resolve(path):
    """'docs/logs/error.log', 'runs/r1/03_end.png' or an absolute path inside a root."""
    head, _, rest = path.replace("\\", "/").partition("/")
    p = (ROOTS[head] / rest) if head in ROOTS else Path(path)
    p = p.resolve()
    for root in ROOTS.values():
        if p == root.resolve() or root.resolve() in p.parents:
            return p
    raise ValueError(f"outside the allowed roots {', '.join(f'{k}={v}' for k, v in ROOTS.items())}: {path}")


def game_running():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq victoria3.exe", "/NH"], capture_output=True,
                         text=True, errors="replace", creationflags=NO_WINDOW).stdout
    return "victoria3.exe" in out.lower()


def active_run():
    with _lock:
        return next((rid for rid, p in _runs.items() if p.poll() is None), None)


mcp = FastMCP(
    "vic3-pc",
    instructions="The user's Windows PC with Victoria 3. Flow: checkout(branch) -> sync_mod() -> "
                 "start_run(...) -> run_status(id) every minute or two until finished -> read_text / grep / "
                 "get_image on runs/<id>/... and docs/... . See .claude/skills/vic3-sandbox/SKILL.md.",
    stateless_http=True, json_response=True, host="127.0.0.1", port=PORT,
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


@mcp.tool()
def checkout(branch: str = "main") -> str:
    """Fetch a branch of BEDTRIP/vic3_mods from GitHub and check it out (detached) in the bridge
    worktree _bridge/wt. sync_mod, start_run and py_tool use that worktree. Returns the commit."""
    if not re.fullmatch(r"[\w./-]+", branch) or ".." in branch or branch.startswith("-"):
        raise ValueError(f"bad branch name: {branch}")
    sh(["git", "-C", REPO, "fetch", "origin", f"+refs/heads/{branch}:refs/remotes/origin/{branch}"])
    if not (WT / ".git").exists():
        sh(["git", "-C", REPO, "worktree", "add", "--detach", WT, f"origin/{branch}"])
    else:
        sh(["git", "-C", WT, "checkout", "--detach", "--force", f"origin/{branch}"])
        sh(["git", "-C", WT, "clean", "-fdq"])
    log(f"checkout {branch}")
    return sh(["git", "-C", WT, "log", "-1", "--format=%h %ad %s", "--date=iso"])


@mcp.tool()
def sync_mod(repo_folder: str = "_ef/ef hotfix 1.13", live_name: str = "E&F Hotfix") -> dict:
    """Make the live mod Documents/.../Victoria 3/mod/<live_name> equal to <repo_folder> of the
    worktree: changed and new files are copied, files gone from the repo are moved to
    _to_delete/<date>/ inside the live mod (the project's rule). Refused while the game runs."""
    if game_running():
        raise RuntimeError("the game is running: the live copy is not synced during a run")
    src = (WT / repo_folder).resolve()
    dst = (DOCS / "mod" / live_name).resolve()
    if WT.resolve() not in src.parents or not src.is_dir():
        raise ValueError(f"no such folder in the worktree: {repo_folder}")
    if dst.parent != (DOCS / "mod").resolve() or not dst.is_dir():
        raise ValueError(f"no such live mod: {live_name}")
    skip = lambda rel: rel.parts[0] in ("_to_delete", ".git")
    copied, moved = [], []
    for f in src.rglob("*"):
        rel = f.relative_to(src)
        if f.is_file() and not skip(rel):
            t = dst / rel
            if not t.exists() or t.read_bytes().replace(b"\r\n", b"\n") != f.read_bytes().replace(b"\r\n", b"\n"):
                t.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, t)
                copied.append(str(rel))
    bin_ = dst / "_to_delete" / f"{datetime.date.today():%Y-%m-%d}"
    for t in list(dst.rglob("*")):
        rel = t.relative_to(dst)
        if t.is_file() and not skip(rel) and not (src / rel).exists():
            (bin_ / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(t, bin_ / rel)
            moved.append(str(rel))
    log(f"sync {repo_folder} -> {live_name}: {len(copied)} copied, {len(moved)} moved")
    return {"copied": copied, "moved_to_delete": moved}


@mcp.tool()
def start_run(run_minutes: int = 10, new_game: bool = False, tag: str = "", start_save: str = "",
              autosaves: int = 0, ai_tag: str = "all", commands: str = "", shots: bool = False,
              countries: str = "", load_wait_sec: int = 400) -> dict:
    """Start tools/run_vic3_sandbox.ps1 of the worktree in the background (parameters as in the
    skill vic3-sandbox). Returns the run id at once; poll run_status(id). Output: runs/<id>/."""
    if active_run() or game_running():
        raise RuntimeError("a run or the game is already going")
    rid = datetime.datetime.now().strftime("r%m%d_%H%M%S")
    out = RUNS / rid
    out.mkdir()
    args = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(WT / "tools" / "run_vic3_sandbox.ps1"),
            "-RunMinutes", str(int(run_minutes)), "-LoadWaitSec", str(int(load_wait_sec)),
            "-Autosaves", str(int(autosaves)), "-AiTag", ai_tag, "-OutDir", str(out)]
    if new_game:
        args.append("-NewGame")
    if shots:
        args.append("-Shots")
    for flag, val in (("-Tag", tag), ("-StartSave", start_save), ("-Commands", commands), ("-Countries", countries)):
        if val:
            args += [flag, val]
    stdout = open(out / "stdout.txt", "w", encoding="utf-8")
    p = subprocess.Popen(args, cwd=WT, stdout=stdout, stderr=subprocess.STDOUT, creationflags=NO_WINDOW)
    (out / "args.json").write_text(json.dumps(args[5:], ensure_ascii=False), encoding="utf-8")

    def wait():
        code = p.wait()
        stdout.close()
        (out / "exit.txt").write_text(str(code), encoding="utf-8")
        log(f"run {rid} exited {code}")

    with _lock:
        _runs[rid] = p
    threading.Thread(target=wait, daemon=True).start()
    log(f"run {rid} started: {args[5:]}")
    return {"id": rid, "out": f"runs/{rid}"}


def tail(path, n):
    with open(path, encoding="utf-8", errors="replace") as f:
        return "".join(collections.deque(f, n))


@mcp.tool()
def run_status(run_id: str, tail_lines: int = 30) -> dict:
    """State of a run: running / finished (exit code), the tail of its stdout and, once finished,
    of run.log (run.log is not read while the script writes it), and the files in runs/<id>."""
    out = resolve(f"runs/{run_id}")
    with _lock:
        p = _runs.get(run_id)
    exit_file = out / "exit.txt"
    state = ("running" if p and p.poll() is None else
             f"finished, exit {exit_file.read_text().strip()}" if exit_file.exists() else
             "unknown (the bridge was restarted during the run)")
    res = {"state": state, "game_running": game_running(),
           "stdout": tail(out / "stdout.txt", tail_lines) if (out / "stdout.txt").exists() else ""}
    if state != "running" and (out / "run.log").exists():
        res["run_log"] = tail(out / "run.log", tail_lines)
    res["files"] = sorted(f"{f.relative_to(out).as_posix()} {f.stat().st_size}" for f in out.rglob("*") if f.is_file())
    return res


@mcp.tool()
def stop_run(run_id: str = "") -> str:
    """Kill a run's script and the game (e.g. it stands on «Конец игры» after an annexation).
    The logs are then in docs/logs (the script did not copy them)."""
    with _lock:
        p = _runs.get(run_id) if run_id else None
    if p and p.poll() is None:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True, creationflags=NO_WINDOW)
    subprocess.run(["taskkill", "/F", "/IM", "victoria3.exe"], capture_output=True, creationflags=NO_WINDOW)
    log(f"stop {run_id}")
    return f"game running: {game_running()}"


@mcp.tool()
def list_dir(path: str = "runs", pattern: str = "*", limit: int = 200) -> list[str]:
    """Entries of a folder, newest first: '<name>[/] <size> <mtime>'. Roots: docs (Documents/
    Paradox Interactive/Victoria 3: mod, logs, save games, crashes), game (the game folder),
    runs (bridge runs), wt (the worktree)."""
    d = resolve(path)
    items = sorted((e for e in d.iterdir() if fnmatch.fnmatch(e.name, pattern)), key=lambda e: -e.stat().st_mtime)
    return [f"{e.name}{'/' if e.is_dir() else ''} {e.stat().st_size if e.is_file() else ''} "
            f"{datetime.datetime.fromtimestamp(e.stat().st_mtime):%Y-%m-%d %H:%M}" for e in items[:limit]]


@mcp.tool()
def read_text(path: str, offset: int = 0, limit: int = 400, from_end: bool = False) -> str:
    """Lines of a text file, numbered from 1; offset skips lines, from_end gives the last `limit`
    lines. Streams, so a 450 MB save is fine for its first lines but use grep to find things."""
    f = resolve(path)
    with open(f, encoding="utf-8-sig", errors="replace") as fh:
        if from_end:
            n, buf = 0, collections.deque(maxlen=limit)
            for n, line in enumerate(fh, 1):
                buf.append((n, line))
            return "".join(f"{i}\t{l}" for i, l in buf)
        out = []
        for i, line in enumerate(fh, 1):
            if i > offset + limit:
                out.append(f"... (more after line {i - 1})\n")
                break
            if i > offset:
                out.append(f"{i}\t{line}")
        return "".join(out)


@mcp.tool()
def grep(path: str, pattern: str, glob: str = "*", max_matches: int = 200, context: int = 0) -> str:
    """Regex search in a file or, recursively, in the files of a folder matching `glob`.
    Lines as 'file:line:text' (context lines with '-')."""
    rx = re.compile(pattern)
    p = resolve(path)
    files = [p] if p.is_file() else sorted(f for f in p.rglob(glob) if f.is_file())
    out, hits = [], 0
    for f in files:
        before = collections.deque(maxlen=context)
        after = 0
        with open(f, encoding="utf-8-sig", errors="replace") as fh:
            for i, line in enumerate(fh, 1):
                name = f.name if p.is_file() else f.relative_to(p).as_posix()
                if rx.search(line):
                    out += [f"{name}-{j}-{l.rstrip()}" for j, l in before]
                    before.clear()
                    out.append(f"{name}:{i}:{line.rstrip()}")
                    hits += 1
                    after = context
                    if hits >= max_matches:
                        return "\n".join(out + [f"... stopped at {max_matches} matches"])
                elif after:
                    out.append(f"{name}-{i}-{line.rstrip()}")
                    after -= 1
                else:
                    before.append((i, line))
    return "\n".join(out) or "no matches"


@mcp.tool()
def get_image(path: str, crop: list[float] | None = None, max_width: int = 1600) -> Image:
    """A screenshot (PNG/JPG). crop = [x0, y0, x1, y1] in fractions of the image (0..1), to read a
    tooltip at full resolution instead of the whole 2560x1440 screen; then scaled to max_width."""
    from PIL import Image as PImage
    im = PImage.open(resolve(path)).convert("RGB")
    if crop:
        w, h = im.size
        im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    if im.width > max_width:
        im = im.resize((max_width, round(im.height * max_width / im.width)))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=85)
    return Image(data=buf.getvalue(), format="jpeg")


@mcp.tool()
def py_tool(name: str, args: list[str]) -> str:
    """Run a repo tool of the worktree on the PC's files (saves are 450 MB, too big to fetch):
    parse_eflog (args: <run>/eflog.txt <out.json>) or save_money_check (args: [save] [TAG ...]).
    Paths in args may be 'runs/...' or 'docs/...'. Returns the output (tail)."""
    script = PY_TOOLS.get(name) or f"tools/{name}.py"
    if name not in PY_TOOLS and not (re.fullmatch(r"\w+", name) and any(fnmatch.fnmatch(f"{name}.py", g) for g in PY_TOOL_GLOBS)
                                     and (WT / script).is_file()):
        raise ValueError(f"tools: {', '.join(PY_TOOLS)} and {', '.join(PY_TOOL_GLOBS)}")
    real = [str(resolve(a)) if a.split("/")[0] in ROOTS else a for a in args]
    p = subprocess.run(["py", script, *real], cwd=WT, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=1200, creationflags=NO_WINDOW, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    log(f"py_tool {name} {real} -> {p.returncode}")
    return f"exit {p.returncode}\n{(p.stdout + p.stderr)[-20000:]}"

@mcp.tool()
def wt_diff() -> str:
    """The worktree's changes made by generators, new files included, as a git patch for `git apply` in the cloud clone."""
    sh(["git", "-C", WT, "add", "-A", "-N"])
    return sh(["git", "-C", WT, "diff", "--binary"])

class BearerAuth:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            got = dict(scope["headers"]).get(b"authorization", b"").decode()
            if not hmac.compare_digest(got, f"Bearer {TOKEN}"):
                await send({"type": "http.response.start", "status": 401, "headers": [(b"content-type", b"text/plain")]})
                await send({"type": "http.response.body", "body": b"unauthorized"})
                return
        await self.app(scope, receive, send)


if __name__ == "__main__":
    log(f"bridge up on 127.0.0.1:{PORT}")
    uvicorn.run(BearerAuth(mcp.streamable_http_app()), host="127.0.0.1", port=PORT, log_level="warning")
