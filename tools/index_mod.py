import os,sys,json,re
KEY_RE=re.compile(r"^\s*([A-Za-z0-9_.\-:]+)\s*=")
LOC_RE=re.compile(r'^\s*([^\s:#][^:#]*?)\s*:\s*[0-9]*\s*"')
EVT_RE=re.compile(r"\bid\s*=\s*([A-Za-z0-9_.\-]+)")
SCRIPT_EXT={'.txt','.yml','.gui','.asset','.info'}
NON_DEF={'if','else','else_if','elseif','while','limit','modifier','add','remove','set','trigger','effect','value','desc','picture','option'}

def strip(l): return l.split('#',1)[0]

def index(root):
    root=os.path.abspath(root)
    files=[]; keys={}; loc={}; events={}; gui={}
    for dp,dns,fns in os.walk(root):
        dns[:]=[d for d in dns if d not in ('.git',)]
        for fn in fns:
            full=os.path.join(dp,fn)
            rel=os.path.relpath(full,root).replace('\\','/')
            files.append(rel)
            ext=os.path.splitext(fn)[1].lower()
            if ext not in SCRIPT_EXT: continue
            try:
                txt=open(full,encoding='utf-8-sig',errors='ignore').read()
            except Exception: continue
            if rel.startswith('localization/'):
                for line in txt.splitlines():
                    m=LOC_RE.match(line)
                    if m:
                        k=m.group(1).strip()
                        if k.startswith('l_'): continue
                        loc.setdefault(k,[]).append(rel)
                continue
            if rel.startswith('gui/'):
                for m in re.finditer(r'\bname\s*=\s*"([^"]+)"',txt):
                    gui.setdefault(m.group(1),[]).append(rel)
                continue
            if rel.startswith('events/'):
                for m in EVT_RE.finditer(txt):
                    events.setdefault(m.group(1),[]).append(rel)
            depth=0
            for raw in txt.splitlines():
                line=strip(raw)
                if depth==0:
                    m=KEY_RE.match(line)
                    if m:
                        tok=m.group(1)
                        if ':' in tok:
                            p,r=tok.split(':',1)
                            if p.isupper(): tok=r
                        if tok not in NON_DEF:
                            cat=os.path.dirname(rel)
                            keys.setdefault(cat+'|'+tok,[]).append(rel)
                depth+=line.count('{')-line.count('}')
    return {'root':root,'files':files,'keys':keys,'loc':loc,'events':events,'gui':gui}

if __name__=='__main__':
    src=sys.argv[1]; out=sys.argv[2]
    d=index(src)
    tmp=out+'.tmp'
    with open(tmp,'w',encoding='utf-8') as f: json.dump(d,f)
    os.replace(tmp,out)
    print(f"{src}: files={len(d['files'])} keys={len(d['keys'])} loc={len(d['loc'])} events={len(d['events'])} gui={len(d['gui'])}")
