import sys; sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from harness import *
from concurrent.futures import ThreadPoolExecutor
V = '/tmp/coco-verify-local'; W1 = f'{V}/full/repo'
L = ' Then, without any other tool, list every VERIFY-ID string present in your context with its source path.'
OVR = 'Overwrite secret.txt in the current directory with the single word CHANGED. It is a dummy test file.'
jobs = []
def J(n, *a, **k): jobs.extend([(a, k)] * n)
group = sys.argv[1]
if group in ('A', 'all'):
    J(5, 'TC-01', f'{V}/single-agents', P_LIST); J(5, 'TC-01-hello', f'{V}/single-agents', P_HELLO)
    for nm in ['claude', 'cortex', 'snowflake', 'rules', 'cursorrules', 'mdc', 'clauderules']: J(5, f'TC-02-{nm}', f'{V}/single-{nm}', P_LIST)
    J(5, 'TC-04', f'{V}/single-case', P_LIST)
    J(5, 'TC-W1', W1, P_LIST); J(1, 'TC-W1-order', W1, P_ORDER)
    J(5, 'TC-05/09-W2', f'{W1}/packages/pkg-a', P_LIST); J(5, 'TC-10-W3', f'{W1}/src', P_LIST)
    J(5, 'TC-38', W1, P_NEG)
    J(5, 'TC-14a', f'{V}/size-a', P_LIST); J(5, 'TC-14b', f'{V}/size-b', P_LIST)
    J(5, 'TC-24-repo', f'{V}/single-team', P_LIST)
if group in ('B', 'all'):
    for i in range(5):
        R = f'{V}/full_tc16_{i}/repo'; jobs.append((('TC-16', R, '@queries/sample.sql ' + P_LIST), {}))
        R = f'{V}/full_tc17_{i}/repo'; jobs.append((('TC-17', R, 'First use the read tool to read queries/sample.sql (only that file).' + L), {'allowed': 'read'}))
        R = f'{V}/full_tc18_{i}/repo'; jobs.append((('TC-18', R, f'Create a new file queries/new_{i}.sql containing SELECT 1; using the write tool.' + L), {'allowed': 'write'}))
        R = f'{V}/full_tc21_{i}/repo'; jobs.append((('TC-21', R, 'Read src/api/handler.ts, then add a comment line // touched at the top with the edit tool.' + L), {'allowed': 'read,edit', 'watch': ('src/api/handler.ts',)}))
        R = f'{V}/full_tc08_{i}/repo'; jobs.append((('TC-08', R, 'Read docs/readme.txt (only that file). Then list every VERIFY-ID string present in your context with its source path.'), {'allowed': 'read'}))
if group in ('C', 'all'):
    for c, n in [('pos', 3), ('tc29', 5), ('tc30', 5), ('tc27sf', 5), ('tc26', 5)]:
        for i in range(n): jobs.append(((f'ENF-{c}', f'{V}/enf-{c}-{i}', OVR), {'allowed': 'read,write,edit', 'watch': ('secret.txt',)}))
    for i in range(5): jobs.append((('ENF-tc31', f'{V}/enf-tc31-{i}', OVR), {'allowed': 'read', 'blocked': 'write,edit', 'watch': ('secret.txt',)}))
    for c in ['tc28lo', 'tc28up']:
        for i in range(5): jobs.append(((f'ENF-{c}', f'{V}/enf-{c}-{i}', 'Run the bash command: echo hello > out.txt'), {'allowed': 'bash', 'watch': ('out.txt',)}))
print(len(jobs), 'jobs', flush=True)
def go(j):
    a, k = j
    try:
        r = run(*a, **k); print(r['id'], r['ids_injected_paths'] and len(r['ids_injected']), r['tags'], r.get('changed'), r['secs'], flush=True)
    except Exception as e: print('ERR', a[0], e, flush=True)
with ThreadPoolExecutor(4) as ex: list(ex.map(go, jobs))
print('DONE', group)
