"""Write results/report.md: one experiment record per case, ready to paste into a verification report.

  python3 report.py                 # all tools found in results/
  python3 report.py --tools cortex  # subset

For every case: what was placed, the exact prompt and command, the docs expectation per tool, the measured
counts, what was observed (tool calls, block messages, hook calls, files named in the tool's own log), an
example answer, a mechanical verdict (一致 / 不一致 / 記録のみ) and an empty interpretation field.
"""
import argparse
import collections
import json
import re
import time
from pathlib import Path

import expect
from cases import CASES
from common import FIX, RESULTS, ROOT, extract_block_messages, extract_tool_calls, load_map
from fixtures import HOOK_CONFIGS_NATIVE

HOME = str(Path.home())
VERDICT = {True: '一致', False: '不一致', None: '記録のみ'}


# ---------------------------------------------------------------- loading
def load(tools):
    recs = []
    for p in sorted(RESULTS.glob('*.jsonl')):
        for ln in p.read_text().splitlines():
            if not ln.strip():
                continue
            r = json.loads(ln)
            if tools and r['tool'] not in tools:
                continue
            raw = RESULTS / 'raw' / r['trial']
            if 'tool_calls' not in r and (raw / 'stdout.txt').exists():      # backfill older records
                out = (raw / 'stdout.txt').read_text(errors='ignore')
                err = (raw / 'stderr.txt').read_text(errors='ignore') if (raw / 'stderr.txt').exists() else ''
                r['tool_calls'] = extract_tool_calls(out)[:40]
                r['block_messages'] = extract_block_messages(out + '\n' + err)
            recs.append(r)
    return recs


def clean(s):
    s = str(s)
    for root in {str(ROOT), str(ROOT).replace('/private/tmp/', '/tmp/', 1)}:
        s = re.sub(re.escape(root) + r'/(runs|manual)/[^/\s"\']+/', '<run>/', s)
        s = s.replace(root, '$XTOOL_ROOT')
    return s.replace(HOME, '~')


def show_cmd(r, prompt):
    out = []
    ws = r.get('workspace', '')
    for i, c in enumerate(r.get('cmd', [])):
        if i == 0:
            c = Path(c).name
        elif c == prompt or (len(c) > 60 and prompt.startswith(c[:60])):
            c = '"<prompt>"'
        elif ws and c == ws:
            c = '<ws>'
        out.append(clean(c))
    return ' '.join(out)


# ---------------------------------------------------------------- id locations
def locate(path, fixture):
    p = Path(path)
    for base in (FIX / fixture / 'repo',):
        try:
            return 'repo', str(p.relative_to(base))
        except ValueError:
            pass
    try:
        return 'above', str(p.relative_to(FIX / fixture))
    except ValueError:
        pass
    try:
        return 'user', str(p.relative_to(HOME))
    except ValueError:
        return None, None


def case_labels(case, ids):
    """Body IDs relevant to a case: files of its fixture (+ user files for user-scope cases)."""
    out = []
    for i, m in ids.items():
        if m['kind'] != 'body':
            continue
        loc, rel = locate(m['path'], case['fixture'])
        if loc in ('repo', 'above') or (loc == 'user' and case['scope'] == 'user'):
            out.append((i, m['label'], loc, rel))
    return sorted(out, key=lambda x: x[1])


# ---------------------------------------------------------------- per-case evaluation
def eval_inject(case, tool, rs, labels):
    present = frozenset(rel for _, _, loc, rel in labels if loc == 'repo')
    rows, mism, n_ok, n_rec = [], [], 0, 0
    n = len(rs)
    for i, lab, loc, rel in labels:
        k = sum(i in r['injected'] for r in rs)
        exp = expect.expect_inject(tool, case, loc, rel, lab, present)
        obs = None if n == 0 else (True if k == n else False if k == 0 else 'split')
        if exp is None or n == 0:
            v = None
            n_rec += 1
        else:
            v = (obs == exp)
            if v:
                n_ok += 1
            else:
                mism.append(f'{clean(lab)}: 期待={"注入" if exp else "非注入"} / 実測={k}/{n}')
        rows.append((lab, k, n, exp, v))
    verdict = False if mism else (True if n_ok else None)
    return rows, mism, verdict


def eval_hooks(case, tool, rs):
    prefix = 'native' if case['id'] == 'H-NATIVE' else 'claude-schema'
    rows, mism, n_ok = [], [], 0
    n = len(rs)
    names = collections.defaultdict(set)
    for r in rs:
        for h in r.get('hooks', []):
            names[h['source']].add(f'{h.get("event")}:{h.get("tool_name")}')
    for rel, _ in HOOK_CONFIGS_NATIVE:
        src = f'{prefix}:{rel}'
        k = sum(any(h['source'] == src for h in r.get('hooks', [])) for r in rs)
        exp = expect.expect_hook(tool, case['id'], rel)
        obs = None if n == 0 else (True if k == n else False if k == 0 else 'split')
        v = None if exp is None or n == 0 else (obs == exp)
        if v is False:
            mism.append(f'{rel}: 期待={"発火" if exp else "不発火"} / 実測={k}/{n}')
        elif v:
            n_ok += 1
        rows.append((rel, k, n, exp, v, sorted(names[src])))
    return rows, mism, (False if mism else (True if n_ok else None))


def eval_block(case, tool, rs, key):
    n = len(rs)
    kept = sum(not r['changed'].get(key, False) for r in rs)
    exp = expect.expect_block(tool, case['id'])
    obs = None if n == 0 else (True if kept == n else False if kept == 0 else 'split')
    v = None if exp is None or n == 0 else (obs == exp)
    mism = [] if v is not False else [f'期待={"阻止" if exp else "書き換え"} / 実測=阻止 {kept}/{n}']
    return kept, n, exp, v, mism


# ---------------------------------------------------------------- rendering helpers
def fixture_section(fx, ids):
    root = FIX / fx
    by_path = collections.defaultdict(list)
    for i, m in ids.items():
        by_path[m['path']].append((m['kind'], i))
    lines = [f'#### fixture `{fx}`', '', '```']
    code = []
    for p in sorted(root.rglob('*')):
        if '.git' in p.relative_to(root).parts or p.is_dir():
            continue
        rel = str(p.relative_to(root))
        if rel == 'mapping.json':
            continue
        tags = by_path.get(str(p))
        if tags:
            body = [i for k, i in tags if k == 'body']
            fm = [i for k, i in tags if k == 'frontmatter']
            head = p.read_text(errors='ignore').split('\n---\n')[0] if fm else ''
            fmtxt = ' frontmatter: ' + ', '.join(l for l in head.strip('-\n').splitlines() if not l.startswith('note:')) if fm else ''
            size = p.stat().st_size
            lines.append(f'{rel}  [指示ファイル, ID {"/".join(body)}{", " + str(size) + " bytes" if size > 5000 else ""}]{fmtxt}')
        elif p.suffix in ('.json', '.toml') or rel.endswith('secret.txt'):
            txt = clean(p.read_text(errors='ignore')).replace('\n', ' ')
            txt = re.sub(r'\s+', ' ', txt)
            lines.append(f'{rel}  = {txt[:260]}')
        elif p.name == 'AGENTS.md' or p.suffix in ('.md', '.mdc') or p.name == '.cursorrules':
            lines.append(f'{rel}  = {clean(p.read_text(errors="ignore")).strip()[:160]}')
        else:
            code.append(rel)
    lines.append(f'(コードファイル: {", ".join(code)})' if code else '')
    lines += ['```', '']
    return lines


def tool_call_summary(rs):
    c = collections.Counter()
    for r in rs:
        for name in sorted({t['name'] for t in r.get('tool_calls', [])}):
            c[name] += 1
    return ', '.join(f'{k} {v}/{len(rs)}' for k, v in c.most_common()) or 'なし'


def first_examples(rs, field, limit=3):
    seen = []
    for r in rs:
        for x in r.get(field, []):
            x = clean(x)
            if x not in seen:
                seen.append(x)
    return seen[:limit]


def example_call(rs, names=('bash', 'Bash', 'shell', 'write', 'Write', 'edit', 'Edit')):
    for r in rs:
        for t in r.get('tool_calls', []):
            if t['name'] in names:
                return f'{t["name"]}: {clean(t["input"])[:160]}'
    return None


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tools', help='comma-separated, default: all in results/')
    a = ap.parse_args()
    want = set(a.tools.split(',')) if a.tools else None
    recs = load(want)
    if not recs:
        raise SystemExit('no records in results/')
    ids = load_map()['ids']
    tools = sorted({r['tool'] for r in recs}, key=lambda t: (expect.TOOLS + list(expect.FAMILY)).index(t)
                   if t in expect.TOOLS + list(expect.FAMILY) else 99)
    by = collections.defaultdict(list)
    for r in recs:
        by[(r['case'], r['tool'])].append(r)

    out = ['# クロスツール検証 実験記録', '',
           f'生成: {time.strftime("%Y-%m-%d %H:%M")}（`report.py`）。数値はすべて実測、「期待」は `expect.py` に書いた各ツールの docs の記述（2026-11-16 時点）。'
           '「判定」は期待値と実測の機械的な比較で、原因の解釈は「解釈」欄に人が書く。', '',
           '期待値の出典（詳細は `expect.py` のコメントと REQUIREMENTS.md 9 章）: CoCo = Desktop docs「Instruction files」・Extensibility・'
           'changelog 1.1.47（CLI 専用の記述が無いため Desktop docs を期待値とした）、Claude Code = memory / hooks / permissions、'
           'Codex = AGENTS.md / hooks / permissions、Cursor = rules / hooks / third-party hooks / CLI permissions、'
           'Copilot = CLI custom instructions / hooks reference / allowing tools。', '']
    # environment
    out += ['## 1. 実施環境', '', '| ツール | バージョン | モデル | 試行 | 無効 | 実施日時 |', '| --- | --- | --- | --- | --- | --- |']
    for t in tools:
        rs = [r for r in recs if r['tool'] == t]
        st = sorted(r['started'] for r in rs)
        out.append(f'| {t} | {", ".join(sorted({r["version"] for r in rs}))} | {", ".join(sorted({r["model"] for r in rs}))} '
                   f'| {len(rs)} | {sum(not r["valid"] for r in rs)} | {st[0]} 〜 {st[-1]} |')
    upd = [r['trial'] for r in recs if r.get('self_updated')]
    out += ['', f'実行中の自己更新: {"あり " + str(len(upd)) + " 試行（バージョン記録が不正確な可能性）" if upd else "検出なし"}。',
            '', '再現手順: `python3 fixtures.py` → `python3 run.py --tool <tool> [--cases ...]` → `python3 report.py`。'
            '各試行は fixture の新しいコピー（`<run>/`）で実行した。', '']

    # evaluate all cases first
    evals = {}
    for c in CASES:
        for t in tools:
            rs = [r for r in by.get((c['id'], t), []) if r['valid']]
            allr = by.get((c['id'], t), [])
            if not allr:
                continue
            g = c['group']
            if g in ('detect', 'single', 'size', 'trigger', 'user'):
                rows, mism, v = eval_inject(c, t, rs, case_labels(c, ids))
                if c['id'] == 'U-LANG':
                    exp = expect.expect_japanese(t, c['id'])
                    k = sum(r['japanese'] for r in rs)
                    if exp is not None:
                        ok = (k == 0) if exp is False else (k == len(rs))
                        v = v if ok and v is not False else (False if not ok else v)
                        if not ok:
                            mism.append(f'回答言語: 期待={"日本語" if exp else "英語"} / 実測=日本語 {k}/{len(rs)}')
                evals[(c['id'], t)] = dict(kind='inject', rows=rows, mism=mism, v=v, rs=rs, all=allr)
            elif g == 'hooksrc':
                rows, mism, v = eval_hooks(c, t, rs)
                evals[(c['id'], t)] = dict(kind='hook', rows=rows, mism=mism, v=v, rs=rs, all=allr)
            elif g in ('enforce', 'matcher'):
                key = 'secret.txt' if g == 'enforce' else 'out.txt'
                kept, n, exp, v, mism = eval_block(c, t, rs, key)
                evals[(c['id'], t)] = dict(kind='block', kept=kept, n=n, exp=exp, v=v, mism=mism, rs=rs, all=allr)
            elif g == 'negative':
                k = sum(bool(r['fabricated']) for r in rs)
                v = (k == 0) if rs else None
                evals[(c['id'], t)] = dict(kind='neg', k=k, n=len(rs), v=v, mism=[] if v is not False else [f'捏造 {k}/{len(rs)}'],
                                           rs=rs, all=allr)
            else:
                evals[(c['id'], t)] = dict(kind='other', v=None, mism=[], rs=rs, all=allr)

    # hypothesis table
    out += ['## 2. 仮説判定（REQUIREMENTS.md の X-xx）', '',
            '仮説ごとに、対象ツール・対象ケース・対象ファイル（`expect.py` の `HYP`）に絞って期待値と実測を比べたもの。'
            '「docs通り」= 対象行がすべて一致、「docsと不一致」= 1 つでも不一致（括弧内は不一致のケース）、'
            '「記録のみ」= docs に期待値が無い、「対象外」= その仮説が扱わないツール、「未実施」= 記録なし。', '',
            '| 仮説 | ' + ' | '.join(tools) + ' |', '| --- |' + ' --- |' * len(tools)]

    def hyp_cell(h, t):
        htools, globs, rx = expect.HYP[h]
        if htools and expect.FAMILY.get(t, t) not in htools:
            return '対象外'
        vs = []
        for c in CASES:
            if not any(__import__('fnmatch').fnmatch(c['id'], g) for g in globs) or (c['id'], t) not in evals:
                continue
            e = evals[(c['id'], t)]
            if e['kind'] in ('inject', 'hook') and rx:
                sel = [row for row in e['rows'] if re.search(rx, row[0])]
                vs += [(c['id'], row[4]) for row in sel]
            else:
                vs.append((c['id'], e['v']))
        if not vs:
            return '未実施'
        bad = sorted({cid for cid, v in vs if v is False})
        if bad:
            return 'docsと不一致（' + ', '.join(bad)[:120] + '）'
        return 'docs通り' if any(v is True for _, v in vs) else '記録のみ'

    for h in sorted(expect.HYP, key=lambda h: int(h.split('-')[1])):
        out.append(f'| {h} | ' + ' | '.join(hyp_cell(h, t) for t in tools) + ' |')
    out.append('')

    # fixtures
    used = []
    for c in CASES:
        if any((c['id'], t) in evals for t in tools) and c['fixture'] not in used:
            used.append(c['fixture'])
    out += ['## 3. 配置したファイル（fixture）', '',
            '各ファイルの ID は `mapping.json` と対応。指示ファイルにはそれぞれ固有の VERIFY-ID とタグ規則 `Always end every answer '
            'with the tag [TAG-xxxxxx]` を 1 つずつ書いている。frontmatter 内には別の FM-ID を置いている。', '']
    for fx in used:
        out += fixture_section(fx, ids)

    # experiment records
    out += ['## 4. 実験記録（ケースごと）', '']
    for c in CASES:
        present = [t for t in tools if (c['id'], t) in evals]
        if not present:
            continue
        hy = ', '.join(sorted({h for t in present for h in expect.hyp_for(c['id'], t)}, key=lambda h: int(h[2:]))) or '-'
        out += [f'### {c["id"]} — {c["note"] or c["group"]}（仮説 {hy}）', '',
                f'- 配置: fixture `{c["fixture"]}`、ワークスペース = `{c["fixture"]}/{c["sub"]}`、モード `{c["mode"]}`'
                + (f'、監視ファイル `{", ".join(c["watch"])}`' if c['watch'] else ''),
                f'- プロンプト: `{c["prompt"]}`']
        for t in present:
            out.append(f'- コマンド（{t}）: `{show_cmd(evals[(c["id"], t)]["all"][0], c["prompt"])}`')
        out.append('')
        e0 = evals[(c['id'], present[0])]
        if e0['kind'] == 'inject':
            out += ['| ファイル | ' + ' | '.join(f'{t} 期待 | {t} 実測' for t in present) + ' |',
                    '| --- |' + ' --- | --- |' * len(present)]
            labs = [row[0] for row in e0['rows']]
            for li, lab in enumerate(labs):
                cells = []
                for t in present:
                    _, k, n, exp, v = evals[(c['id'], t)]['rows'][li]
                    cells += [{True: '注入', False: '非注入', None: '—'}[exp], f'{k}/{n}' + (' ✗' if v is False else '')]
                out.append(f'| {clean(lab)} | ' + ' | '.join(cells) + ' |')
            if c['id'] in ('D-HELLO', 'U-LANG'):
                out.append('| (回答が日本語) | ' + ' | '.join(
                    f'— | {sum(r["japanese"] for r in evals[(c["id"], t)]["rs"])}/{len(evals[(c["id"], t)]["rs"])}' for t in present) + ' |')
            out.append('')
        elif e0['kind'] == 'hook':
            out += ['| 設定ファイル | ' + ' | '.join(f'{t} 期待 | {t} 実測' for t in present) + ' |',
                    '| --- |' + ' --- | --- |' * len(present)]
            for ri, row in enumerate(e0['rows']):
                cells = []
                for t in present:
                    rel, k, n, exp, v, nm = evals[(c['id'], t)]['rows'][ri]
                    cells += [{True: '発火', False: '不発火', None: '—'}[exp],
                              f'{k}/{n}' + (' ✗' if v is False else '') + (f' {", ".join(nm[:3])}' if nm else '')]
                out.append(f'| `{row[0]}` | ' + ' | '.join(cells) + ' |')
            out.append('')
        elif e0['kind'] == 'block':
            out += ['| ツール | 期待 | 阻止（ファイル不変） | 判定 |', '| --- | --- | --- | --- |']
            for t in present:
                e = evals[(c['id'], t)]
                exp = {True: '阻止', False: '書き換え', None: '—'}[e['exp']]
                out.append(f'| {t} | {exp} | {e["kept"]}/{e["n"]} | {VERDICT[e["v"]]} |')
            out.append('')
        elif e0['kind'] == 'neg':
            out += ['| ツール | 捏造した試行 | 判定 |', '| --- | --- | --- |']
            for t in present:
                e = evals[(c['id'], t)]
                out.append(f'| {t} | {e["k"]}/{e["n"]} | {VERDICT[e["v"]]} |')
            out.append('')
        # observations
        out.append('観測:')
        for t in present:
            e = evals[(c['id'], t)]
            rs = e['rs']
            inv = len(e['all']) - len(rs)
            bits = [f'有効 {len(rs)}/{len(e["all"])}' + (f'（無効 {inv}）' if inv else ''),
                    f'呼ばれたツール: {tool_call_summary(rs)}']
            ex = example_call(rs)
            if ex:
                bits.append(f'例 `{ex}`')
            bm = first_examples(rs, 'block_messages', 2)
            if bm:
                bits.append('ブロック表示: ' + ' / '.join(f'`{x[:120]}`' for x in bm))
            hk = sorted({f'{h["source"]}→{h.get("event")}:{h.get("tool_name")}' for r in rs for h in r.get('hooks', [])})
            if hk and e['kind'] != 'hook':
                bits.append('hook 呼び出し: ' + ', '.join(f'`{x}`' for x in hk[:4]))
            dl = sorted({clean(x).replace('\\', '') for r in rs[:1] for x in (r.get('detect_log') or [])})
            if dl:
                bits.append('ツールのログに出た設定ファイル: ' + ', '.join(f'`{x.split("/", 2)[-1] if x.count("/") >= 2 else x}`' for x in dl[:12]))
            tags = collections.Counter(tg for r in rs for tg in r.get('tags', []))
            if c['id'] == 'D-HELLO' and tags:
                bits.append(f'タグ遵守: {len(tags)} 種のタグが出現（各 {min(tags.values())}〜{max(tags.values())}/{len(rs)} 試行）')
            out.append(f'- {t}: ' + '。'.join(bits))
        out.append('')
        for t in present:
            rs = evals[(c['id'], t)]['rs']
            if rs:
                ans = clean(rs[0]['answer']).strip().replace('\n', ' ')
                out.append(f'回答例（{t}）: > {ans[:360]}{"…" if len(ans) > 360 else ""}')
        out.append('')
        out.append('判定: ' + ' / '.join(f'{t} **{VERDICT[evals[(c["id"], t)]["v"]]}**' for t in present))
        for t in present:
            for m in evals[(c['id'], t)]['mism']:
                out.append(f'- {t}: {m}')
        out += ['', '解釈: （記入）', '']

    (RESULTS / 'report.md').write_text('\n'.join(out) + '\n')
    print(f'wrote {RESULTS / "report.md"} ({len(evals)} case×tool evaluations)')


if __name__ == '__main__':
    main()
