import sys, glob; sys.path.insert(0, '/workspace/coco-rules-verify')
from harness import *
MAP.update(json.load(open(MAPF)))
known = MAP['ids']
recs = []
for f in sorted(glob.glob(f'{OUT}/logs/*.jsonl')):
    tid = os.path.basename(f)[:-6]
    rf = f'{OUT}/logs/{tid}.rec.json'
    if os.path.exists(rf): recs.append(json.load(open(rf))); continue
    raw = open(f).read(); out, _, logpart = raw.partition('\n#LOG\n')
    case = re.sub(r'-\d+-\d+$', '', tid)
    sid = None; ws = None; texts = []; tools = []; tres = []; final = ''; mu = {}; denials = []
    for ln in out.splitlines():
        try: j = json.loads(ln)
        except Exception: continue
        sid = sid or j.get('session_id'); ws = ws or j.get('cwd')
        if j.get('type') == 'assistant':
            for c in j['message'].get('content', []):
                if c.get('type') == 'text': texts.append(c['text'])
                if c.get('type') == 'tool_use': tools.append({'name': c.get('name'), 'input': c.get('input')})
        if j.get('type') == 'user':
            cs = j.get('message', {}).get('content', [])
            if isinstance(cs, list):
                for c in cs:
                    if isinstance(c, dict) and c.get('type') == 'tool_result':
                        cc = c.get('content'); tres.append(cc if isinstance(cc, str) else json.dumps(cc))
        if j.get('type') == 'result':
            final = j.get('result') or ''; mu = j.get('modelUsage', {}); denials = j.get('permission_denials', [])
    loglines = logpart.splitlines()
    ans = final or '\n'.join(texts); tooltxt = '\n'.join(tres)
    toks = set(TOK.findall(ans)) - {'ZZNONE00000X'}
    inj = sorted(t for t in toks if t in known and t not in tooltxt)
    fab = [t for t in toks if t not in known and re.search(r'[A-Z]', t) and re.search(r'\d', t)]
    changed = {}
    if ws and '/enf-' in ws:
        s = open(f'{ws}/secret.txt').read() if os.path.exists(f'{ws}/secret.txt') else None
        changed['secret.txt'] = s != 'ORIGINAL dummy secret\n'
        if 'tc28' in ws: changed['out.txt'] = os.path.exists(f'{ws}/out.txt')
    if ws and 'full_tc21' in ws: changed['src/api/handler.ts'] = '// touched' in open(f'{ws}/src/api/handler.ts').read()
    recs.append(dict(id=tid, case=case, ws=ws, session_id=sid, model_usage=list(mu.keys()), answer=ans[:3000],
        ids_injected=inj, ids_injected_paths=[known[i]['path'] + ('#FM' if known[i]['kind'] == 'frontmatter' else '') for i in inj],
        ids_via_tool=sorted(t for t in toks if t in known and t in tooltxt), tool_result_has_system_reminder=any('system-reminder' in x for x in tres),
        fabricated=fab, tags=sorted(set(re.findall(r'TAG-([A-Z0-9]{6})', ans))), tool_calls=tools, tool_results=[x[:500] for x in tres],
        denials=denials, detect_log=[l for l in loglines if 'nstruction' in l or 'cursor' in l.lower()][:40], hook_log=[l for l in loglines if 'hook' in l.lower()][:20],
        changed=changed, rebuilt_from_log=True))
with open('/tmp/all.jsonl', 'w') as o:
    for r in recs: o.write(json.dumps(r, ensure_ascii=False) + '\n')
shutil.copy('/tmp/all.jsonl', f'{OUT}/results.jsonl')
print(len(recs))
