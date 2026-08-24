import os,re,sys
P=os.path.expanduser('~/mnt/Projects')
F=P+'/vic3_mods_out/for addon'; G=P+'/vic3_mods_out/grey_add_alot_of_things'
MODS=[('vanilla',P+'/vic3_mods_out/.vanillaVIC3'),('CMF',P+'/vic3_mods_out/_cmf'),('ETF',P+'/vic3_mods_out/_etf'),
 ('TGR',P+'/vic3_mods_out/TheGreatRevision'),('PSC',P+'/vic3_mods_out/PSC'),('KAI',P+'/vic3_mods_out/TechRes+Kuromi/kai'),
 ('EF',P+'/vic3_mods_out/E&F'),('EFHOTFIX',P+'/vic3_mods/_ef/ef hotfix 1.13'),('MORG',P+'/vic3_mods_out/Morgenrote'),
 ('TR',P+'/vic3_mods_out/TechRes+Kuromi/t&r'),('PBE',P+'/vic3_mods_out/PowerBlocksExpanded'),
 ('MEGAPACK',P+'/vic3_mods/__megapacks/megapack'),
 ('multiline',G+'/_multiline'),('llwa',P+'/vic3_mods_out/llwa'),('usu',G+'/grey_usu'),('llwa_morg',G+'/llwa_morgen compatch'),
 ('usu_llwa',G+'/usu_llwa comatch'),('softecon',G+'/_grey_soft_econ'),('food',G+'/grey_food'),('ranch',G+'/grey_food_2_ranch'),
 ('diplo',F+'/grey_diplo'),('subject',F+'/grey_subject'),('gob',F+'/gatesofbosphorus'),('hail',F+'/hailcolumbia'),('moh',F+'/mandateofheaven')]
KEY=re.compile(r"^\s*([A-Za-z0-9_.\-:]+)\s*=")
def vfs(cat):
    m={}
    for name,root in MODS:
        d=os.path.join(root,cat)
        if not os.path.isdir(d): continue
        for dp,dns,fns in os.walk(d):
            for fn in fns:
                if not fn.endswith('.txt'): continue
                rel=os.path.relpath(os.path.join(dp,fn),os.path.join(root,cat)).replace('\\','/')
                m[rel]=(name,os.path.join(dp,fn))
    return dict(sorted(m.items(),key=lambda kv:kv[0].encode()))
def parse(path):
    lines=open(path,encoding='utf-8-sig',errors='ignore').read().replace('\r\n','\n').split('\n')
    out=[];depth=0
    for i,raw in enumerate(lines):
        line=raw.split('#',1)[0]
        if depth==0:
            mm=KEY.match(line)
            if mm:
                tok=mm.group(1);pref=''
                if ':' in tok:
                    p,r=tok.split(':',1)
                    if p.isupper(): pref,tok=p,r
                d=0;st=False;j=i;sub=[]
                while j<len(lines):
                    l=lines[j].split('#',1)[0]
                    if d==1:
                        m2=KEY.match(l)
                        if m2: sub.append(m2.group(1))
                    d+=l.count('{')-l.count('}')
                    if '{' in l: st=True
                    if st and d<=0: break
                    j+=1
                out.append((tok,pref,sub,j-i+1))
        depth+=line.count('{')-line.count('}')
    return out
cat=sys.argv[1];keys=set(sys.argv[2:])
files=vfs(cat); res={k:[] for k in keys}
for rel,(mod,full) in files.items():
    for tok,pref,sub,n in parse(full):
        if tok in keys: res[tok].append((rel,mod,pref,sub,n))
for k in sys.argv[2:]:
    print('='*70); print(cat+'/'+k)
    for rel,mod,pref,sub,n in res[k]:
        print(f'  {rel:52} [{mod:9}] {pref or "(bare)":18} {n:4}L sub={sub[:12]}')
