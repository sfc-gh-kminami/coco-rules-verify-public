import sys; sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from harness import *
from concurrent.futures import ThreadPoolExecutor
HOME = os.path.expanduser('~'); V = '/tmp/coco-verify-local'; B = '/tmp/coco-backup-local'
targets = ['.snowflake/cortex/AGENTS.md', 'AGENTS.md', 'CLAUDE.md', '.claude/CLAUDE.md', '.claude/rules', '.cursor/rules',
           '.claude/settings.json', '.snowflake/cortex/settings.json', '.snowflake/cortex/hooks.json']
rep = []
os.makedirs(B, exist_ok=True)
def tree_hash(p):
    if os.path.isdir(p):
        return {os.path.relpath(os.path.join(r, f), p): sha(os.path.join(r, f)) for r, _, fs in os.walk(p) for f in fs}
    return sha(p)
pre = {}
for t in targets:
    p = f'{HOME}/{t}'
    if os.path.exists(p):
        pre[t] = tree_hash(p); dst = f'{B}/{t}'; os.makedirs(os.path.dirname(dst), exist_ok=True)
        (shutil.copytree if os.path.isdir(p) else shutil.copy2)(p, dst)
    else: pre[t] = None
created = []
try:
    def U(rel, **k):
        p = f'{HOME}/{rel}'; existed = os.path.exists(p)
        if existed: os.remove(p)
        created.append(rel); return wfile(p, **k)
    U('.snowflake/cortex/AGENTS.md', label='U1', rule='Always answer in Japanese.')
    U('AGENTS.md', label='U2'); U('CLAUDE.md', label='U3'); U('.claude/CLAUDE.md', label='U4')
    U('.claude/rules/u.md', label='U5', fm={'description': '"u"'}); U('.cursor/rules/u.mdc', label='U6', fm={'description': '"u"'})
    d = f'{V}/user-ws'; git(d); wfile(f'{d}/AGENTS.md', label='W1', rule='Always answer in English.'); wfile(f'{d}/CLAUDE.md', label='W2')
    c = f'{V}/user-ctrl'; git(c); open(f'{c}/readme.txt', 'w').write('no instructions\n')
    # TC-24 user setting
    st = f'{HOME}/.snowflake/cortex/settings.json'
    orig = json.load(open(st)) if os.path.exists(st) else {}
    t24 = f'{V}/user-team'; git(t24); wfile(f'{t24}/TEAM.md', label='TC24-user-TEAM')
    jobs = [('TC-12/13-user', d, P_LIST)] * 5 + [('TC-12-order', d, P_ORDER)] * 3 + [('TC-11', d, P_HELLO)] * 5 + [('TC-user-ctrl', c, P_LIST)] * 3 + [('TC-11-ctrl', c, P_HELLO)] * 5
    with ThreadPoolExecutor(3) as ex:  # parallel within phase: ~ is static during these runs
        for r in ex.map(lambda j: run(*j), jobs): print(r['id'], r['ids_injected_paths'], r['answer'][:80].replace('\n', ' '), flush=True)
    # local: do not modify the user's real settings.json
    for _ in range(0): r = run('TC-24-user', t24, P_LIST); print(r['id'], r['ids_injected_paths'], flush=True)
finally:
    for rel in created:
        try: os.remove(f'{HOME}/{rel}')
        except FileNotFoundError: pass
    for t in targets:
        p = f'{HOME}/{t}'
        if pre[t] is None:
            if os.path.isdir(p) and not os.listdir(p): os.rmdir(p)
            elif os.path.isfile(p) and t.endswith('settings.json') and t in ('.snowflake/cortex/settings.json',): pass
        else:
            if os.path.isdir(p): shutil.rmtree(p)
            elif os.path.exists(p): os.remove(p)
            (shutil.copytree if os.path.isdir(f'{B}/{t}') else shutil.copy2)(f'{B}/{t}', p)
    if pre['.snowflake/cortex/settings.json'] is None and os.path.exists(f'{HOME}/.snowflake/cortex/settings.json'):
        os.remove(f'{HOME}/.snowflake/cortex/settings.json')
    post = {t: (tree_hash(f'{HOME}/{t}') if os.path.exists(f'{HOME}/{t}') else None) for t in targets}
    json.dump({'pre': pre, 'post': post, 'match': pre == post}, open(f'{OUT}/backup_restore.json', 'w'), indent=1)
    print('restore match', pre == post)
