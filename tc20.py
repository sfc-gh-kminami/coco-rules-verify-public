import sys, uuid; sys.path.insert(0, '/workspace/coco-rules-verify')
from harness import *
V = '/tmp/coco-verify'
for k in range(2):
    src = f'{V}/full'; dst = f'{V}/full_tc20_{k}'
    if not os.path.exists(dst): shutil.copytree(src, dst, symlinks=True)
    R = f'{dst}/repo'; sid = str(uuid.uuid4())
    turns = [(P_HELLO, None), ('Edit queries/sample.sql to append the line -- edited at the end using the edit tool.', 'read,edit'),
             (P_LIST, None), (P_HELLO, None), (P_HELLO, None), (P_HELLO, None), (P_LIST, None)]
    for t, (p, al) in enumerate(turns, 1):
        base = ['cortex', '--output-format', 'stream-json', '-m', 'claude-opus-5-5', '--max-turns', '6', '-w', R]
        base += ['--session-id', sid] if t == 1 else ['-r', sid]
        if al: base += ['--allowed-tools', al]
        base += ['-p']
        r = run(f'TC-20-s{k}-t{t}', R, p, extra={'cmd': base}, retry=False, timeout=300, watch=('queries/sample.sql',))
        print(t, r['session_id'], r['rc'], r['ids_injected_paths'], r['tags'], r['changed'], r['answer'][:150].replace('\n', ' '), r['stderr_tail'][-200:], flush=True)
        if t == 1 and not r['session_id']: print('no session; abort'); break
