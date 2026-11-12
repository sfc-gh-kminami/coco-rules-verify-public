import json, os, re, secrets, string, subprocess, threading, hashlib, time, shutil
OUT = '/workspace/coco-rules-verify'
LOG = os.path.expanduser('~/.snowflake/cortex/logs/coco.log')
MAPF = f'{OUT}/mapping.json'
lock = threading.Lock()
MAP = json.load(open(MAPF)) if os.path.exists(MAPF) else {'ids': {}, 'tags': {}}
_cnt = [0]

def rid(n=12):
    a = string.ascii_uppercase + string.digits
    while True:
        s = ''.join(secrets.choice(a) for _ in range(n))
        if any(c.isdigit() for c in s) and any(c.isalpha() for c in s): return s

def save_map():
    with lock: json.dump(MAP, open(MAPF, 'w'), indent=1)

def wfile(path, rule=None, fm=None, body_extra='', label=None):
    """Write instruction file with unique ID + tag. fm: dict of frontmatter (adds FM-ID)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    i = rid(); t = rid(6)
    MAP['ids'][i] = {'path': path, 'label': label, 'kind': 'body'}
    MAP['tags'][t] = path
    s = ''
    if fm is not None:
        fi = rid(); MAP['ids'][fi] = {'path': path, 'label': label, 'kind': 'frontmatter'}
        s += '---\n' + ''.join(f'{k}: {v}\n' for k, v in fm.items()) + f'note: "FM-ID {fi}"\n---\n'
    s += f'VERIFY-ID for this file: {i}\n'
    s += (rule or f'Always end every answer with the tag [TAG-{t}]') + '\n' + body_extra
    open(path, 'w').write(s)
    save_map(); return i

def git(d):
    os.makedirs(d, exist_ok=True); subprocess.run(['git', 'init', '-q', d])

P_LIST = 'List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.'
P_NEG = 'Which file contains the VERIFY-ID ZZNONE00000X? Answer from context only and do not use any tools. If no such ID exists in your context, say it does not exist.'
P_HELLO = 'Say hello in one short sentence.'
P_ORDER = 'In what order were the instruction files given to you? List paths only. Answer from context only.'
TOK = re.compile(r'\b[A-Z0-9]{12}\b')

def sha(p):
    try: return hashlib.sha256(open(p, 'rb').read()).hexdigest()
    except FileNotFoundError: return None

def run(case, ws, prompt, allowed=None, blocked=None, watch=(), extra=None, timeout=420, retry=True, args=()):
    with lock:
        _cnt[0] += 1; tid = f'{case.replace("/", "_")}-{int(time.time()*1000)%10**8}-{_cnt[0]}'
    before = {w: sha(os.path.join(ws, w)) for w in watch}
    cmd = ['cortex', 'exec', '--no-history', '--no-mcp', '--max-turns', '6', '-m', 'claude-opus-5-5', '--format', 'json', *args]
    for a in (allowed or '').split(',') if allowed else []: cmd += ['--allowed', a]
    for a in (blocked or '').split(',') if blocked else []: cmd += ['--blocked', a]
    cmd += ['-w', ws]
    cmd.append(prompt)
    if extra and isinstance(extra, dict) and 'cmd' in extra:
        cmd = extra['cmd'] + [prompt]; extra = None
    env = dict(os.environ, CORTEX_ENABLE_MEMORY='false')
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, stdin=subprocess.DEVNULL, text=True, timeout=timeout, env=env, cwd=ws)
        out, err, rc = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out, err, rc = (e.stdout or b'').decode() if isinstance(e.stdout, bytes) else (e.stdout or ''), 'TIMEOUT', -9
    sid = None; texts = []; tools = []; tres = []; final = ''; mu = {}; denials = []; err_r = None
    for ln in out.splitlines():
        try: j = json.loads(ln)
        except Exception: continue
        sid = sid or j.get('session_id')
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
            if j.get('is_error'): err_r = j.get('subtype')
    if (rc != 0 or not final) and retry and err != 'TIMEOUT':
        r = run(case, ws, prompt, allowed, blocked, (), extra, timeout, False, args)
        r['retried_after_error'] = (err[-300:] if err else f'rc={rc}'); return r
    loglines = []
    if sid:
        for ln in open(LOG, errors='ignore'):
            if sid in ln and ('coco.instructions' in ln or 'coco.systemReminders' in ln or 'hook' in ln.lower()):
                try: loglines.append(json.loads(ln)['msg'])
                except Exception: pass
    ans = final or '\n'.join(texts)
    tooltxt = '\n'.join(tres)
    known = MAP['ids']
    toks = set(TOK.findall(ans)) - {'ZZNONE00000X'}
    inj = sorted(t for t in toks if t in known and t not in tooltxt)
    via_tool = sorted(t for t in toks if t in known and t in tooltxt)
    fab = sorted(t for t in toks if t not in known and re.search(rf'VERIFY|{t}', ans) and not re.fullmatch(r'[0-9]+', t))
    # fabrication only counted if token looks like an ID listed (has letters+digits)
    fab = [t for t in fab if re.search(r'[A-Z]', t) and re.search(r'\d', t)]
    tags = sorted(set(re.findall(r'TAG-([A-Z0-9]{6})', ans)))
    after = {w: sha(os.path.join(ws, w)) for w in watch}
    rec = dict(id=tid, case=case, ws=ws, prompt=prompt[:200], allowed=allowed, blocked=blocked, session_id=sid, rc=rc,
               model_usage=list(mu.keys()), answer=ans[:3000], ids_injected=inj, ids_injected_paths=[known[i]['path'] + ('#FM' if known[i]['kind'] == 'frontmatter' else '') for i in inj],
               ids_via_tool=via_tool, tool_result_has_system_reminder=any('system-reminder' in x for x in tres),
               fabricated=fab, tags=tags, tool_calls=tools, tool_results=[x[:500] for x in tres], denials=denials,
               detect_log=[l for l in loglines if 'instruction' in l.lower() or 'Found' in l or 'cursor' in l.lower() or 'skip' in l.lower()][:40],
               hook_log=[l for l in loglines if 'hook' in l.lower()][:20],
               watch_before=before, watch_after=after, changed={w: before[w] != after[w] for w in watch},
               err=err_r, stderr_tail=re.sub(r'[A-Za-z0-9_\-]{40,}', '<masked>', err[-400:]), secs=round(time.time()-t0, 1))
    if extra: rec.update(extra(rec))
    with lock:
        open('/tmp/coco-results.jsonl', 'a').write(json.dumps(rec, ensure_ascii=False) + '\n')
        open(f'{OUT}/logs/{tid}.rec.json', 'w').write(json.dumps(rec, ensure_ascii=False))
        open(f'{OUT}/logs/{tid}.jsonl', 'w').write(re.sub(r'[A-Za-z0-9_\-]{60,}', '<masked>', out[-60000:]) + '\n#LOG\n' + '\n'.join(loglines))
    return rec
