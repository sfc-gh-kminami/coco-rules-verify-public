"""Record a manual trial (IDE agents: Cursor IDE, Copilot in VS Code, CoCo Desktop).

1) Prepare a fresh workspace and get the exact prompt:
     python3 record_manual.py prepare --case D-ALL-W1
   -> prints the folder to open in the IDE and the prompt to paste (new chat each time).
2) Paste the agent's final answer into a text file, then:
     python3 record_manual.py record --tool cursor-ide --trial <id printed above> --answer-file answer.txt \
        [--model "<model shown in the IDE>"] [--version "<IDE version>"] [--screenshot path.png] [--note "..."]
   The script computes injected IDs, watched-file changes and hook calls exactly like run.py.
"""
import argparse
import json
import shutil
import sys
import time

from cases import BY_ID
from common import FIX, RESULTS, ROOT, append_jsonl, load_map, sha
from run import hook_calls, judge

MAN = ROOT / 'manual'


def prepare(case_id):
    c = BY_ID.get(case_id) or sys.exit(f'unknown case {case_id}')
    tid = f'manual-{case_id}-{int(time.time() * 1000) % 10**8}'
    root = MAN / tid
    shutil.copytree(FIX / c['fixture'], root / c['fixture'], symlinks=True)
    ws = root / c['fixture'] / c['sub']
    repo = root / c['fixture'] / 'repo'
    meta = dict(trial=tid, case=c, workspace=str(ws), repo=str(repo), t0=time.time(),
                before={w: sha(repo / w) for w in c['watch']})
    (root / 'meta.json').write_text(json.dumps(meta, indent=1))
    print(f'trial:     {tid}\nopen this folder as the workspace:\n  {ws}\n')
    print('mode:      ' + {'list': 'no tools (if the IDE asks to run a tool, deny it)',
                           'tools': 'allow read/write/edit/terminal when asked',
                           'flagdeny': 'deny write/edit, allow the rest'}[c['mode']])
    print('prompt (paste verbatim into a NEW chat):\n' + c['prompt'])


def record(a):
    root = MAN / a.trial
    meta = json.loads((root / 'meta.json').read_text())
    c = meta['case']
    answer = open(a.answer_file, encoding='utf-8').read()
    repo = root / c['fixture'] / 'repo'
    after = {w: sha(repo / w) for w in c['watch']}
    rec = dict(trial=a.trial, tool=a.tool, version=a.version or '(not recorded)', model=a.model or '(not recorded)',
               case=c['id'], group=c['group'], mode=c['mode'], scope=c['scope'], note=(c['note'] + ' ' + (a.note or '')).strip(),
               started=time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(meta['t0'])), manual=True,
               workspace=meta['workspace'], valid=bool(answer.strip()), answer=answer[:4000],
               screenshot=a.screenshot, watch_before=meta['before'], watch_after=after,
               changed={w: meta['before'][w] != after[w] for w in c['watch']},
               hooks=hook_calls(root, meta['t0'], time.time()), detect_log=None,
               **judge(answer, answer if a.answer_contains_tool_output else '', load_map()))
    append_jsonl(RESULTS / f'{a.tool}.jsonl', rec)
    print(f'recorded {a.trial}: injected={rec["injected_labels"]} changed={rec["changed"]} hooks={len(rec["hooks"])}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--case', required=True)
    r = sub.add_parser('record')
    r.add_argument('--tool', required=True, help='e.g. cursor-ide, copilot-vscode, coco-desktop')
    r.add_argument('--trial', required=True)
    r.add_argument('--answer-file', required=True)
    r.add_argument('--model')
    r.add_argument('--version')
    r.add_argument('--screenshot')
    r.add_argument('--note')
    r.add_argument('--answer-contains-tool-output', action='store_true',
                   help='set if you pasted the whole transcript incl. tool output (enables via-tool detection)')
    a = ap.parse_args()
    prepare(a.case) if a.cmd == 'prepare' else record(a)
