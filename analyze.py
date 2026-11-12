import json, collections, os, re
OUT = '/workspace/coco-rules-verify'
M = json.load(open(f'{OUT}/mapping.json'))
recs = [json.loads(l) for l in open('/tmp/all.jsonl')]
by = collections.defaultdict(list)
for r in recs: by[r['case']].append(r)
lab = lambda p: next((v['label'] + ('#FM' if v['kind'] == 'frontmatter' else '') for k, v in M['ids'].items() if v['path'] == p.replace('#FM', '') and (v['kind'] == 'frontmatter') == p.endswith('#FM')), p)
def short(p): return re.sub(r'/tmp/coco-verify/[^/]+/', '', p)
for c in sorted(by):
    rs = by[c]; print(f'== {c} N={len(rs)}')
    for r in rs:
        loads = [l for l in r['detect_log'] if l.startswith('Loading') or l.startswith('Found') or 'skip' in l.lower() or 'Skip' in l or 'large' in l.lower() or 'exceed' in l.lower()]
        print('  ', r['id'][-12:], 'inj=', [short(p) for p in r['ids_injected_paths']], 'via_tool=', len(r.get('ids_via_tool', [])), 'fab=', r['fabricated'], 'tags=', len(r['tags']),
              'tools=', [t['name'] for t in r['tool_calls']], 'chg=', r.get('changed'), 'model=', r['model_usage'])
        for l in loads: print('      LOG:', short(l)[:400])
        if r['hook_log']: print('      HOOK:', r['hook_log'][:3])
        if c.startswith(('TC-11', 'TC-38', 'TC-01-hello', 'ENF', 'TC-24', 'TC-12-order', 'TC-W1-order', 'TC-14')) or 'TC-20' in c:
            print('      ANS:', r['answer'][:300].replace('\n', ' | '))
        if c.startswith('ENF'):
            for t in r['tool_calls']: print('      CALL:', t['name'], json.dumps(t['input'])[:150])
            for t in r['tool_results']: print('      RES:', t[:200].replace('\n', ' '))
