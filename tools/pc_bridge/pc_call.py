"""Мост vic3-pc по HTTP без MCP-клиента сессии (облако, когда инструменты mcp__vic3-pc__* не подключились).

    python3 tools/pc_bridge/pc_call.py list
    python3 tools/pc_bridge/pc_call.py call <инструмент> '<аргументы JSON>'

Адрес — из .mcp.json, токен — переменная окружения PC_BRIDGE_TOKEN. Таймаут вызова — PC_TIMEOUT (с, по умолчанию 900).
"""
import json,os,sys,urllib.request
URL="https://untimed-diploma-creation.ngrok-free.dev/mcp"
H={"Authorization":"Bearer "+os.environ["PC_BRIDGE_TOKEN"],"Accept":"application/json, text/event-stream","Content-Type":"application/json"}
def post(body,sid=None,timeout=900):
    h=dict(H)
    if sid: h["Mcp-Session-Id"]=sid
    r=urllib.request.urlopen(urllib.request.Request(URL,json.dumps(body).encode(),h),timeout=timeout)
    sid2=r.headers.get("Mcp-Session-Id"); raw=r.read().decode('utf-8','replace')
    msgs=[]
    if raw.lstrip().startswith('{'): msgs=[json.loads(raw)] if raw.strip() else []
    else:
        for line in raw.splitlines():
            if line.startswith('data:'):
                d=line[5:].strip()
                if d: msgs.append(json.loads(d))
    return sid2,msgs
def session():
    sid,_=post({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"cloud","version":"1"}}})
    try: post({"jsonrpc":"2.0","method":"notifications/initialized"},sid)
    except Exception: pass
    return sid
sid=session()
if sys.argv[1]=='list':
    _,m=post({"jsonrpc":"2.0","id":2,"method":"tools/list"},sid)
    for t in m[-1]['result']['tools']:
        print('-',t['name'],':',t.get('description','').split('\n')[0][:150]); print('   args:',list(t['inputSchema'].get('properties',{}).keys()))
else:
    args=json.loads(sys.argv[3]) if len(sys.argv)>3 else {}
    _,m=post({"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":sys.argv[2],"arguments":args}},sid,timeout=int(os.environ.get('PC_TIMEOUT','900')))
    res=m[-1]
    if 'error' in res: print('ERROR',res['error']); sys.exit(1)
    for c in res['result'].get('content',[]):
        print(c.get('text',c))
