"""Temporarily place user-scope test files under ~ and restore the originals afterwards.

  python3 user_scope.py status
  python3 user_scope.py apply [--with-hooks]   # moves existing files to ~/.xtool-verify-backup/<ts>/
  python3 user_scope.py restore                # deletes test files, moves originals back, checks sha256

Close every AI coding tool (CoCo, Claude Code, Codex, Cursor, Copilot) before apply and restore.
Files that are never touched: ~/.snowflake/cortex/settings.json, ~/.codex/config.toml (auth/model), credentials.
"""
import json
import shutil
import sys
import time
from pathlib import Path

from common import HOOKS, MAPF, Mapping, load_map, sha

HOME = Path.home()
BK = HOME / '.xtool-verify-backup'
MANIFEST = BK / 'active-manifest.json'
JA = 'Always answer in Japanese.'

INSTRUCTION_FILES = [  # (path, frontmatter)
    ('.snowflake/cortex/AGENTS.md', None),       # CoCo (primary user location)
    ('AGENTS.md', None),                         # CoCo docs: ~/
    ('CLAUDE.md', None),                         # CoCo docs: ~/
    ('.claude/CLAUDE.md', None),                 # Claude Code
    ('.claude/rules/xtool-u.md', None),          # Claude Code, CoCo docs
    ('.cursor/rules/xtool-u.mdc', {'alwaysApply': 'true'}),  # CoCo docs (Cursor user rules are UI-based)
    ('.codex/AGENTS.md', None),                  # Codex
    ('.copilot/copilot-instructions.md', None),  # Copilot CLI
    ('.copilot/instructions/xtool-u.instructions.md', {'applyTo': '"**"'}),
]
HOOK_FILES = [  # user-level hook configs (only with --with-hooks)
    '.claude/settings.json', '.snowflake/cortex/hooks.json', '.codex/hooks.json',
    '.cursor/hooks.json', '.copilot/hooks/xtool.json',
]


def _hook_payload(rel):
    from fixtures import claude_style, copilot_style, cursor_style
    src = f'user:~/{rel}'
    if rel.startswith('.cursor/'):
        return cursor_style(src, 'log')
    if rel.startswith('.copilot/'):
        return copilot_style(src, 'log')
    return claude_style(src, 'log')


def status():
    if MANIFEST.exists():
        m = json.loads(MANIFEST.read_text())
        print(f'APPLIED at {m["applied_at"]}: {len(m["entries"])} paths. Run "restore" when done.')
    else:
        print('not applied')
    for rel, _ in INSTRUCTION_FILES:
        p = HOME / rel
        print(('exists  ' if p.exists() else 'absent  ') + str(p))
    for rel in HOOK_FILES:
        p = HOME / rel
        print(('exists  ' if p.exists() else 'absent  ') + str(p))


def apply(with_hooks):
    if MANIFEST.exists():
        sys.exit('already applied; run restore first')
    if not MAPF.exists():
        sys.exit('run fixtures.py first')
    ts = time.strftime('%Y%m%d-%H%M%S')
    bdir = BK / ts
    bdir.mkdir(parents=True)
    mp = Mapping()
    mp.m = load_map()
    entries = []

    def save():
        MANIFEST.write_text(json.dumps({'applied_at': ts, 'backup_dir': str(bdir), 'entries': entries}, indent=1))

    targets = [(rel, 'instr', fm) for rel, fm in INSTRUCTION_FILES]
    if with_hooks:
        targets += [(rel, 'hook', None) for rel in HOOK_FILES]
    for rel, kind, fm in targets:
        p = HOME / rel
        e = {'rel': rel, 'kind': kind, 'backup': None, 'orig_sha': None}
        created = [str(d) for d in reversed(p.parents) if str(d).startswith(str(HOME) + '/') and not d.exists()]
        e['created_dirs'] = created
        entries.append(e)
        save()   # record intent before touching anything, so a crash can still be restored
        if p.exists():
            if p.is_dir():
                sys.exit(f'{p} is a directory; aborting before any change')
            dst = bdir / rel.replace('/', '__')
            e['orig_sha'] = sha(p)
            e['backup'] = str(dst)
            save()
            shutil.move(str(p), str(dst))
        p.parent.mkdir(parents=True, exist_ok=True)
        if kind == 'instr':
            from common import write_instruction
            write_instruction(mp, p, f'USER/~/{rel}', fm=fm, rule=JA)
        else:
            p.write_text(json.dumps(_hook_payload(rel), indent=1))
        e['test_sha'] = sha(p)
        save()
    mp.save()
    print(f'applied {len(entries)} files; originals in {bdir}')


def restore():
    if not MANIFEST.exists():
        sys.exit('nothing to restore')
    m = json.loads(MANIFEST.read_text())
    problems = []
    for e in reversed(m['entries']):
        p = HOME / e['rel']
        if p.exists():
            if sha(p) == e.get('test_sha'):
                p.unlink()
            elif e.get('backup') and not Path(e['backup']).exists() and sha(p) == e['orig_sha']:
                pass   # crash before the move: the original is still in place
            else:
                problems.append(f'{p} changed since apply; left in place, original NOT restored')
                continue
        if e['backup'] and Path(e['backup']).exists():
            shutil.move(e['backup'], str(p))
            if sha(p) != e['orig_sha']:
                problems.append(f'{p} hash mismatch after restore')
        for d in reversed(e.get('created_dirs', [])):   # remove only dirs we created, only if empty
            try:
                Path(d).rmdir()
            except OSError:
                pass
    report = {'restored_at': time.strftime('%Y%m%d-%H%M%S'), 'problems': problems, **m}
    (Path(m['backup_dir']) / 'restore-report.json').write_text(json.dumps(report, indent=1))
    if problems:
        print('RESTORE FINISHED WITH PROBLEMS:\n  ' + '\n  '.join(problems))
        print(f'manifest kept at {MANIFEST}')
        sys.exit(1)
    MANIFEST.unlink()
    print('restored; all hashes match')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd == 'apply':
        apply('--with-hooks' in sys.argv)
    elif cmd == 'restore':
        restore()
    else:
        status()
