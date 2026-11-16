"""Summarize results/*.jsonl into results/summary.md (matrices across tools).

  python3 summarize.py
"""
import collections
import json
from pathlib import Path

from common import RESULTS, load_map


def load():
    recs = []
    for p in sorted(RESULTS.glob('*.jsonl')):
        for ln in p.read_text().splitlines():
            if ln.strip():
                recs.append(json.loads(ln))
    return recs


def frac(k, n):
    return f'{k}/{n}' if n else '-'


def main():
    recs = load()
    mp = load_map()['ids']
    tools = sorted({r['tool'] for r in recs})
    out = ['# cross-tool summary', '', f'records: {len(recs)}', '']
    out += ['## versions / models', '', '| tool | version | model | trials | invalid |', '| --- | --- | --- | --- | --- |']
    for t in tools:
        rs = [r for r in recs if r['tool'] == t]
        out.append(f'| {t} | {", ".join(sorted({r["version"] for r in rs}))} | {", ".join(sorted({r["model"] for r in rs}))} '
                   f'| {len(rs)} | {sum(not r["valid"] for r in rs)} |')

    # injection matrix: label x tool, per case
    out += ['', '## injection (body ID reached the model; n = valid trials)', '']
    by_case = collections.defaultdict(list)
    for r in recs:
        if r['group'] in ('detect', 'single', 'size', 'trigger', 'user', 'negative', 'comply'):
            by_case[r['case']].append(r)
    for case in sorted(by_case):
        rs = [r for r in by_case[case] if r['valid']]
        labels = collections.Counter()
        fm = collections.Counter()
        for r in rs:
            for lab in r['injected_labels']:
                (fm if lab.endswith('#frontmatter') else labels)[(lab.replace('#frontmatter', ''), r['tool'])] += 1
        n = collections.Counter(r['tool'] for r in rs)
        names = sorted({lab for lab, _ in labels} | {lab for lab, _ in fm})
        fab = collections.Counter(r['tool'] for r in rs if r['fabricated'])
        via = collections.Counter(r['tool'] for r in rs if r['via_tool_output'])
        out += [f'### {case}', '', '| file | ' + ' | '.join(tools) + ' |', '| --- |' + ' --- |' * len(tools)]
        for lab in names:
            cells = []
            for t in tools:
                c = frac(labels[(lab, t)], n[t])
                if fm[(lab, t)]:
                    c += f' (frontmatter {fm[(lab, t)]})'
                cells.append(c)
            out.append(f'| {lab} | ' + ' | '.join(cells) + ' |')
        out.append('| (fabricated IDs) | ' + ' | '.join(frac(fab[t], n[t]) for t in tools) + ' |')
        out.append('| (IDs seen via tool output) | ' + ' | '.join(frac(via[t], n[t]) for t in tools) + ' |')
        if case.startswith(('D-HELLO', 'U-LANG')):
            ja = collections.Counter(r['tool'] for r in rs if r['japanese'])
            out.append('| (answer in Japanese) | ' + ' | '.join(frac(ja[t], n[t]) for t in tools) + ' |')
        out.append('')

    # hook sources
    out += ['## hook config discovery (log-only hooks)', '']
    hs = [r for r in recs if r['group'] == 'hooksrc']
    src = collections.Counter()
    names = collections.defaultdict(set)
    n = collections.Counter()
    for r in hs:
        n[(r['case'], r['tool'])] += 1
        seen = set()
        for h in r['hooks']:
            seen.add(h['source'])
            names[(h['source'], r['tool'])].add(f'{h.get("event")}:{h.get("tool_name")}')
        for s in seen:
            src[(r['case'], s, r['tool'])] += 1
    for case in sorted({r['case'] for r in hs}):
        from fixtures import HOOK_CONFIGS_NATIVE
        prefix = 'native' if case == 'H-NATIVE' else 'claude-schema'
        expected = {f'{prefix}:{rel}' for rel, _ in HOOK_CONFIGS_NATIVE}
        out += [f'### {case}', '', '| config file | ' + ' | '.join(tools) + ' |', '| --- |' + ' --- |' * len(tools)]
        for s in sorted(expected | {s for c, s, _ in src if c == case}):
            out.append(f'| {s} | ' + ' | '.join(
                f'{frac(src[(case, s, t)], n[(case, t)])} {sorted(names[(s, t)])[:4] if names[(s, t)] else ""}' for t in tools) + ' |')
        out.append('| (trials) | ' + ' | '.join(str(n[(case, t)]) for t in tools) + ' |')
        out.append('')

    # enforcement / matcher
    for grp, title, key in [('enforce', 'enforcement (secret.txt unchanged = blocked)', 'secret.txt'),
                            ('matcher', 'matcher in .claude/settings.json (out.txt not created = blocked)', 'out.txt')]:
        rs = [r for r in recs if r['group'] == grp and r['valid']]
        out += [f'## {title}', '', '| case | ' + ' | '.join(tools) + ' |', '| --- |' + ' --- |' * len(tools)]
        for case in sorted({r['case'] for r in rs}):
            cells = []
            for t in tools:
                x = [r for r in rs if r['case'] == case and r['tool'] == t]
                kept = sum(not r['changed'].get(key, False) for r in x)
                cells.append(frac(kept, len(x)))
            out.append(f'| {case} | ' + ' | '.join(cells) + ' |')
        out.append('')
    out += ['Notes: "blocked" only means the file did not change; read the answer and hooks fields of each record before '
            'concluding that a hook or rule (and not the model itself) stopped the action. Positive control E-POS must '
            'show 0/N for the matrix to mean anything.']
    (RESULTS / 'summary.md').write_text('\n'.join(out) + '\n')
    print(f'wrote {RESULTS / "summary.md"}')


if __name__ == '__main__':
    main()
