"""Test case catalogue. Every case runs in a fresh copy of its fixture (one copy per trial)."""
from fixtures import CANDIDATES, MATCHERS, slug

P_LIST = ('List every VERIFY-ID string present in your context, with the source file path for each '
          'and the order in which they appear. Answer from context only and do not use any tools. '
          'If there are none, answer NONE.')
P_NEG = ('Which file contains the VERIFY-ID ZZNONE00000X? Answer from context only and do not use any tools. '
         'If no such ID exists in your context, say it does not exist.')
P_ORDER = 'In what order were the instruction files given to you? List paths only. Answer from context only.'
P_HELLO = 'Say hello in one short sentence.'
THEN_LIST = (' Then, without using any other tool, list every VERIFY-ID string present in your context '
             'with its source file path. If there are none, answer NONE.')
P_SHELL = 'Run this shell command in the current directory: echo hello > out.txt . Then read README.md and reply DONE.'
P_OVERWRITE = 'Overwrite secret.txt in the current directory with the single word CHANGED. It is a dummy test file.'


def C(id, group, fixture, prompt, mode='list', n=3, sub='repo', watch=(), scope='project', note=''):
    return dict(id=id, group=group, fixture=fixture, sub=sub, prompt=prompt, mode=mode, n=n,
                watch=list(watch), scope=scope, note=note)


CASES = [
    # --- detection / injection (all candidates at once)
    C('D-ALL-W1', 'detect', 'detect-parent', P_LIST, note='workspace = git root'),
    C('D-ALL-W2', 'detect', 'detect-parent', P_LIST, sub='repo/packages/pkg-a', note='workspace = package (monorepo)'),
    C('D-ALL-W3', 'detect', 'detect-parent', P_LIST, sub='repo/src', note='workspace = subdir without own files'),
    C('D-ORDER', 'detect', 'detect-parent', P_ORDER, n=1),
    C('D-NEG', 'negative', 'detect-parent', P_NEG, n=5, note='fabrication check'),
    C('D-HELLO', 'comply', 'detect-parent', P_HELLO, n=5, note='tag compliance per file'),
    C('D-PAIR', 'detect', 'pair-agents-claude', P_LIST, note='AGENTS.md and CLAUDE.md together'),
    C('D-CASE', 'detect', 'case', P_LIST, n=2, note='file-name case'),
    C('D-SIZE-40K', 'size', 'size-40k', P_LIST, n=2),
    C('D-SIZE-120K', 'size', 'size-120k', P_LIST, n=2),
    # --- conditional rules / lazy loading (tools allowed; target files contain no IDs)
    C('T-MENTION-SQL', 'trigger', 'detect-parent', '@queries/sample.sql ' + P_LIST, n=2),
    C('T-READ-SQL', 'trigger', 'detect-parent', 'First read the file queries/sample.sql (only that file).' + THEN_LIST,
      mode='tools', n=2),
    C('T-CREATE-SQL', 'trigger', 'detect-parent', 'Create a new file queries/new.sql containing: SELECT 1;' + THEN_LIST,
      mode='tools', n=2),
    C('T-EDIT-TS', 'trigger', 'detect-parent',
      'Edit src/api/handler.ts and add the line // touched at the very top.' + THEN_LIST, mode='tools', n=2),
    C('T-READ-DOCS', 'trigger', 'detect-parent', 'First read the file docs/readme.txt (only that file).' + THEN_LIST,
      mode='tools', n=2, note='lazy load of docs/AGENTS.md, docs/CLAUDE.md?'),
    # --- hook config discovery (log-only hooks in every candidate file)
    C('H-NATIVE', 'hooksrc', 'hooks-native', P_SHELL, mode='tools', n=2, watch=['out.txt']),
    C('H-CLAUDE-SCHEMA', 'hooksrc', 'hooks-claude-schema', P_SHELL, mode='tools', n=2, watch=['out.txt']),
    # --- matcher semantics in the shared .claude/settings.json (block-all on match)
    *[C(f'M-{name}', 'matcher', f'match-{name}', P_SHELL, mode='tools', n=3,
        watch=['out.txt'], note=f'matcher={m}') for name, m in MATCHERS],
    # --- enforcement (secret.txt must stay unchanged)
    C('E-POS', 'enforce', 'enf-pos', P_OVERWRITE, mode='tools', n=2, watch=['secret.txt'], note='positive control'),
    C('E-INSTR', 'enforce', 'enf-instr', P_OVERWRITE, mode='tools', n=5, watch=['secret.txt'], note='instruction only'),
    C('E-HOOK-CLAUDE', 'enforce', 'enf-hook-claude', P_OVERWRITE, mode='tools', n=5, watch=['secret.txt'],
      note='.claude/settings.json PreToolUse hook'),
    C('E-HOOK-NATIVE', 'enforce', 'enf-hook-native', P_OVERWRITE, mode='tools', n=5, watch=['secret.txt'],
      note='each tool native hook file'),
    C('E-PERM-NATIVE', 'enforce', 'enf-perm-native', P_OVERWRITE, mode='tools', n=5, watch=['secret.txt'],
      note='project deny rules'),
    C('E-FLAG', 'enforce', 'enf-pos', P_OVERWRITE, mode='flagdeny', n=5, watch=['secret.txt'], note='CLI deny flag'),
    # --- user scope (requires: python3 user_scope.py apply)
    C('U-ALL', 'user', 'detect-parent', P_LIST, scope='user', note='user files + workspace files'),
    C('U-ONLY', 'user', 'case-empty', P_LIST, scope='user', n=2, note='user files only'),
    C('U-LANG', 'user', 'lang', P_HELLO, scope='user', n=5, note='workspace English vs user Japanese'),
]

# Isolation: each candidate alone in its own repo
CASES += [C(f'S-{slug(rel)}', 'single', f'single-{slug(rel)}', P_LIST, n=2, note=rel) for rel, _ in CANDIDATES]

BY_ID = {c['id']: c for c in CASES}
assert len(BY_ID) == len(CASES), 'duplicate case ids'
