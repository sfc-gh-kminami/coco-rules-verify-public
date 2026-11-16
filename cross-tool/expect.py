"""Docs-based expectations per tool (as read on 2026-11-16; see REQUIREMENTS.md section 9).

Each function returns True / False / None.  None = the docs do not say (the report shows "記録のみ").
These are the *expected* values that measurements are compared against; they are not conclusions.
Edit this file when a tool's docs change, and keep the comments with the source of each rule.
"""
from fnmatch import fnmatch

TOOLS = ['cortex', 'claude', 'codex', 'cursor', 'copilot']
# IDE/manual tools are compared against the docs of their CLI/product family
FAMILY = {'cursor-ide': 'cursor', 'copilot-vscode': 'copilot', 'coco-desktop': 'cortex'}

SQL_TRIGGERS = {'T-MENTION-SQL', 'T-READ-SQL', 'T-CREATE-SQL'}

# Hypotheses (REQUIREMENTS.md section 5): tools it is about (None = all), case globs, and a regex that selects
# the rows (instruction-file label or hook config path) the hypothesis is about (None = whole case verdict).
HYP = {
    'X-01': (None, ['D-ALL-*', 'S-*'], None),
    'X-02': (['claude'], ['D-PAIR', 'D-ALL-W1'], r'AGENTS'),
    'X-03': (['codex'], ['D-ALL-W1', 'S-agents_*', 'D-SIZE-*'], r'AGENTS'),
    'X-04': (['cursor'], ['D-ALL-W1', 'S-cursor_*', 'T-*SQL'], r'\.cursor/rules'),
    'X-05': (['copilot'], ['D-ALL-W1', 'S-*', 'T-*SQL'], r'copilot|instructions|GEMINI|AGENTS|CLAUDE'),
    'X-06': (None, ['T-READ-DOCS', 'T-EDIT-TS'], r'^SUBDIR'),
    'X-07': (None, ['D-ALL-W1'], r'^ABOVE'),
    'X-08': (None, ['D-CASE'], None),
    'X-09': (None, ['D-SIZE-*'], None),
    'X-10': (None, ['H-NATIVE', 'H-CLAUDE-SCHEMA', 'E-HOOK-CLAUDE'], r'^\.claude/'),
    'X-11': (None, ['H-NATIVE'], r'^(?!\.claude/)'),
    'X-12': (None, ['H-CLAUDE-SCHEMA'], r'^(\.cursor/|\.github/)'),
    'X-13': (None, ['M-*'], None),
    'X-14': (None, ['E-HOOK-NATIVE', 'M-any-shell'], None),
    'X-15': (None, ['E-INSTR'], None),
    'X-16': (None, ['E-PERM-NATIVE'], None),
    'X-17': (None, ['E-FLAG'], None),
    'X-18': (None, ['U-*'], None),
    'X-19': (['cortex'], ['H-NATIVE'], r'^\.cortex/'),
}


def hyp_for(case_id, tool=None):
    out = []
    for h, (tools, globs, _) in HYP.items():
        if tool and tools and FAMILY.get(tool, tool) not in tools:
            continue
        if any(fnmatch(case_id, g) for g in globs):
            out.append(h)
    return out


# ---------------------------------------------------------------- instruction files
# loc: 'repo' (rel = path from git root), 'above' (outside git root), 'user' (rel = path from ~)
def expect_inject(tool, case, loc, rel, label='', present=frozenset()):
    """present: set of repo-relative paths of instruction files that exist in this case's fixture."""
    tool = FAMILY.get(tool, tool)
    cid = case['id']
    fn = globals().get(f'_inj_{tool}')
    return fn(cid, loc, rel, label, present) if fn else None


def _top(rel):
    """Instruction file location class inside the repo."""
    if rel.startswith('packages/pkg-a/src/'):
        return 'pkgsub'
    if rel.startswith('packages/pkg-a/'):
        return 'pkg'
    if rel.startswith(('docs/', 'src/api/')):
        return 'subdir'
    return 'root'


def _ws_includes(cid, where):
    """Is a directory class between workspace and git root (i.e. loaded at startup by root-ward walkers)?"""
    if where == 'root':
        return True
    if where == 'pkg':
        return cid in ('D-ALL-W2',)
    return False


def _inj_cortex(cid, loc, rel, label, present):
    # D-IF: names AGENTS/CLAUDE/CORTEX/SNOWFLAKE/RULES.md, .cursorrules (case-insensitive),
    # .cursor/rules/*.mdc and .claude/rules/*.md relative to git root; workspace root .. git root;
    # ~/.snowflake/cortex, ~/, ~/.claude, ~/.cursor/rules, ~/.claude/rules; same name -> workspace wins;
    # total ~100,000 chars, files that would exceed are skipped. .instructions.md only described as applyTo.
    names = {'agents.md', 'claude.md', 'cortex.md', 'snowflake.md', 'rules.md', '.cursorrules'}
    if loc == 'above':
        return False
    if loc == 'user':
        base = rel.split('/')[-1].lower()
        dirs = rel.rsplit('/', 1)[0] if '/' in rel else ''
        if dirs in ('.snowflake/cortex', '', '.claude') and base in names:
            if cid in ('U-ALL', 'U-LANG') and base in ('agents.md', 'claude.md'):
                return False          # same name exists in the workspace -> user version skipped
            return True
        if rel.startswith('.claude/rules/') and rel.endswith('.md'):
            return True
        if rel.startswith('.cursor/rules/') and rel.endswith('.mdc'):
            return True
        return False
    if cid == 'D-SIZE-120K' and rel in ('AGENTS.md', 'CLAUDE.md'):
        return False                  # each 120k file alone exceeds ~100k -> skipped
    where = _top(rel)
    base = rel.split('/')[-1].lower()
    if '/' not in rel or where in ('pkg', 'pkgsub', 'subdir'):
        if base in names:
            if where == 'subdir':
                return None if cid.startswith('T-') else False
            if where == 'pkgsub':
                return False
            return _ws_includes(cid, where)
        return False
    if rel.startswith('.cursor/rules/'):
        if not rel.endswith('.mdc'):
            return False
        if rel.endswith('sql.mdc'):
            return True if cid == 'T-MENTION-SQL' else (None if cid in SQL_TRIGGERS else False)
        return True
    if rel.startswith('.claude/rules/'):
        return None if rel.endswith('api.md') else True
    if rel.startswith('.github/instructions/'):
        return None                   # listed only in the format section, not in supported names
    return False


def _inj_claude(cid, loc, rel, label, present):
    # Claude Code memory: CLAUDE.md, .claude/CLAUDE.md, CLAUDE.local.md in cwd and every parent at launch;
    # subdirectory files on demand when reading/writing/editing there; .claude/rules/*.md (paths: = conditional);
    # AGENTS.md only when no CLAUDE.md/CLAUDE.local.md exists in or above cwd; user ~/.claude/CLAUDE.md, ~/.claude/rules.
    if loc == 'user':
        return rel in ('.claude/CLAUDE.md',) or rel.startswith('.claude/rules/')
    if cid == 'D-CASE':
        return None                   # case handling not stated
    claude_names = ('CLAUDE.md', 'CLAUDE.local.md', '.claude/CLAUDE.md')
    has_claude_root = any(p in present for p in claude_names)
    has_claude_pkg = 'packages/pkg-a/CLAUDE.md' in present and cid == 'D-ALL-W2'
    base = rel.split('/')[-1]
    if loc == 'above':
        return (not (has_claude_root or has_claude_pkg)) if base == 'AGENTS.md' else None
    where = _top(rel)
    if rel in claude_names or (base == 'CLAUDE.md' and where != 'root'):
        if where == 'root':
            return True
        if where == 'pkg':
            return cid == 'D-ALL-W2'
        if where == 'subdir':
            return cid == 'T-READ-DOCS' and rel.startswith('docs/')
        return False
    if base == 'AGENTS.md':
        if where == 'root':
            return not (has_claude_root or has_claude_pkg)
        if where == 'pkg':
            return cid == 'D-ALL-W2' and not (has_claude_root or has_claude_pkg)
        if where == 'subdir':
            return False if has_claude_root else (cid == 'T-EDIT-TS' and rel.startswith('src/api/'))
        return False
    if rel.startswith('.claude/rules/'):
        if rel.endswith('api.md'):
            return cid == 'T-EDIT-TS'
        return True
    return False


def _inj_codex(cid, loc, rel, label, present):
    # Codex AGENTS.md: ~/.codex/AGENTS.override.md or AGENTS.md; project root (git root) -> cwd, one file per dir:
    # AGENTS.override.md > AGENTS.md > project_doc_fallback_filenames; project_doc_max_bytes 32 KiB combined.
    if loc == 'user':
        return rel == '.codex/AGENTS.md'
    if loc == 'above':
        return False
    if cid == 'D-CASE':
        return None
    where = _top(rel)
    base = rel.split('/')[-1]
    if base not in ('AGENTS.md', 'AGENTS.override.md'):
        return False
    if where == 'root':
        if '/' in rel:
            return False
        if cid.startswith('D-SIZE'):
            return '(start)' in label     # 32 KiB limit: the start fits, the end does not
        if 'AGENTS.override.md' in present:
            return base == 'AGENTS.override.md'
        return True
    if where == 'pkg':
        return cid == 'D-ALL-W2' and base == 'AGENTS.md'
    return False


def _inj_cursor(cid, loc, rel, label, present):
    # Cursor rules: .cursor/rules/**/*.mdc only (alwaysApply / globs auto-attach / description = agent decides);
    # AGENTS.md at project root and subdirectories; CLI also reads CLAUDE.md at project root; user rules are UI only.
    if loc in ('user', 'above'):
        return False
    base = rel.split('/')[-1]
    where = _top(rel)
    if rel.startswith('.cursor/rules/'):
        if not rel.endswith('.mdc'):
            return False
        if rel.endswith('always.mdc') or rel.endswith('small.mdc'):
            return True
        if rel.endswith('sql.mdc'):
            return True if cid == 'T-MENTION-SQL' else (None if cid in SQL_TRIGGERS else False)
        return None                   # description-only: the agent decides
    if base == 'AGENTS.md':
        return True if where == 'root' or (where == 'pkg' and cid == 'D-ALL-W2') else None
    if base == 'CLAUDE.md' and '/' not in rel:
        return True
    if base == '.cursorrules':
        return None                   # legacy format; not described on the current rules page
    if cid == 'D-CASE':
        return None
    return False


def _inj_copilot(cid, loc, rel, label, present):
    # Copilot CLI: $HOME/.copilot/copilot-instructions.md, $HOME/.copilot/instructions/**/*.instructions.md;
    # repo .github/copilot-instructions.md, .github/instructions/**/*.instructions.md (applyTo);
    # AGENTS.md, CLAUDE.md, .claude/CLAUDE.md, GEMINI.md in repo root, cwd, dirs between, and dirs of files worked on.
    if loc == 'user':
        return rel in ('.copilot/copilot-instructions.md',) or rel.startswith('.copilot/instructions/')
    if loc == 'above':
        return False
    base = rel.split('/')[-1]
    where = _top(rel)
    if cid == 'D-CASE':
        return None
    if rel == '.github/copilot-instructions.md':
        return True
    if rel.startswith('.github/instructions/'):
        if rel.endswith('sql.instructions.md'):
            return None if cid in SQL_TRIGGERS else False
        return True
    if base in ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md') or rel == '.claude/CLAUDE.md':
        if where == 'root':
            return True
        if where == 'pkg':
            return cid == 'D-ALL-W2'
        if where == 'subdir':
            if cid == 'T-READ-DOCS' and rel.startswith('docs/'):
                return True
            if cid == 'T-EDIT-TS' and rel.startswith('src/api/'):
                return True
            return False
        return False
    return False


# ---------------------------------------------------------------- hooks (project config files)
HOOK_EXPECT = {
    # C-EXT: .cortex/settings.local.json > .cortex/settings.json > ~/.claude/settings.json > ~/.snowflake/cortex/hooks.json
    # Desktop hooks docs: <workspace>/.snowflake/cortex/settings.json or .cortex/settings.json. C-CL 1.1.47: no project .claude/settings.json
    'cortex': {'.cortex/settings.json', '.cortex/settings.local.json', '.snowflake/cortex/settings.json'},
    'claude': {'.claude/settings.json', '.claude/settings.local.json'},
    # Codex: <repo>/.codex/hooks.json and .codex/config.toml, only for trusted projects
    'codex': {'.codex/hooks.json', '.codex/config.toml'},
    # Cursor: .cursor/hooks.json + Claude settings via Third-Party Imports (default on)
    'cursor': {'.cursor/hooks.json', '.claude/settings.json', '.claude/settings.local.json'},
    # Copilot: .github/hooks/*.json, inline hooks in .github/copilot/settings(.local).json, and .claude/settings(.local).json
    'copilot': {'.github/hooks/xtool.json', '.github/copilot/settings.json', '.claude/settings.json', '.claude/settings.local.json'},
}
NATIVE_CLAUDE_LIKE = {'.cortex/settings.json', '.cortex/settings.local.json', '.snowflake/cortex/settings.json',
                      '.claude/settings.json', '.claude/settings.local.json', '.codex/hooks.json', '.codex/config.toml'}


def expect_hook(tool, case_id, rel):
    tool = FAMILY.get(tool, tool)
    exp = HOOK_EXPECT.get(tool)
    if exp is None:
        return None
    if tool == 'codex' and rel in exp:
        return None                   # depends on project trust (XTOOL_CODEX_TRUST_HOOKS)
    if case_id == 'H-CLAUDE-SCHEMA' and rel not in NATIVE_CLAUDE_LIKE:
        return False                  # wrong schema for that file
    return rel in exp


# ---------------------------------------------------------------- blocking (E-*, M-*): expected "file unchanged"
def expect_block(tool, case_id):
    tool = FAMILY.get(tool, tool)
    if case_id == 'E-POS':
        return False
    if case_id == 'E-INSTR':
        return None                   # compliance, not enforcement
    reads_claude_hooks = tool in ('claude', 'cursor', 'copilot')
    if case_id == 'E-HOOK-CLAUDE':
        return reads_claude_hooks
    if case_id == 'E-HOOK-NATIVE':
        return None if tool == 'codex' else True
    if case_id == 'E-PERM-NATIVE':
        return {'claude': True, 'cursor': True, 'codex': True, 'cortex': False, 'copilot': False}.get(tool)
    if case_id == 'E-FLAG':
        return {'cortex': True, 'claude': True, 'copilot': True, 'codex': True, 'cursor': None}.get(tool)
    if case_id.startswith('M-'):
        if not (reads_claude_hooks or tool == 'cortex'):
            return False
        m = {'M-lower-bash': 'bash', 'M-pascal-Bash': 'Bash', 'M-lower-shell': 'shell',
             'M-pascal-Shell': 'Shell', 'M-any-shell': 'Bash|bash|Shell|shell'}[case_id]
        names = {'cortex': ['bash'], 'claude': ['Bash'], 'copilot': ['Bash']}.get(tool)   # C-EXT / CC-HK / Copilot PascalCase
        if names is None:
            return None               # Cursor: name mapping of imported Claude hooks not stated
        return any(fnmatch(n, alt) for n in names for alt in m.split('|'))
    return None


def expect_japanese(tool, case_id):
    tool = FAMILY.get(tool, tool)
    if case_id == 'U-LANG':
        return False if tool == 'cortex' else None    # D-IF: workspace wins over user
    return None
