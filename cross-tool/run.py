"""Run cases against one CLI tool and append one JSON record per trial.

  python3 run.py --tool cortex --list
  python3 run.py --tool claude                       # all project-scope cases
  python3 run.py --tool codex --cases 'D-*,E-*' --n 1 --parallel 2
  python3 run.py --tool copilot --cases U-ALL        # user-scope cases need: user_scope.py apply

Results: $XTOOL_ROOT/results/<tool>.jsonl  (+ raw output per trial under results/raw/<trial>/)
"""
import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from adapters import ADAPTERS
from cases import CASES
from common import (FIX, HOOKS, INVLOG, RESULTS, ROOT, append_jsonl, extract_block_messages, extract_tool_calls,
                    load_map, sha)
from user_scope import MANIFEST

RUNS = ROOT / 'runs'
TOK = re.compile(r'\b[A-Z0-9]{12}\b')
CANDIDATE_NAMES = ['AGENTS.md', 'AGENTS.override.md', 'CLAUDE.md', 'CLAUDE.local.md', 'CORTEX.md', 'SNOWFLAKE.md',
                   'RULES.md', 'GEMINI.md', '.cursorrules', '.mdc', '.claude/rules', 'copilot-instructions.md',
                   '.instructions.md', 'settings.json', 'settings.local.json', 'hooks.json', 'config.toml', 'cli.json']


def judge(answer, raw, mapping):
    """Classify IDs. 'injected' = in the answer and never shown as file content in the raw stream."""
    ids = mapping['ids']
    answer = answer or ''
    toks = set(TOK.findall(answer)) - {'ZZNONE00000X'}
    shown = {i for i in ids if f'VERIFY-ID for this file: {i}' in raw or f'VERIFY-ID (end of file): {i}' in raw
             or f'FM-ID {i}' in raw}
    known = sorted(t for t in toks if t in ids)
    injected = [t for t in known if t not in shown]
    fabricated = sorted(t for t in toks if t not in ids and re.search(r'[A-Z]', t) and re.search(r'\d', t))
    return dict(
        ids_in_answer=known,
        injected=injected,
        injected_labels=[ids[t]['label'] + ('#frontmatter' if ids[t]['kind'] == 'frontmatter' else '') for t in injected],
        via_tool_output=sorted(t for t in known if t in shown),
        ids_shown_as_file_content=sorted(shown),
        fabricated=fabricated,
        tags=sorted(set(re.findall(r'TAG-([A-Z0-9]{6})', answer))),
        japanese=bool(re.search(r'[\u3040-\u30ff\u4e00-\u9fff]', answer)),
    )


def variants(root):
    s = str(root)
    return {s, s.replace('/private/tmp/', '/tmp/', 1), s.replace('/private/var/', '/var/', 1)}


def hook_calls(root, t0, t1):
    out = []
    roots = variants(root)
    if not INVLOG.exists():
        return out
    for ln in INVLOG.read_text(errors='ignore').splitlines():
        try:
            j = json.loads(ln)
        except Exception:
            continue
        cwd = str(j.get('stdin_cwd') or '') + '|' + str(j.get('proc_cwd') or '')
        if t0 - 1 <= j.get('ts', 0) <= t1 + 1 and any(r in cwd for r in roots):
            out.append({k: j.get(k) for k in ('source', 'mode', 'event', 'tool_name', 'stdin_keys')})
    return out


def detect_evidence(log_dir, root):
    """Which candidate files are mentioned in the tool's own log (best-effort 'detection' signal)."""
    if not log_dir or not Path(log_dir).exists():
        return None
    text = ''
    for p in Path(log_dir).rglob('*'):
        if p.is_file() and p.stat().st_size < 50_000_000:
            text += p.read_text(errors='ignore')
    hits = set()
    for r in variants(root):
        for m in re.finditer(re.escape(r) + r'[^\s"\'\]\),]*', text):
            rel = m.group(0)[len(r):].lstrip('/')
            if any(n in rel for n in CANDIDATE_NAMES):
                hits.add(rel)
    return sorted(hits)


def version(adapter):
    try:
        p = subprocess.run(adapter.version_cmd(), capture_output=True, text=True, timeout=60)
        return (p.stdout or p.stderr).strip().splitlines()[0] if (p.stdout or p.stderr).strip() else f'rc={p.returncode}'
    except Exception as e:
        return f'unavailable: {e}'


def run_trial(adapter, case, k, ver, mapping):
    tid = f'{adapter.name}-{case["id"]}-{k}-{int(time.time() * 1000) % 10**8}'
    tdir = RESULTS / 'raw' / tid
    tdir.mkdir(parents=True, exist_ok=True)
    root = RUNS / tid
    shutil.copytree(FIX / case['fixture'], root / case['fixture'], symlinks=True)
    ws = (root / case['fixture'] / case['sub']).resolve()
    repo = (root / case['fixture'] / 'repo').resolve()
    spec = adapter.build(case['mode'], ws, case['prompt'], tdir)
    before = {w: sha(repo / w) for w in case['watch']}
    env = dict(os.environ, **spec['env'])
    t0 = time.time()
    try:
        p = subprocess.run(spec['cmd'], cwd=spec['cwd'], env=env, capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=int(os.environ.get('XTOOL_TIMEOUT', '600')))
        out, err, rc = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or '')
        err, rc = 'TIMEOUT', -9
    except FileNotFoundError as e:
        out, err, rc = '', f'NOT FOUND: {e}', -127
    t1 = time.time()
    (tdir / 'stdout.txt').write_text(out)
    (tdir / 'stderr.txt').write_text(err)
    answer = adapter.answer(out, spec['answer_file'])
    after = {w: sha(repo / w) for w in case['watch']}
    rec = dict(
        trial=tid, tool=adapter.name, version=ver, model=os.environ.get(f'XTOOL_{adapter.name.upper()}_MODEL') or '(default)',
        case=case['id'], group=case['group'], mode=case['mode'], scope=case['scope'], note=case['note'],
        started=time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(t0)), secs=round(t1 - t0, 1), rc=rc,
        cmd=[c if len(c) < 300 else c[:300] + '...' for c in spec['cmd']], workspace=str(ws),
        valid=bool(answer and answer.strip()) and rc not in (-9, -127),
        self_updated=bool(re.search(r'Updated successfully|updating to|auto-?updat(ed|ing)', err, re.I)),
        answer=(answer or '')[:4000], stderr_tail=err[-600:],
        watch_before=before, watch_after=after,
        changed={w: before[w] != after[w] for w in case['watch']},
        hooks=hook_calls(root, t0, t1),
        tool_calls=extract_tool_calls(out)[:40],
        block_messages=extract_block_messages(out + '\n' + err),
        detect_log=detect_evidence(spec['log_dir'], root),
        **judge(answer, out + '\n' + err, mapping),
    )
    append_jsonl(RESULTS / f'{adapter.name}.jsonl', rec)
    if os.environ.get('XTOOL_KEEP_RUNS') != '1':
        shutil.rmtree(root, ignore_errors=True)
    flag = 'OK ' if rec['valid'] else 'INV'
    print(f'[{flag}] {tid} injected={len(rec["injected"])} changed={rec["changed"]} hooks={len(rec["hooks"])}', flush=True)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tool', required=True, choices=sorted(ADAPTERS))
    ap.add_argument('--cases', default='*', help="comma-separated ids or globs, e.g. 'D-*,E-POS'")
    ap.add_argument('--n', type=int, help='override trials per case')
    ap.add_argument('--parallel', type=int, default=1)
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--allow-mixed', action='store_true', help='run project cases while user scope is applied')
    a = ap.parse_args()
    pats = [s.strip() for s in a.cases.split(',') if s.strip()]
    user_applied = MANIFEST.exists()
    sel = []
    for c in CASES:
        if not any(fnmatch.fnmatch(c['id'], p) for p in pats):
            continue
        if c['scope'] == 'user' and not user_applied:
            continue
        if c['scope'] == 'project' and user_applied and not a.allow_mixed:
            continue
        sel.append(c)
    if a.list:
        for c in sel:
            print(f'{c["id"]:<28} n={a.n or c["n"]:<2} mode={c["mode"]:<8} {c["fixture"]}/{c["sub"]}  {c["note"]}')
        print(f'{len(sel)} cases (user scope applied: {user_applied})')
        return
    if not (FIX / 'mapping.json').exists():
        sys.exit('run fixtures.py first')
    hook_sha = (HOOKS / 'hook.py.sha256').read_text().strip()
    adapter = ADAPTERS[a.tool]
    ver = version(adapter)
    print(f'{adapter.name}: {ver}  bin={adapter.bin()}  cases={len(sel)}  user_scope={user_applied}')
    mapping = load_map()
    jobs = [(c, k) for c in sel for k in range(a.n or c['n'])]
    with ThreadPoolExecutor(max(1, a.parallel)) as ex:
        list(ex.map(lambda ck: run_trial(adapter, ck[0], ck[1], ver, mapping), jobs))
    if sha(HOOKS / 'hook.py') != hook_sha:
        print('WARNING: hook.py changed during the run; hook results are not trustworthy', file=sys.stderr)
    ver_after = version(adapter)
    if ver_after != ver:
        print(f'WARNING: {adapter.name} version changed during the run: {ver} -> {ver_after}. '
              'Disable auto-update and re-run.', file=sys.stderr)
    print(f'done: {len(jobs)} trials -> {RESULTS / (adapter.name + ".jsonl")}')


if __name__ == '__main__':
    main()
