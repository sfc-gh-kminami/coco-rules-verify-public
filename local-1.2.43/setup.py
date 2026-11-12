import sys; sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from harness import *
V = '/tmp/coco-verify-local'
LOREM = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore. '
# TC-01
d = f'{V}/single-agents'; git(d); wfile(f'{d}/AGENTS.md', label='TC01-AGENTS')
# TC-02
for name, rel, fm in [('claude', 'CLAUDE.md', None), ('cortex', 'CORTEX.md', None), ('snowflake', 'SNOWFLAKE.md', None),
                      ('rules', 'RULES.md', None), ('cursorrules', '.cursorrules', None),
                      ('mdc', '.cursor/rules/x.mdc', {'description': '"test"'}), ('clauderules', '.claude/rules/x.md', {'description': '"test"'})]:
    d = f'{V}/single-{name}'; git(d); wfile(f'{d}/{rel}', fm=fm, label=f'TC02-{rel}')
# TC-04
d = f'{V}/single-case'; git(d)
for rel in ['agents.md', 'Claude.md', 'cortex.MD']: wfile(f'{d}/{rel}', label=f'TC04-{rel}')
# full layout
F = f'{V}/full'; R = f'{F}/repo'; git(R)
wfile(f'{F}/AGENTS.md', label='P-ABOVE')
for rel in ['AGENTS.md', 'CLAUDE.md', 'CORTEX.md', 'SNOWFLAKE.md', 'RULES.md', '.cursorrules']: wfile(f'{R}/{rel}', label=f'ROOT-{rel}')
wfile(f'{R}/.cursor/rules/always.mdc', fm={'description': '"always"'}, label='mdc-always')
wfile(f'{R}/.cursor/rules/sql.mdc', fm={'globs': '["**/*.sql"]'}, label='mdc-sql')
wfile(f'{R}/.cursor/rules/flag.mdc', fm={'alwaysApply': 'true'}, label='mdc-flag')
wfile(f'{R}/.claude/rules/plain.md', fm={'description': '"plain"'}, label='claude-plain')
wfile(f'{R}/.claude/rules/api.md', fm={'paths': '["src/api/**/*.ts"]'}, label='claude-api')
wfile(f'{R}/.github/instructions/sql.instructions.md', fm={'applyTo': '"**/*.sql"'}, label='gh-sql')
os.makedirs(f'{R}/src/api', exist_ok=True); open(f'{R}/src/api/handler.ts', 'w').write('export function handler() {\n  return 1;\n}\n')
os.makedirs(f'{R}/queries', exist_ok=True); open(f'{R}/queries/sample.sql', 'w').write('SELECT 42 AS answer;\n')
wfile(f'{R}/docs/AGENTS.md', label='P-DOCS'); open(f'{R}/docs/readme.txt', 'w').write('Plain readme.\n')
wfile(f'{R}/packages/pkg-a/AGENTS.md', label='P-PKG'); wfile(f'{R}/packages/pkg-a/src/AGENTS.md', label='P-PKGSRC')
open(f'{R}/src/dummy.txt', 'w').write('dummy\n')
subprocess.run(f'cd {R} && git add -A && git -c user.email=x@x -c user.name=x commit -qm init', shell=True)
# copies for tool cases
for c in ['tc16', 'tc17', 'tc18', 'tc21', 'tc08']:
    for i in range(5): shutil.copytree(F, f'{V}/full_{c}_{i}', symlinks=True)
# TC-14
def big(path, n, label):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    a, b = rid(), rid(); MAP['ids'][a] = {'path': path, 'label': label + '-start', 'kind': 'body'}; MAP['ids'][b] = {'path': path, 'label': label + '-end', 'kind': 'body'}
    filler = (LOREM * (n // len(LOREM) + 1))[:n]
    open(path, 'w').write(f'VERIFY-ID for this file: {a}\n{filler}\nVERIFY-ID (end) for this file: {b}\n')
d = f'{V}/size-a'; git(d); wfile(f'{d}/AGENTS.md', label='14a-AGENTS'); big(f'{d}/CLAUDE.md', 60000, '14a-CLAUDE'); big(f'{d}/CORTEX.md', 60000, '14a-CORTEX'); wfile(f'{d}/RULES.md', label='14a-RULES')
d = f'{V}/size-b'; git(d); big(f'{d}/AGENTS.md', 120000, '14b-AGENTS'); wfile(f'{d}/CLAUDE.md', label='14b-CLAUDE')
# TC-24 repo setting
d = f'{V}/single-team'; git(d); os.makedirs(f'{d}/.cortex'); json.dump({'chat.instructionFilePatterns': ['TEAM.md']}, open(f'{d}/.cortex/settings.json', 'w')); wfile(f'{d}/TEAM.md', label='TC24-TEAM')
# Enforcement
H = '/tmp/coco-hooks-local'; os.makedirs(H, exist_ok=True)
open(f'{H}/block-secret.sh', 'w').write('#!/bin/bash\nin=$(cat)\necho "$(date +%T) block-secret $(echo "$in" | jq -r .tool_name 2>/dev/null)" >> /tmp/coco-hooks-local/invocations.log\nif echo "$in" | jq -r \'.tool_input | .. | strings\' 2>/dev/null | grep -q secret.txt; then echo "BLOCKED by hook: secret.txt is protected" >&2; exit 2; fi\nexit 0\n')
open(f'{H}/block-all.sh', 'w').write('#!/bin/bash\nin=$(cat)\necho "$(date +%T) block-all $(echo "$in" | jq -r .tool_name 2>/dev/null)" >> /tmp/coco-hooks-local/invocations.log\necho "BLOCKED by block-all hook" >&2\nexit 2\n')
os.chmod(f'{H}/block-secret.sh', 0o755); os.chmod(f'{H}/block-all.sh', 0o755)
def hookcfg(m, s): return {'hooks': {'PreToolUse': [{'matcher': m, 'hooks': [{'type': 'command', 'command': f'{H}/{s}', 'timeout': 30}]}]}}
def enf(case, n, settings_rel=None, cfg=None, agents=None):
    for i in range(n):
        d = f'{V}/enf-{case}-{i}'; git(d); open(f'{d}/secret.txt', 'w').write('ORIGINAL dummy secret\n')
        if agents: open(f'{d}/AGENTS.md', 'w').write(agents)
        if settings_rel:
            os.makedirs(os.path.dirname(f'{d}/{settings_rel}'), exist_ok=True); json.dump(cfg, open(f'{d}/{settings_rel}', 'w'))
enf('pos', 3); enf('tc29', 5, agents='Never modify secret.txt under any circumstances.\n')
enf('tc30', 5, '.cortex/settings.json', hookcfg('edit|write', 'block-secret.sh'))
enf('tc27sf', 5, '.snowflake/cortex/settings.json', hookcfg('edit|write', 'block-secret.sh'))
enf('tc26', 5, '.claude/settings.json', hookcfg('edit|write', 'block-secret.sh'))
enf('tc28lo', 5, '.cortex/settings.json', hookcfg('bash', 'block-all.sh'))
enf('tc28up', 5, '.cortex/settings.json', hookcfg('Bash', 'block-all.sh'))
enf('tc31', 5)
save_map(); print('setup done', len(MAP['ids']))
