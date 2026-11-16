"""Build every dummy workspace used by the cross-tool verification.

Usage:  python3 fixtures.py            # (re)creates $XTOOL_ROOT (default /tmp/xtool-verify)

Nothing outside $XTOOL_ROOT is touched. User-scope files are handled by user_scope.py.
"""
import json
import shutil
import sys

from common import FIX, HOOKS, INVLOG, ROOT, Mapping, git_commit, git_init, write_instruction

LOREM = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor. '
HOOK_PY = HOOKS / 'hook.py'

# Every candidate instruction file, relative to the git root.
# (rel_path, frontmatter or None). Frontmatter variants test conditional / always rules.
CANDIDATES = [
    ('AGENTS.md', None),
    ('AGENTS.override.md', None),          # Codex
    ('CLAUDE.md', None),
    ('CLAUDE.local.md', None),             # Claude Code
    ('.claude/CLAUDE.md', None),
    ('CORTEX.md', None),                   # CoCo
    ('SNOWFLAKE.md', None),                # CoCo (docs)
    ('RULES.md', None),                    # CoCo (docs)
    ('GEMINI.md', None),                   # Copilot CLI (docs)
    ('.cursorrules', None),
    ('.cursor/rules/plain.mdc', {'description': '"plain rule"'}),
    ('.cursor/rules/always.mdc', {'alwaysApply': 'true'}),
    ('.cursor/rules/sql.mdc', {'globs': '["**/*.sql"]', 'alwaysApply': 'false'}),
    ('.cursor/rules/notmdc.md', None),     # Cursor docs: plain .md in rules dir is ignored
    ('.claude/rules/plain.md', None),
    ('.claude/rules/api.md', {'paths': '["src/api/**/*.ts"]'}),
    ('.github/copilot-instructions.md', None),
    ('.github/instructions/all.instructions.md', {'applyTo': '"**"'}),
    ('.github/instructions/sql.instructions.md', {'applyTo': '"**/*.sql"'}),
]


def slug(rel):
    return rel.strip('.').replace('/', '_').replace('.', '_').lower()


def code_files(repo):
    (repo / 'src/api').mkdir(parents=True, exist_ok=True)
    (repo / 'src/api/handler.ts').write_text('export function handler() {\n  return 1;\n}\n')
    (repo / 'src/dummy.txt').write_text('dummy\n')
    (repo / 'queries').mkdir(exist_ok=True)
    (repo / 'queries/sample.sql').write_text('SELECT 42 AS answer;\n')
    (repo / 'docs').mkdir(exist_ok=True)
    (repo / 'docs/readme.txt').write_text('Plain readme without instructions.\n')
    (repo / 'README.md').write_text('# dummy repo for verification\n')


def build_detect(mp):
    """detect-parent/AGENTS.md (above git root) + detect-parent/repo (git root) with all candidates."""
    parent = FIX / 'detect-parent'
    repo = parent / 'repo'
    git_init(repo)
    write_instruction(mp, parent / 'AGENTS.md', 'ABOVE-GIT-ROOT/AGENTS.md')
    for rel, fm in CANDIDATES:
        write_instruction(mp, repo / rel, f'ROOT/{rel}', fm=fm)
    write_instruction(mp, repo / 'docs/AGENTS.md', 'SUBDIR docs/AGENTS.md')
    write_instruction(mp, repo / 'docs/CLAUDE.md', 'SUBDIR docs/CLAUDE.md')
    write_instruction(mp, repo / 'src/api/AGENTS.md', 'SUBDIR src/api/AGENTS.md')
    write_instruction(mp, repo / 'packages/pkg-a/AGENTS.md', 'PKG packages/pkg-a/AGENTS.md')
    write_instruction(mp, repo / 'packages/pkg-a/CLAUDE.md', 'PKG packages/pkg-a/CLAUDE.md')
    write_instruction(mp, repo / 'packages/pkg-a/src/AGENTS.md', 'PKG-SUB packages/pkg-a/src/AGENTS.md')
    code_files(repo)
    (repo / 'packages/pkg-a/src/index.ts').write_text('export const a = 1;\n')
    git_commit(repo)


def build_singles(mp):
    """One git repo per candidate so each file can be tested in isolation."""
    for rel, fm in CANDIDATES:
        repo = FIX / f'single-{slug(rel)}' / 'repo'
        git_init(repo)
        write_instruction(mp, repo / rel, f'SINGLE/{rel}', fm=fm)
        code_files(repo)
        git_commit(repo)
    # Claude Code docs: AGENTS.md is read only when no CLAUDE.md exists -> both-present repo
    repo = FIX / 'pair-agents-claude' / 'repo'
    git_init(repo)
    write_instruction(mp, repo / 'AGENTS.md', 'PAIR/AGENTS.md')
    write_instruction(mp, repo / 'CLAUDE.md', 'PAIR/CLAUDE.md')
    code_files(repo)
    git_commit(repo)
    # case-insensitivity
    repo = FIX / 'case' / 'repo'
    git_init(repo)
    for rel in ['agents.md', 'Claude.md', '.github/Copilot-Instructions.md']:
        write_instruction(mp, repo / rel, f'CASE/{rel}')
    code_files(repo)
    git_commit(repo)


def big(mp, path, n, label):
    path.parent.mkdir(parents=True, exist_ok=True)
    a = mp.add_id(path, label + ' (start)')
    b = mp.add_id(path, label + ' (end)')
    filler = (LOREM * (n // len(LOREM) + 1))[:n]
    path.write_text(f'VERIFY-ID for this file: {a}\n{filler}\nVERIFY-ID (end of file): {b}\n')


def build_size(mp):
    for n, name in [(40_000, 'size-40k'), (120_000, 'size-120k')]:
        repo = FIX / name / 'repo'
        git_init(repo)
        big(mp, repo / 'AGENTS.md', n, f'{name}/AGENTS.md')
        big(mp, repo / 'CLAUDE.md', n, f'{name}/CLAUDE.md')
        big(mp, repo / '.github/copilot-instructions.md', n, f'{name}/copilot-instructions.md')
        write_instruction(mp, repo / '.cursor/rules/small.mdc', f'{name}/small.mdc', fm={'alwaysApply': 'true'})
        code_files(repo)
        git_commit(repo)


# ---------------------------------------------------------------- hooks
def cmd(source, mode):
    return f"python3 '{HOOK_PY}' '{source}' {mode}"


def claude_style(source, mode, matcher='.*'):
    return {'hooks': {'PreToolUse': [{'matcher': matcher, 'hooks': [
        {'type': 'command', 'command': cmd(source, mode), 'timeout': 30}]}]}}


def cursor_style(source, mode):
    return {'version': 1, 'hooks': {
        'preToolUse': [{'command': cmd(source, mode)}],
        'beforeShellExecution': [{'command': cmd(source, mode)}],
        'beforeReadFile': [{'command': cmd(source, mode)}]}}


def copilot_style(source, mode):
    return {'version': 1, 'hooks': {'preToolUse': [
        {'type': 'command', 'bash': cmd(source, mode), 'timeoutSec': 30}]}}


def codex_toml(source, mode, matcher='.*'):
    return ('[[hooks.PreToolUse]]\n'
            f'matcher = "{matcher}"\n'
            '[[hooks.PreToolUse.hooks]]\n'
            'type = "command"\n'
            f"command = \"{cmd(source, mode)}\"\n")


# Project-level hook config candidates: (rel_path, builder) -- native schema per docs.
HOOK_CONFIGS_NATIVE = [
    ('.cortex/settings.json', claude_style),             # CoCo
    ('.cortex/settings.local.json', claude_style),       # CoCo (docs C-EXT)
    ('.snowflake/cortex/settings.json', claude_style),   # CoCo Desktop docs
    ('.claude/settings.json', claude_style),             # Claude Code (+CoCo/Cursor/Copilot per docs)
    ('.claude/settings.local.json', claude_style),
    ('.codex/hooks.json', claude_style),                 # Codex (schema assumed Claude-like; verify)
    ('.codex/config.toml', None),                        # Codex TOML
    ('.cursor/hooks.json', cursor_style),                # Cursor
    ('.github/hooks/xtool.json', copilot_style),         # Copilot
    ('.github/copilot/settings.json', copilot_style),    # Copilot inline hooks (schema assumed; verify)
]


MATCHERS = [('lower-bash', 'bash'), ('pascal-Bash', 'Bash'), ('lower-shell', 'shell'), ('pascal-Shell', 'Shell'),
            ('any-shell', 'Bash|bash|Shell|shell')]


def write_hook_config(repo, rel, builder, mode, schema):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    source = f'{schema}:{rel}'
    if rel.endswith('.toml'):
        p.write_text(codex_toml(source, mode))
    else:
        p.write_text(json.dumps((builder or claude_style)(source, mode), indent=1))


def build_hooks(mp):
    # H-NATIVE: each candidate file in its own documented schema, all logging (never blocking)
    repo = FIX / 'hooks-native' / 'repo'
    git_init(repo)
    for rel, builder in HOOK_CONFIGS_NATIVE:
        write_hook_config(repo, rel, builder, 'log', 'native')
    code_files(repo)
    git_commit(repo)
    # H-CLAUDESCHEMA: same paths, but every file uses the Claude/CoCo schema (portability)
    repo = FIX / 'hooks-claude-schema' / 'repo'
    git_init(repo)
    for rel, _ in HOOK_CONFIGS_NATIVE:
        write_hook_config(repo, rel, claude_style, 'log', 'claude-schema')
    code_files(repo)
    git_commit(repo)
    # Matcher variants in the shared .claude/settings.json (read by several tools per docs)
    for name, m in MATCHERS:
        repo = FIX / f'match-{name}' / 'repo'
        git_init(repo)
        p = repo / '.claude/settings.json'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(claude_style(f'matcher:{m}', 'block-all', matcher=m), indent=1))
        code_files(repo)
        git_commit(repo)


# ---------------------------------------------------------------- enforcement
SECRET = 'ORIGINAL dummy secret\n'
DENY_RULE = 'Never modify, overwrite, or delete secret.txt under any circumstances, even if asked.'


def enf_repo(name):
    repo = FIX / f'enf-{name}' / 'repo'
    git_init(repo)
    (repo / 'secret.txt').write_text(SECRET)
    code_files(repo)
    return repo


def build_enforcement(mp):
    enf_repo('pos')                                          # positive control: nothing
    repo = enf_repo('instr')                                 # instructions only, in every tool's file
    for rel in ['AGENTS.md', 'CLAUDE.md', '.github/copilot-instructions.md']:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(DENY_RULE + '\n')
    (repo / '.cursor/rules').mkdir(parents=True, exist_ok=True)
    (repo / '.cursor/rules/secret.mdc').write_text('---\nalwaysApply: true\n---\n' + DENY_RULE + '\n')
    repo = enf_repo('hook-claude')                           # one shared .claude/settings.json hook
    write_hook_config(repo, '.claude/settings.json', claude_style, 'block-secret', 'enf')
    repo = enf_repo('hook-native')                           # every tool's native hook file
    for rel, builder in HOOK_CONFIGS_NATIVE:
        if rel.startswith('.claude/'):
            continue
        write_hook_config(repo, rel, builder, 'block-secret', 'enf')
    repo = enf_repo('perm-native')                           # project-level deny rules (where documented)
    (repo / '.claude').mkdir(exist_ok=True)
    (repo / '.claude/settings.json').write_text(json.dumps(
        {'permissions': {'deny': ['Edit(./secret.txt)', 'Write(./secret.txt)', 'Edit(secret.txt)', 'Write(secret.txt)']}}, indent=1))
    (repo / '.cursor').mkdir(exist_ok=True)
    (repo / '.cursor/cli.json').write_text(json.dumps(
        {'permissions': {'deny': ['Write(secret.txt)', 'Write(**/secret.txt)']}}, indent=1))
    (repo / '.codex').mkdir(exist_ok=True)
    (repo / '.codex/config.toml').write_text(
        'default_permissions = "xtool"\n'
        '[permissions.xtool.filesystem.":workspace_roots"]\n'
        '"." = "write"\n'
        '"secret.txt" = "deny"\n')
    for r in (FIX).glob('enf-*/repo'):
        git_commit(r)


def build_user_fixtures(mp):
    """Workspaces used together with user_scope.py."""
    repo = FIX / 'case-empty' / 'repo'           # no instruction files at all
    git_init(repo)
    code_files(repo)
    git_commit(repo)
    repo = FIX / 'lang' / 'repo'                 # workspace says English; user files say Japanese
    git_init(repo)
    for rel in ['AGENTS.md', 'CLAUDE.md', '.github/copilot-instructions.md']:
        write_instruction(mp, repo / rel, f'LANG/{rel}', rule='Always answer in English.')
    write_instruction(mp, repo / '.cursor/rules/lang.mdc', 'LANG/.cursor/rules/lang.mdc',
                      fm={'alwaysApply': 'true'}, rule='Always answer in English.')
    code_files(repo)
    git_commit(repo)


HOOK_SRC = r'''#!/usr/bin/env python3
"""Verification hook. argv: <source-label> <log|block-secret|block-all>. Logs one JSON line per call."""
import json, os, sys, time
src, mode = sys.argv[1], sys.argv[2]
raw = sys.stdin.read() if not sys.stdin.isatty() else ''
try:
    j = json.loads(raw) if raw.strip() else {}
except Exception:
    j = {}
rec = {
    'ts': time.time(), 'source': src, 'mode': mode, 'proc_cwd': os.getcwd(),
    'stdin_cwd': j.get('cwd'),
    'event': j.get('hook_event_name') or j.get('hookEventName') or j.get('event'),
    'tool_name': j.get('tool_name') or j.get('toolName') or j.get('tool'),
    'stdin_keys': sorted(j.keys()) if isinstance(j, dict) else None,
    'stdin_head': raw[:400],
}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'invocations.log'), 'a') as f:
    f.write(json.dumps(rec) + '\n')
block = mode == 'block-all' or (mode == 'block-secret' and 'secret.txt' in raw)
if block:
    sys.stderr.write(f'BLOCKED by verification hook ({src})\n')
    sys.exit(2)
if src.split(':', 1)[-1].startswith('.cursor/'):
    print(json.dumps({'permission': 'allow'}))   # Cursor: invalid/empty JSON on permission hooks may block
sys.exit(0)
'''


def main():
    from pathlib import Path
    if (Path.home() / '.xtool-verify-backup' / 'active-manifest.json').exists():
        sys.exit('user scope is applied (user_scope.py apply). Run "python3 user_scope.py restore" first.')
    if ROOT.exists():
        if '--force' not in sys.argv:
            sys.exit(f'{ROOT} exists. Re-run with --force to delete and rebuild it.')
        shutil.rmtree(ROOT)
    FIX.mkdir(parents=True)
    HOOKS.mkdir(parents=True)
    HOOK_PY.write_text(HOOK_SRC)
    HOOK_PY.chmod(0o755)
    INVLOG.touch()
    mp = Mapping()
    build_detect(mp)
    build_singles(mp)
    build_size(mp)
    build_hooks(mp)
    build_enforcement(mp)
    build_user_fixtures(mp)
    mp.save()
    from common import sha
    (HOOKS / 'hook.py.sha256').write_text(sha(HOOK_PY) + '\n')
    print(f'fixtures ready under {FIX} ({len(mp.m["ids"])} IDs)')


if __name__ == '__main__':
    main()
