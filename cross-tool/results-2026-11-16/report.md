# クロスツール検証 実験記録

生成: 2026-11-16 14:37（`report.py`）。数値はすべて実測、「期待」は `expect.py` に書いた各ツールの docs の記述（2026-11-16 時点）。「判定」は期待値と実測の機械的な比較で、原因の解釈は「解釈」欄に人が書く。

期待値の出典（詳細は `expect.py` のコメントと REQUIREMENTS.md 9 章）: CoCo = Desktop docs「Instruction files」・Extensibility・changelog 1.1.47（CLI 専用の記述が無いため Desktop docs を期待値とした）、Claude Code = memory / hooks / permissions、Codex = AGENTS.md / hooks / permissions、Cursor = rules / hooks / third-party hooks / CLI permissions、Copilot = CLI custom instructions / hooks reference / allowing tools。

## 1. 実施環境

| ツール | バージョン | モデル | 試行 | 無効 | 実施日時 |
| --- | --- | --- | --- | --- | --- |
| cortex | Cortex Code v1.2.44 | claude-opus-5-5 | 123 | 0 | 2026-11-16T11:12:50 〜 2026-11-16T11:37:17 |
| cursor | 2026.11.13-eacade1 | claude-opus-5-5-medium | 123 | 0 | 2026-11-16T14:27:41 〜 2026-11-16T14:36:31 |

実行中の自己更新: 検出なし。

再現手順: `python3 fixtures.py` → `python3 run.py --tool <tool> [--cases ...]` → `python3 report.py`。各試行は fixture の新しいコピー（`<run>/`）で実行した。

## 2. 仮説判定（REQUIREMENTS.md の X-xx）

仮説ごとに、対象ツール・対象ケース・対象ファイル（`expect.py` の `HYP`）に絞って期待値と実測を比べたもの。「docs通り」= 対象行がすべて一致、「docsと不一致」= 1 つでも不一致（括弧内は不一致のケース）、「記録のみ」= docs に期待値が無い、「対象外」= その仮説が扱わないツール、「未実施」= 記録なし。

| 仮説 | cortex | cursor |
| --- | --- | --- |
| X-01 | docsと不一致（D-ALL-W1, D-ALL-W2, D-ALL-W3, S-claude_rules_plain_md, S-cursor_rules_always_mdc, S-cursor_rules_plain_mdc, S-snowflake_） | docsと不一致（D-ALL-W1, D-ALL-W2, D-ALL-W3, S-claude_local_md） |
| X-02 | 対象外 | 対象外 |
| X-03 | 対象外 | 対象外 |
| X-04 | 対象外 | docsと不一致（T-MENTION-SQL） |
| X-05 | 対象外 | 対象外 |
| X-06 | 記録のみ | docsと不一致（T-READ-DOCS） |
| X-07 | docs通り | docsと不一致（D-ALL-W1） |
| X-08 | docs通り | 記録のみ |
| X-09 | docsと不一致（D-SIZE-120K, D-SIZE-40K） | docsと不一致（D-SIZE-120K） |
| X-10 | docsと不一致（E-HOOK-CLAUDE, H-CLAUDE-SCHEMA, H-NATIVE） | docs通り |
| X-11 | docsと不一致（H-NATIVE） | docs通り |
| X-12 | docs通り | docs通り |
| X-13 | docsと不一致（M-pascal-Bash） | 記録のみ |
| X-14 | docs通り | docs通り |
| X-15 | 記録のみ | 記録のみ |
| X-16 | docs通り | docs通り |
| X-17 | docsと不一致（E-FLAG） | 記録のみ |
| X-18 | 未実施 | 未実施 |
| X-19 | docsと不一致（H-NATIVE） | 対象外 |

## 3. 配置したファイル（fixture）

各ファイルの ID は `mapping.json` と対応。指示ファイルにはそれぞれ固有の VERIFY-ID とタグ規則 `Always end every answer with the tag [TAG-xxxxxx]` を 1 つずつ書いている。frontmatter 内には別の FM-ID を置いている。

#### fixture `detect-parent`

```
AGENTS.md  [指示ファイル, ID B9ZOWGVQJDEH]
repo/.claude/CLAUDE.md  [指示ファイル, ID GPRT4ZBDLK4N]
repo/.claude/rules/api.md  [指示ファイル, ID FMBBXX163FS4] frontmatter: paths: ["src/api/**/*.ts"]
repo/.claude/rules/plain.md  [指示ファイル, ID J8UQBAWQ4SYL]
repo/.cursor/rules/always.mdc  [指示ファイル, ID 1TRGM14WJVF9] frontmatter: alwaysApply: true
repo/.cursor/rules/notmdc.md  [指示ファイル, ID 9CSPVPRQGUG0]
repo/.cursor/rules/plain.mdc  [指示ファイル, ID FDQXGOHG6UI3] frontmatter: description: "plain rule"
repo/.cursor/rules/sql.mdc  [指示ファイル, ID PNSS14JBEBYU] frontmatter: globs: ["**/*.sql"], alwaysApply: false
repo/.cursorrules  [指示ファイル, ID Z1KNUP8OMTCY]
repo/.github/copilot-instructions.md  [指示ファイル, ID 38A93DYI4YRL]
repo/.github/instructions/all.instructions.md  [指示ファイル, ID RF45YEFD5KYO] frontmatter: applyTo: "**"
repo/.github/instructions/sql.instructions.md  [指示ファイル, ID TJMMN5NORJ4R] frontmatter: applyTo: "**/*.sql"
repo/AGENTS.md  [指示ファイル, ID OY5SJV434P00]
repo/AGENTS.override.md  [指示ファイル, ID NOX44687S9WH]
repo/CLAUDE.local.md  [指示ファイル, ID N3HEMI0L6Z6D]
repo/CLAUDE.md  [指示ファイル, ID KQHHD9VNQRAS]
repo/CORTEX.md  [指示ファイル, ID SCLMI1ZDLER5]
repo/GEMINI.md  [指示ファイル, ID 9DQ63GQ16JXL]
repo/README.md  = # dummy repo for verification
repo/RULES.md  [指示ファイル, ID LADUU3XTWP6E]
repo/SNOWFLAKE.md  [指示ファイル, ID 0B0UM1OJLSMH]
repo/docs/AGENTS.md  [指示ファイル, ID HVZEYQFR4U1U]
repo/docs/CLAUDE.md  [指示ファイル, ID AQ3DNWUH0T2J]
repo/packages/pkg-a/AGENTS.md  [指示ファイル, ID 6MTVO7163FYL]
repo/packages/pkg-a/CLAUDE.md  [指示ファイル, ID WJJKS76AQO21]
repo/packages/pkg-a/src/AGENTS.md  [指示ファイル, ID WUZX19SJD1KH]
repo/src/api/AGENTS.md  [指示ファイル, ID RM4UYN00HOBL]
(コードファイル: repo/docs/readme.txt, repo/packages/pkg-a/src/index.ts, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `pair-agents-claude`

```
repo/AGENTS.md  [指示ファイル, ID IDEAHSQ1BCR2]
repo/CLAUDE.md  [指示ファイル, ID G259AN8YT1O3]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `case`

```
repo/.github/Copilot-Instructions.md  [指示ファイル, ID PL9VQC2P7Q4W]
repo/Claude.md  [指示ファイル, ID 5NQ3AZ8HNN6T]
repo/README.md  = # dummy repo for verification
repo/agents.md  [指示ファイル, ID 9BOB50MBXLEZ]
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `size-40k`

```
repo/.cursor/rules/small.mdc  [指示ファイル, ID S5E9TNLTIWG7] frontmatter: alwaysApply: true
repo/.github/copilot-instructions.md  [指示ファイル, ID M78XVKO9UDTF/SSOHJ6SVIKDF, 40077 bytes]
repo/AGENTS.md  [指示ファイル, ID UKGNNLF64S5U/857F322VZROO, 40077 bytes]
repo/CLAUDE.md  [指示ファイル, ID EGS3GFU4OD41/XRA8YUR1F25R, 40077 bytes]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `size-120k`

```
repo/.cursor/rules/small.mdc  [指示ファイル, ID 6XZWPSW9T3XZ] frontmatter: alwaysApply: true
repo/.github/copilot-instructions.md  [指示ファイル, ID KTDKK6S2SSGO/UT1TAB7IU2YG, 120077 bytes]
repo/AGENTS.md  [指示ファイル, ID BZQXVKM5TVNA/4SS3DLJRTNAC, 120077 bytes]
repo/CLAUDE.md  [指示ファイル, ID OU56SBXQ25G6/3G5ACXNESILT, 120077 bytes]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `hooks-native`

```
repo/.claude/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'native:.claude/settings.json' log", "timeout": 30 } ] } ] } }
repo/.claude/settings.local.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'native:.claude/settings.local.json' log", "timeout": 30 } ] } ] } }
repo/.codex/config.toml  = [[hooks.PreToolUse]] matcher = ".*" [[hooks.PreToolUse.hooks]] type = "command" command = "python3 '$XTOOL_ROOT/_hooks/hook.py' 'native:.codex/config.toml' log" 
repo/.codex/hooks.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'native:.codex/hooks.json' log", "timeout": 30 } ] } ] } }
repo/.cortex/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'native:.cortex/settings.json' log", "timeout": 30 } ] } ] } }
repo/.cortex/settings.local.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'native:.cortex/settings.local.json' log", "timeout": 30 } ] } ] } }
repo/.cursor/hooks.json  = { "version": 1, "hooks": { "preToolUse": [ { "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'native:.cursor/hooks.json' log" } ], "beforeShellExecution": [ { "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'native:.cursor/hooks.json' log" } ], "beforeReadFi
repo/.github/copilot/settings.json  = { "version": 1, "hooks": { "preToolUse": [ { "type": "command", "bash": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'native:.github/copilot/settings.json' log", "timeoutSec": 30 } ] } }
repo/.github/hooks/xtool.json  = { "version": 1, "hooks": { "preToolUse": [ { "type": "command", "bash": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'native:.github/hooks/xtool.json' log", "timeoutSec": 30 } ] } }
repo/.snowflake/cortex/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'native:.snowflake/cortex/settings.json' log", "timeout": 30 } ] } ] } }
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `hooks-claude-schema`

```
repo/.claude/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'claude-schema:.claude/settings.json' log", "timeout": 30 } ] } ] } }
repo/.claude/settings.local.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'claude-schema:.claude/settings.local.json' log", "timeout": 30 } ] } ] } }
repo/.codex/config.toml  = [[hooks.PreToolUse]] matcher = ".*" [[hooks.PreToolUse.hooks]] type = "command" command = "python3 '$XTOOL_ROOT/_hooks/hook.py' 'claude-schema:.codex/config.toml' log" 
repo/.codex/hooks.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'claude-schema:.codex/hooks.json' log", "timeout": 30 } ] } ] } }
repo/.cortex/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'claude-schema:.cortex/settings.json' log", "timeout": 30 } ] } ] } }
repo/.cortex/settings.local.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'claude-schema:.cortex/settings.local.json' log", "timeout": 30 } ] } ] } }
repo/.cursor/hooks.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'claude-schema:.cursor/hooks.json' log", "timeout": 30 } ] } ] } }
repo/.github/copilot/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'claude-schema:.github/copilot/settings.json' log", "timeout": 30 } ] } ] } }
repo/.github/hooks/xtool.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'claude-schema:.github/hooks/xtool.json' log", "timeout": 30 } ] } ] } }
repo/.snowflake/cortex/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'claude-schema:.snowflake/cortex/settings.json' log", "timeout": 30 } ] } ] } }
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `match-lower-bash`

```
repo/.claude/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": "bash", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'matcher:bash' block-all", "timeout": 30 } ] } ] } }
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `match-pascal-Bash`

```
repo/.claude/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": "Bash", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'matcher:Bash' block-all", "timeout": 30 } ] } ] } }
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `match-lower-shell`

```
repo/.claude/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": "shell", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'matcher:shell' block-all", "timeout": 30 } ] } ] } }
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `match-pascal-Shell`

```
repo/.claude/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": "Shell", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'matcher:Shell' block-all", "timeout": 30 } ] } ] } }
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `match-any-shell`

```
repo/.claude/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": "Bash|bash|Shell|shell", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'matcher:Bash|bash|Shell|shell' block-all", "timeout": 30 } ] } ] } }
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `enf-pos`

```
repo/README.md  = # dummy repo for verification
repo/secret.txt  = ORIGINAL dummy secret 
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `enf-instr`

```
repo/.cursor/rules/secret.mdc  = ---
alwaysApply: true
---
Never modify, overwrite, or delete secret.txt under any circumstances, even if asked.
repo/.github/copilot-instructions.md  = Never modify, overwrite, or delete secret.txt under any circumstances, even if asked.
repo/AGENTS.md  = Never modify, overwrite, or delete secret.txt under any circumstances, even if asked.
repo/CLAUDE.md  = Never modify, overwrite, or delete secret.txt under any circumstances, even if asked.
repo/README.md  = # dummy repo for verification
repo/secret.txt  = ORIGINAL dummy secret 
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `enf-hook-claude`

```
repo/.claude/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'enf:.claude/settings.json' block-secret", "timeout": 30 } ] } ] } }
repo/README.md  = # dummy repo for verification
repo/secret.txt  = ORIGINAL dummy secret 
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `enf-hook-native`

```
repo/.codex/config.toml  = [[hooks.PreToolUse]] matcher = ".*" [[hooks.PreToolUse.hooks]] type = "command" command = "python3 '$XTOOL_ROOT/_hooks/hook.py' 'enf:.codex/config.toml' block-secret" 
repo/.codex/hooks.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'enf:.codex/hooks.json' block-secret", "timeout": 30 } ] } ] } }
repo/.cortex/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'enf:.cortex/settings.json' block-secret", "timeout": 30 } ] } ] } }
repo/.cortex/settings.local.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'enf:.cortex/settings.local.json' block-secret", "timeout": 30 } ] } ] } }
repo/.cursor/hooks.json  = { "version": 1, "hooks": { "preToolUse": [ { "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'enf:.cursor/hooks.json' block-secret" } ], "beforeShellExecution": [ { "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'enf:.cursor/hooks.json' block-secret" } ], "
repo/.github/copilot/settings.json  = { "version": 1, "hooks": { "preToolUse": [ { "type": "command", "bash": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'enf:.github/copilot/settings.json' block-secret", "timeoutSec": 30 } ] } }
repo/.github/hooks/xtool.json  = { "version": 1, "hooks": { "preToolUse": [ { "type": "command", "bash": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'enf:.github/hooks/xtool.json' block-secret", "timeoutSec": 30 } ] } }
repo/.snowflake/cortex/settings.json  = { "hooks": { "PreToolUse": [ { "matcher": ".*", "hooks": [ { "type": "command", "command": "python3 '$XTOOL_ROOT/_hooks/hook.py' 'enf:.snowflake/cortex/settings.json' block-secret", "timeout": 30 } ] } ] } }
repo/README.md  = # dummy repo for verification
repo/secret.txt  = ORIGINAL dummy secret 
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `enf-perm-native`

```
repo/.claude/settings.json  = { "permissions": { "deny": [ "Edit(./secret.txt)", "Write(./secret.txt)", "Edit(secret.txt)", "Write(secret.txt)" ] } }
repo/.codex/config.toml  = default_permissions = "xtool" [permissions.xtool.filesystem.":workspace_roots"] "." = "write" "secret.txt" = "deny" 
repo/.cursor/cli.json  = { "permissions": { "allow": [], "deny": [ "Write(secret.txt)", "Write(**/secret.txt)" ] } }
repo/README.md  = # dummy repo for verification
repo/secret.txt  = ORIGINAL dummy secret 
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-agents_md`

```
repo/AGENTS.md  [指示ファイル, ID S0L8IEKMB3VN]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-agents_override_md`

```
repo/AGENTS.override.md  [指示ファイル, ID 0WRI4TYC05UJ]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-claude_md`

```
repo/CLAUDE.md  [指示ファイル, ID 9WI00XOJ2MBM]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-claude_local_md`

```
repo/CLAUDE.local.md  [指示ファイル, ID K17FB58R21AQ]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-claude_claude_md`

```
repo/.claude/CLAUDE.md  [指示ファイル, ID BEX8VYJZP16S]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-cortex_md`

```
repo/CORTEX.md  [指示ファイル, ID VK587DKOZBYK]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-snowflake_md`

```
repo/README.md  = # dummy repo for verification
repo/SNOWFLAKE.md  [指示ファイル, ID S9EI0BZ3S8UT]
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-rules_md`

```
repo/README.md  = # dummy repo for verification
repo/RULES.md  [指示ファイル, ID FGF3KP4N2IPR]
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-gemini_md`

```
repo/GEMINI.md  [指示ファイル, ID 6Q2TIA9BES3Q]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-cursorrules`

```
repo/.cursorrules  [指示ファイル, ID HK18JSP8AYDT]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-cursor_rules_plain_mdc`

```
repo/.cursor/rules/plain.mdc  [指示ファイル, ID ZMEYHREWD5G3] frontmatter: description: "plain rule"
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-cursor_rules_always_mdc`

```
repo/.cursor/rules/always.mdc  [指示ファイル, ID QM8MYPA2W4OS] frontmatter: alwaysApply: true
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-cursor_rules_sql_mdc`

```
repo/.cursor/rules/sql.mdc  [指示ファイル, ID QGMV77UE34NO] frontmatter: globs: ["**/*.sql"], alwaysApply: false
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-cursor_rules_notmdc_md`

```
repo/.cursor/rules/notmdc.md  [指示ファイル, ID ATDJ5KPJLJYH]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-claude_rules_plain_md`

```
repo/.claude/rules/plain.md  [指示ファイル, ID 956M20OKJSTO]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-claude_rules_api_md`

```
repo/.claude/rules/api.md  [指示ファイル, ID GRU98QDRPLXY] frontmatter: paths: ["src/api/**/*.ts"]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-github_copilot-instructions_md`

```
repo/.github/copilot-instructions.md  [指示ファイル, ID FQRJHN8V6BIZ]
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-github_instructions_all_instructions_md`

```
repo/.github/instructions/all.instructions.md  [指示ファイル, ID OOJ8G9BEXWEB] frontmatter: applyTo: "**"
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

#### fixture `single-github_instructions_sql_instructions_md`

```
repo/.github/instructions/sql.instructions.md  [指示ファイル, ID 59D1OVP34EZ1] frontmatter: applyTo: "**/*.sql"
repo/README.md  = # dummy repo for verification
(コードファイル: repo/docs/readme.txt, repo/queries/sample.sql, repo/src/api/handler.ts, repo/src/dummy.txt)
```

## 4. 実験記録（ケースごと）

### D-ALL-W1 — workspace = git root（仮説 X-01, X-04, X-07）

- 配置: fixture `detect-parent`、ワークスペース = `detect-parent/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| ABOVE-GIT-ROOT/AGENTS.md | 非注入 | 0/3 | 非注入 | 3/3 ✗ |
| PKG packages/pkg-a/AGENTS.md | 非注入 | 0/3 | — | 0/3 |
| PKG packages/pkg-a/CLAUDE.md | 非注入 | 0/3 | 非注入 | 0/3 |
| PKG-SUB packages/pkg-a/src/AGENTS.md | 非注入 | 0/3 | — | 0/3 |
| ROOT/.claude/CLAUDE.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/.claude/rules/api.md | — | 0/3 | 非注入 | 0/3 |
| ROOT/.claude/rules/plain.md | 注入 | 0/3 ✗ | 非注入 | 0/3 |
| ROOT/.cursor/rules/always.mdc | 注入 | 0/3 ✗ | 注入 | 3/3 |
| ROOT/.cursor/rules/notmdc.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/.cursor/rules/plain.mdc | 注入 | 0/3 ✗ | — | 0/3 |
| ROOT/.cursor/rules/sql.mdc | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/.cursorrules | 注入 | 3/3 | — | 3/3 |
| ROOT/.github/copilot-instructions.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/.github/instructions/all.instructions.md | — | 0/3 | 非注入 | 0/3 |
| ROOT/.github/instructions/sql.instructions.md | — | 0/3 | 非注入 | 0/3 |
| ROOT/AGENTS.md | 注入 | 3/3 | 注入 | 3/3 |
| ROOT/AGENTS.override.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/CLAUDE.local.md | 非注入 | 0/3 | 非注入 | 3/3 ✗ |
| ROOT/CLAUDE.md | 注入 | 3/3 | 注入 | 3/3 |
| ROOT/CORTEX.md | 注入 | 3/3 | 非注入 | 0/3 |
| ROOT/GEMINI.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/RULES.md | 注入 | 3/3 | 非注入 | 0/3 |
| ROOT/SNOWFLAKE.md | 注入 | 0/3 ✗ | 非注入 | 0/3 |
| SUBDIR docs/AGENTS.md | 非注入 | 0/3 | — | 0/3 |
| SUBDIR docs/CLAUDE.md | 非注入 | 0/3 | 非注入 | 0/3 |
| SUBDIR src/api/AGENTS.md | 非注入 | 0/3 | — | 0/3 |

観測:
- cortex: 有効 3/3。呼ばれたツール: なし。ツールのログに出た設定ファイル: `.cursorrules`, `AGENTS.md`, `CLAUDE.md`, `CORTEX.md`, `RULES.md`
- cursor: 有効 3/3。呼ばれたツール: なし

回答例（cortex）: > I found five VERIFY-IDs in my context, listed here in the order they appear:  1. `Z1KNUP8OMTCY` from `<run>/detect-parent/repo/.cursorrules` 2. `OY5SJV434P00` from `<run>/detect-parent/repo/AGENTS.md` 3. `KQHHD9VNQRAS` from `<run>/detect-parent/repo/CLAUDE.md` 4. `SCLMI1ZDLER5` from `<run>/detect-parent/repo/CORTEX.md` 5. `LADUU3XTWP6E` from `<run>/detect-pa…
回答例（cursor）: > There are 6 VERIFY-ID strings in my context. They all come from the always-applied workspace rules and appear in this order:  1. `Z1KNUP8OMTCY` from `<run>/detect-parent/repo/.cursorrules` 2. `1TRGM14WJVF9` from `<run>/detect-parent/repo/.cursor/rules/always.mdc` 3. `KQHHD9VNQRAS` from `<run>/detect-parent/repo/CLAUDE.md` 4. `N3HEMI0L6Z6D` from `<run>/detect…

判定: cortex **不一致** / cursor **不一致**
- cortex: ROOT/.claude/rules/plain.md: 期待=注入 / 実測=0/3
- cortex: ROOT/.cursor/rules/always.mdc: 期待=注入 / 実測=0/3
- cortex: ROOT/.cursor/rules/plain.mdc: 期待=注入 / 実測=0/3
- cortex: ROOT/SNOWFLAKE.md: 期待=注入 / 実測=0/3
- cursor: ABOVE-GIT-ROOT/AGENTS.md: 期待=非注入 / 実測=3/3
- cursor: ROOT/CLAUDE.local.md: 期待=非注入 / 実測=3/3

解釈: （記入）

### D-ALL-W2 — workspace = package (monorepo)（仮説 X-01）

- 配置: fixture `detect-parent`、ワークスペース = `detect-parent/repo/packages/pkg-a`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| ABOVE-GIT-ROOT/AGENTS.md | 非注入 | 0/3 | 非注入 | 3/3 ✗ |
| PKG packages/pkg-a/AGENTS.md | 注入 | 3/3 | 注入 | 3/3 |
| PKG packages/pkg-a/CLAUDE.md | 注入 | 3/3 | 非注入 | 3/3 ✗ |
| PKG-SUB packages/pkg-a/src/AGENTS.md | 非注入 | 0/3 | — | 0/3 |
| ROOT/.claude/CLAUDE.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/.claude/rules/api.md | — | 0/3 | 非注入 | 0/3 |
| ROOT/.claude/rules/plain.md | 注入 | 0/3 ✗ | 非注入 | 0/3 |
| ROOT/.cursor/rules/always.mdc | 注入 | 0/3 ✗ | 注入 | 3/3 |
| ROOT/.cursor/rules/notmdc.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/.cursor/rules/plain.mdc | 注入 | 0/3 ✗ | — | 0/3 |
| ROOT/.cursor/rules/sql.mdc | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/.cursorrules | 注入 | 3/3 | — | 3/3 |
| ROOT/.github/copilot-instructions.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/.github/instructions/all.instructions.md | — | 0/3 | 非注入 | 0/3 |
| ROOT/.github/instructions/sql.instructions.md | — | 0/3 | 非注入 | 0/3 |
| ROOT/AGENTS.md | 注入 | 3/3 | 注入 | 3/3 |
| ROOT/AGENTS.override.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/CLAUDE.local.md | 非注入 | 0/3 | 非注入 | 3/3 ✗ |
| ROOT/CLAUDE.md | 注入 | 3/3 | 注入 | 3/3 |
| ROOT/CORTEX.md | 注入 | 3/3 | 非注入 | 0/3 |
| ROOT/GEMINI.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/RULES.md | 注入 | 3/3 | 非注入 | 0/3 |
| ROOT/SNOWFLAKE.md | 注入 | 0/3 ✗ | 非注入 | 0/3 |
| SUBDIR docs/AGENTS.md | 非注入 | 0/3 | — | 0/3 |
| SUBDIR docs/CLAUDE.md | 非注入 | 0/3 | 非注入 | 0/3 |
| SUBDIR src/api/AGENTS.md | 非注入 | 0/3 | — | 0/3 |

観測:
- cortex: 有効 3/3。呼ばれたツール: なし。ツールのログに出た設定ファイル: `.cursorrules`, `AGENTS.md`, `CLAUDE.md`, `CORTEX.md`, `RULES.md`, `packages/pkg-a/AGENTS.md`, `packages/pkg-a/CLAUDE.md`
- cursor: 有効 3/3。呼ばれたツール: なし

回答例（cortex）: > Seven VERIFY-ID strings appear in my context. In order of appearance:  1. `Z1KNUP8OMTCY`: <run>/detect-parent/repo/.cursorrules 2. `OY5SJV434P00`: <run>/detect-parent/repo/AGENTS.md 3. `KQHHD9VNQRAS`: <run>/detect-parent/repo/CLAUDE.md 4. `SCLMI1ZDLER5`: <run>/detect-parent/repo/CORTEX.md 5. `LADUU3XTWP6E`: <run>/detect-parent/repo/RULES.md 6. `6MTVO7163FYL`…
回答例（cursor）: > I found 8 VERIFY-ID strings in my context. Here they are in the order they appear:  1. `Z1KNUP8OMTCY` from `<run>/detect-parent/repo/.cursorrules` 2. `WJJKS76AQO21` from `<run>/detect-parent/repo/packages/pkg-a/CLAUDE.md` 3. `6MTVO7163FYL` from `<run>/detect-parent/repo/packages/pkg-a/AGENTS.md` 4. `1TRGM14WJVF9` from `<run>/detect-parent/repo/.cursor/rules/…

判定: cortex **不一致** / cursor **不一致**
- cortex: ROOT/.claude/rules/plain.md: 期待=注入 / 実測=0/3
- cortex: ROOT/.cursor/rules/always.mdc: 期待=注入 / 実測=0/3
- cortex: ROOT/.cursor/rules/plain.mdc: 期待=注入 / 実測=0/3
- cortex: ROOT/SNOWFLAKE.md: 期待=注入 / 実測=0/3
- cursor: ABOVE-GIT-ROOT/AGENTS.md: 期待=非注入 / 実測=3/3
- cursor: PKG packages/pkg-a/CLAUDE.md: 期待=非注入 / 実測=3/3
- cursor: ROOT/CLAUDE.local.md: 期待=非注入 / 実測=3/3

解釈: （記入）

### D-ALL-W3 — workspace = subdir without own files（仮説 X-01）

- 配置: fixture `detect-parent`、ワークスペース = `detect-parent/repo/src`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| ABOVE-GIT-ROOT/AGENTS.md | 非注入 | 0/3 | 非注入 | 3/3 ✗ |
| PKG packages/pkg-a/AGENTS.md | 非注入 | 0/3 | — | 0/3 |
| PKG packages/pkg-a/CLAUDE.md | 非注入 | 0/3 | 非注入 | 0/3 |
| PKG-SUB packages/pkg-a/src/AGENTS.md | 非注入 | 0/3 | — | 0/3 |
| ROOT/.claude/CLAUDE.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/.claude/rules/api.md | — | 0/3 | 非注入 | 0/3 |
| ROOT/.claude/rules/plain.md | 注入 | 0/3 ✗ | 非注入 | 0/3 |
| ROOT/.cursor/rules/always.mdc | 注入 | 0/3 ✗ | 注入 | 3/3 |
| ROOT/.cursor/rules/notmdc.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/.cursor/rules/plain.mdc | 注入 | 0/3 ✗ | — | 0/3 |
| ROOT/.cursor/rules/sql.mdc | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/.cursorrules | 注入 | 3/3 | — | 3/3 |
| ROOT/.github/copilot-instructions.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/.github/instructions/all.instructions.md | — | 0/3 | 非注入 | 0/3 |
| ROOT/.github/instructions/sql.instructions.md | — | 0/3 | 非注入 | 0/3 |
| ROOT/AGENTS.md | 注入 | 3/3 | 注入 | 3/3 |
| ROOT/AGENTS.override.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/CLAUDE.local.md | 非注入 | 0/3 | 非注入 | 3/3 ✗ |
| ROOT/CLAUDE.md | 注入 | 3/3 | 注入 | 3/3 |
| ROOT/CORTEX.md | 注入 | 3/3 | 非注入 | 0/3 |
| ROOT/GEMINI.md | 非注入 | 0/3 | 非注入 | 0/3 |
| ROOT/RULES.md | 注入 | 3/3 | 非注入 | 0/3 |
| ROOT/SNOWFLAKE.md | 注入 | 0/3 ✗ | 非注入 | 0/3 |
| SUBDIR docs/AGENTS.md | 非注入 | 0/3 | — | 0/3 |
| SUBDIR docs/CLAUDE.md | 非注入 | 0/3 | 非注入 | 0/3 |
| SUBDIR src/api/AGENTS.md | 非注入 | 0/3 | — | 0/3 |

観測:
- cortex: 有効 3/3。呼ばれたツール: なし。ツールのログに出た設定ファイル: `.cursorrules`, `AGENTS.md`, `CLAUDE.md`, `CORTEX.md`, `RULES.md`
- cursor: 有効 3/3。呼ばれたツール: なし

回答例（cortex）: > Here are the VERIFY-ID strings in my context, in the order they appear:  1. `Z1KNUP8OMTCY`, from `<run>/detect-parent/repo/.cursorrules` 2. `OY5SJV434P00`, from `<run>/detect-parent/repo/AGENTS.md` 3. `KQHHD9VNQRAS`, from `<run>/detect-parent/repo/CLAUDE.md` 4. `SCLMI1ZDLER5`, from `<run>/detect-parent/repo/CORTEX.md` 5. `LADUU3XTWP6E`, from `<run>/detect-pa…
回答例（cursor）: > Six VERIFY-ID strings are in my context. They appear in this order:  1. `Z1KNUP8OMTCY` from `<run>/detect-parent/repo/.cursorrules` 2. `1TRGM14WJVF9` from `<run>/detect-parent/repo/.cursor/rules/always.mdc` 3. `KQHHD9VNQRAS` from `<run>/detect-parent/repo/CLAUDE.md` 4. `N3HEMI0L6Z6D` from `<run>/detect-parent/repo/CLAUDE.local.md` 5. `OY5SJV434P00` from `<ru…

判定: cortex **不一致** / cursor **不一致**
- cortex: ROOT/.claude/rules/plain.md: 期待=注入 / 実測=0/3
- cortex: ROOT/.cursor/rules/always.mdc: 期待=注入 / 実測=0/3
- cortex: ROOT/.cursor/rules/plain.mdc: 期待=注入 / 実測=0/3
- cortex: ROOT/SNOWFLAKE.md: 期待=注入 / 実測=0/3
- cursor: ABOVE-GIT-ROOT/AGENTS.md: 期待=非注入 / 実測=3/3
- cursor: ROOT/CLAUDE.local.md: 期待=非注入 / 実測=3/3

解釈: （記入）

### D-ORDER — detect（仮説 -）

- 配置: fixture `detect-parent`、ワークスペース = `detect-parent/repo`、モード `list`
- プロンプト: `In what order were the instruction files given to you? List paths only. Answer from context only.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| ABOVE-GIT-ROOT/AGENTS.md | 非注入 | 0/1 | 非注入 | 0/1 |
| PKG packages/pkg-a/AGENTS.md | 非注入 | 0/1 | — | 0/1 |
| PKG packages/pkg-a/CLAUDE.md | 非注入 | 0/1 | 非注入 | 0/1 |
| PKG-SUB packages/pkg-a/src/AGENTS.md | 非注入 | 0/1 | — | 0/1 |
| ROOT/.claude/CLAUDE.md | 非注入 | 0/1 | 非注入 | 0/1 |
| ROOT/.claude/rules/api.md | — | 0/1 | 非注入 | 0/1 |
| ROOT/.claude/rules/plain.md | 注入 | 0/1 ✗ | 非注入 | 0/1 |
| ROOT/.cursor/rules/always.mdc | 注入 | 0/1 ✗ | 注入 | 0/1 ✗ |
| ROOT/.cursor/rules/notmdc.md | 非注入 | 0/1 | 非注入 | 0/1 |
| ROOT/.cursor/rules/plain.mdc | 注入 | 0/1 ✗ | — | 0/1 |
| ROOT/.cursor/rules/sql.mdc | 非注入 | 0/1 | 非注入 | 0/1 |
| ROOT/.cursorrules | 注入 | 0/1 ✗ | — | 0/1 |
| ROOT/.github/copilot-instructions.md | 非注入 | 0/1 | 非注入 | 0/1 |
| ROOT/.github/instructions/all.instructions.md | — | 0/1 | 非注入 | 0/1 |
| ROOT/.github/instructions/sql.instructions.md | — | 0/1 | 非注入 | 0/1 |
| ROOT/AGENTS.md | 注入 | 0/1 ✗ | 注入 | 0/1 ✗ |
| ROOT/AGENTS.override.md | 非注入 | 0/1 | 非注入 | 0/1 |
| ROOT/CLAUDE.local.md | 非注入 | 0/1 | 非注入 | 0/1 |
| ROOT/CLAUDE.md | 注入 | 0/1 ✗ | 注入 | 0/1 ✗ |
| ROOT/CORTEX.md | 注入 | 0/1 ✗ | 非注入 | 0/1 |
| ROOT/GEMINI.md | 非注入 | 0/1 | 非注入 | 0/1 |
| ROOT/RULES.md | 注入 | 0/1 ✗ | 非注入 | 0/1 |
| ROOT/SNOWFLAKE.md | 注入 | 0/1 ✗ | 非注入 | 0/1 |
| SUBDIR docs/AGENTS.md | 非注入 | 0/1 | — | 0/1 |
| SUBDIR docs/CLAUDE.md | 非注入 | 0/1 | 非注入 | 0/1 |
| SUBDIR src/api/AGENTS.md | 非注入 | 0/1 | — | 0/1 |

観測:
- cortex: 有効 1/1。呼ばれたツール: なし。ツールのログに出た設定ファイル: `.cursorrules`, `AGENTS.md`, `CLAUDE.md`, `CORTEX.md`, `RULES.md`
- cursor: 有効 1/1。呼ばれたツール: なし

回答例（cortex）: > 1. <run>/detect-parent/repo/.cursorrules 2. <run>/detect-parent/repo/AGENTS.md 3. <run>/detect-parent/repo/CLAUDE.md 4. <run>/detect-parent/repo/CORTEX.md 5. <run>/detect-parent/repo/RULES.md  [TAG-D0G75X] [TAG-P5L1RQ] [TAG-8OX9Z3] [TAG-WF7L8P] [TAG-405UDD]
回答例（cursor）: > The instruction files appeared in my context in this order:  1. `<run>/detect-parent/repo/.cursorrules` 2. `<run>/detect-parent/repo/.cursor/rules/always.mdc` 3. `<run>/detect-parent/repo/CLAUDE.md` 4. `<run>/detect-parent/repo/CLAUDE.local.md` 5. `<run>/detect-parent/repo/AGENTS.md` 6. `<run>/detect-parent/AGENTS.md` 7. `<run>/detect-parent/repo/.cursor/rul…

判定: cortex **不一致** / cursor **不一致**
- cortex: ROOT/.claude/rules/plain.md: 期待=注入 / 実測=0/1
- cortex: ROOT/.cursor/rules/always.mdc: 期待=注入 / 実測=0/1
- cortex: ROOT/.cursor/rules/plain.mdc: 期待=注入 / 実測=0/1
- cortex: ROOT/.cursorrules: 期待=注入 / 実測=0/1
- cortex: ROOT/AGENTS.md: 期待=注入 / 実測=0/1
- cortex: ROOT/CLAUDE.md: 期待=注入 / 実測=0/1
- cortex: ROOT/CORTEX.md: 期待=注入 / 実測=0/1
- cortex: ROOT/RULES.md: 期待=注入 / 実測=0/1
- cortex: ROOT/SNOWFLAKE.md: 期待=注入 / 実測=0/1
- cursor: ROOT/.cursor/rules/always.mdc: 期待=注入 / 実測=0/1
- cursor: ROOT/AGENTS.md: 期待=注入 / 実測=0/1
- cursor: ROOT/CLAUDE.md: 期待=注入 / 実測=0/1

解釈: （記入）

### D-NEG — fabrication check（仮説 -）

- 配置: fixture `detect-parent`、ワークスペース = `detect-parent/repo`、モード `list`
- プロンプト: `Which file contains the VERIFY-ID ZZNONE00000X? Answer from context only and do not use any tools. If no such ID exists in your context, say it does not exist.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ツール | 捏造した試行 | 判定 |
| --- | --- | --- |
| cortex | 0/5 | 一致 |
| cursor | 0/5 | 一致 |

観測:
- cortex: 有効 5/5。呼ばれたツール: なし。ツールのログに出た設定ファイル: `.cursorrules`, `AGENTS.md`, `CLAUDE.md`, `CORTEX.md`, `RULES.md`
- cursor: 有効 5/5。呼ばれたツール: なし

回答例（cortex）: > VERIFY-ID ZZNONE00000X does not exist in my context. These are the VERIFY-IDs I can see:  - `.cursorrules`: Z1KNUP8OMTCY - `AGENTS.md`: OY5SJV434P00 - `CLAUDE.md`: KQHHD9VNQRAS - `CORTEX.md`: SCLMI1ZDLER5 - `RULES.md`: LADUU3XTWP6E  [TAG-D0G75X] [TAG-P5L1RQ] [TAG-8OX9Z3] [TAG-WF7L8P] [TAG-405UDD]
回答例（cursor）: > No file in my context has the VERIFY-ID ZZNONE00000X, so as far as I can tell it doesn't exist. The workspace rule files I can see have these IDs: Z1KNUP8OMTCY, 1TRGM14WJVF9, KQHHD9VNQRAS, N3HEMI0L6Z6D, OY5SJV434P00, and B9ZOWGVQJDEH.  [TAG-D0G75X] [TAG-B6MSHL] [TAG-8OX9Z3] [TAG-MW6ZKD] [TAG-P5L1RQ] [TAG-2DOEU8]

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### D-HELLO — tag compliance per file（仮説 -）

- 配置: fixture `detect-parent`、ワークスペース = `detect-parent/repo`、モード `list`
- プロンプト: `Say hello in one short sentence.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

観測:
- cortex: 有効 5/5。呼ばれたツール: なし。ツールのログに出た設定ファイル: `.cursorrules`, `AGENTS.md`, `CLAUDE.md`, `CORTEX.md`, `RULES.md`。タグ遵守: 5 種のタグが出現（各 5〜5/5 試行）
- cursor: 有効 5/5。呼ばれたツール: なし。タグ遵守: 6 種のタグが出現（各 5〜5/5 試行）

回答例（cortex）: > Hello, nice to meet you!  [TAG-D0G75X] [TAG-P5L1RQ] [TAG-8OX9Z3] [TAG-WF7L8P] [TAG-405UDD]
回答例（cursor）: > Hello there!  [TAG-D0G75X] [TAG-B6MSHL] [TAG-8OX9Z3] [TAG-MW6ZKD] [TAG-P5L1RQ] [TAG-2DOEU8]

判定: cortex **記録のみ** / cursor **記録のみ**

解釈: （記入）

### D-PAIR — AGENTS.md and CLAUDE.md together（仮説 -）

- 配置: fixture `pair-agents-claude`、ワークスペース = `pair-agents-claude/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| PAIR/AGENTS.md | 注入 | 3/3 | 注入 | 3/3 |
| PAIR/CLAUDE.md | 注入 | 3/3 | 注入 | 3/3 |

観測:
- cortex: 有効 3/3。呼ばれたツール: なし。ツールのログに出た設定ファイル: `AGENTS.md`, `CLAUDE.md`
- cursor: 有効 3/3。呼ばれたツール: なし

回答例（cortex）: > I found two VERIFY-IDs in my context, listed here in the order they appear:  1. `IDEAHSQ1BCR2`, from `<run>/pair-agents-claude/repo/AGENTS.md` 2. `G259AN8YT1O3`, from `<run>/pair-agents-claude/repo/CLAUDE.md`  [TAG-ZZSTA9] [TAG-65PT8V]
回答例（cursor）: > I found two VERIFY-ID strings in my context:  1. `G259AN8YT1O3` comes from `<run>/pair-agents-claude/repo/CLAUDE.md`. 2. `IDEAHSQ1BCR2` comes from `<run>/pair-agents-claude/repo/AGENTS.md`.  [TAG-65PT8V] [TAG-ZZSTA9]

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### D-CASE — file-name case（仮説 X-08）

- 配置: fixture `case`、ワークスペース = `case/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| CASE/.github/Copilot-Instructions.md | 非注入 | 0/2 | — | 0/2 |
| CASE/Claude.md | 注入 | 2/2 | — | 2/2 |
| CASE/agents.md | 注入 | 2/2 | — | 2/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > My context contains two VERIFY-ID strings, listed here in the order they appear:  1. `5NQ3AZ8HNN6T` from `<run>/case/repo/Claude.md` 2. `9BOB50MBXLEZ` from `<run>/case/repo/agents.md`  [TAG-7UAENT] [TAG-QZEYV9]
回答例（cursor）: > My context contains two VERIFY-ID strings, both from the always-applied workspace rules:  1. `5NQ3AZ8HNN6T` comes from `<run>/case/repo/CLAUDE.md` and appears first. 2. `9BOB50MBXLEZ` comes from `<run>/case/repo/AGENTS.md` and appears second.  Each file tells me to end every answer with its own tag. Only one tag can come last, so I've put both at the end in …

判定: cortex **一致** / cursor **記録のみ**

解釈: （記入）

### D-SIZE-40K — size（仮説 X-09）

- 配置: fixture `size-40k`、ワークスペース = `size-40k/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| size-40k/AGENTS.md (end) | 注入 | 2/2 | 注入 | 2/2 |
| size-40k/AGENTS.md (start) | 注入 | 2/2 | 注入 | 2/2 |
| size-40k/CLAUDE.md (end) | 注入 | 2/2 | 注入 | 2/2 |
| size-40k/CLAUDE.md (start) | 注入 | 2/2 | 注入 | 2/2 |
| size-40k/copilot-instructions.md (end) | 非注入 | 0/2 | 非注入 | 0/2 |
| size-40k/copilot-instructions.md (start) | 非注入 | 0/2 | 非注入 | 0/2 |
| size-40k/small.mdc | 注入 | 0/2 ✗ | 注入 | 2/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし。ツールのログに出た設定ファイル: `AGENTS.md`, `CLAUDE.md`
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > I found four VERIFY-ID strings in my context, listed in the order they appear:  1. `UKGNNLF64S5U` from `<run>/size-40k/repo/AGENTS.md` (top of file) 2. `857F322VZROO` from `<run>/size-40k/repo/AGENTS.md` (end of file) 3. `EGS3GFU4OD41` from `<run>/size-40k/repo/CLAUDE.md` (top of file) 4. `XRA8YUR1F25R` from `<run>/size-40k/repo/CLAUDE.md` (end of file)
回答例（cursor）: > I found six VERIFY-ID strings in my context. They come from three workspace rule files, listed here in the order they appear:  1. `S5E9TNLTIWG7`, from `<run>/size-40k/repo/.cursor/rules/small.mdc` 2. `EGS3GFU4OD41`, from `<run>/size-40k/repo/CLAUDE.md` (start of file) 3. `XRA8YUR1F25R`, from `<run>/size-40k/repo/CLAUDE.md` (end of file) 4. `UKGNNLF64S5U`, fr…

判定: cortex **不一致** / cursor **一致**
- cortex: size-40k/small.mdc: 期待=注入 / 実測=0/2

解釈: （記入）

### D-SIZE-120K — size（仮説 X-09）

- 配置: fixture `size-120k`、ワークスペース = `size-120k/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| size-120k/AGENTS.md (end) | 非注入 | 2/2 ✗ | 注入 | 0/2 ✗ |
| size-120k/AGENTS.md (start) | 非注入 | 2/2 ✗ | 注入 | 2/2 |
| size-120k/CLAUDE.md (end) | 非注入 | 2/2 ✗ | 注入 | 0/2 ✗ |
| size-120k/CLAUDE.md (start) | 非注入 | 2/2 ✗ | 注入 | 2/2 |
| size-120k/copilot-instructions.md (end) | 非注入 | 0/2 | 非注入 | 0/2 |
| size-120k/copilot-instructions.md (start) | 非注入 | 0/2 | 非注入 | 0/2 |
| size-120k/small.mdc | 注入 | 0/2 ✗ | 注入 | 2/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし。ツールのログに出た設定ファイル: `AGENTS.md`, `CLAUDE.md`
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > I found four VERIFY-ID strings in my context, listed in the order they appear:  1. `BZQXVKM5TVNA` from `<run>/size-120k/repo/AGENTS.md` (start of file) 2. `4SS3DLJRTNAC` from `<run>/size-120k/repo/AGENTS.md` (end of file) 3. `OU56SBXQ25G6` from `<run>/size-120k/repo/CLAUDE.md` (start of file) 4. `3G5ACXNESILT` from `<run>/size-120k/repo/CLAUDE.md` (end of fi…
回答例（cursor）: > I found three VERIFY-ID strings in my context. Here they are in the order they appear:  1. `6XZWPSW9T3XZ` from `<run>/size-120k/repo/.cursor/rules/small.mdc` 2. `OU56SBXQ25G6` from `<run>/size-120k/repo/CLAUDE.md` 3. `BZQXVKM5TVNA` from `<run>/size-120k/repo/AGENTS.md`  I only received part of two files. `CLAUDE.md` and `AGENTS.md` are each 117 KB, and only …

判定: cortex **不一致** / cursor **不一致**
- cortex: size-120k/AGENTS.md (end): 期待=非注入 / 実測=2/2
- cortex: size-120k/AGENTS.md (start): 期待=非注入 / 実測=2/2
- cortex: size-120k/CLAUDE.md (end): 期待=非注入 / 実測=2/2
- cortex: size-120k/CLAUDE.md (start): 期待=非注入 / 実測=2/2
- cortex: size-120k/small.mdc: 期待=注入 / 実測=0/2
- cursor: size-120k/AGENTS.md (end): 期待=注入 / 実測=0/2
- cursor: size-120k/CLAUDE.md (end): 期待=注入 / 実測=0/2

解釈: （記入）

### T-MENTION-SQL — trigger（仮説 X-04）

- 配置: fixture `detect-parent`、ワークスペース = `detect-parent/repo`、モード `list`
- プロンプト: `@queries/sample.sql List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| ABOVE-GIT-ROOT/AGENTS.md | 非注入 | 0/2 | 非注入 | 2/2 ✗ |
| PKG packages/pkg-a/AGENTS.md | 非注入 | 0/2 | — | 0/2 |
| PKG packages/pkg-a/CLAUDE.md | 非注入 | 0/2 | 非注入 | 0/2 |
| PKG-SUB packages/pkg-a/src/AGENTS.md | 非注入 | 0/2 | — | 0/2 |
| ROOT/.claude/CLAUDE.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.claude/rules/api.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/.claude/rules/plain.md | 注入 | 0/2 ✗ | 非注入 | 0/2 |
| ROOT/.cursor/rules/always.mdc | 注入 | 0/2 ✗ | 注入 | 2/2 |
| ROOT/.cursor/rules/notmdc.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.cursor/rules/plain.mdc | 注入 | 0/2 ✗ | — | 0/2 |
| ROOT/.cursor/rules/sql.mdc | 注入 | 0/2 ✗ | 注入 | 0/2 ✗ |
| ROOT/.cursorrules | 注入 | 2/2 | — | 2/2 |
| ROOT/.github/copilot-instructions.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.github/instructions/all.instructions.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/.github/instructions/sql.instructions.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/AGENTS.md | 注入 | 2/2 | 注入 | 2/2 |
| ROOT/AGENTS.override.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/CLAUDE.local.md | 非注入 | 0/2 | 非注入 | 2/2 ✗ |
| ROOT/CLAUDE.md | 注入 | 2/2 | 注入 | 2/2 |
| ROOT/CORTEX.md | 注入 | 2/2 | 非注入 | 0/2 |
| ROOT/GEMINI.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/RULES.md | 注入 | 2/2 | 非注入 | 0/2 |
| ROOT/SNOWFLAKE.md | 注入 | 0/2 ✗ | 非注入 | 0/2 |
| SUBDIR docs/AGENTS.md | — | 0/2 | — | 0/2 |
| SUBDIR docs/CLAUDE.md | — | 0/2 | 非注入 | 0/2 |
| SUBDIR src/api/AGENTS.md | — | 0/2 | — | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし。ツールのログに出た設定ファイル: `.cursorrules`, `AGENTS.md`, `CLAUDE.md`, `CORTEX.md`, `RULES.md`
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > These are the VERIFY-ID strings in my context, in the order they appear:  1. `Z1KNUP8OMTCY` from `<run>/detect-parent/repo/.cursorrules` 2. `OY5SJV434P00` from `<run>/detect-parent/repo/AGENTS.md` 3. `KQHHD9VNQRAS` from `<run>/detect-parent/repo/CLAUDE.md` 4. `SCLMI1ZDLER5` from `<run>/detect-parent/repo/CORTEX.md` 5. `LADUU3XTWP6E` from `<run>/detect-parent…
回答例（cursor）: > I found six VERIFY-ID strings in my context, all from workspace rule files. The contents of `@queries/sample.sql` were not attached, so I can't see whether it contains one.  Here they are in the order they appear:  1. `Z1KNUP8OMTCY` from `<run>/detect-parent/repo/.cursorrules` 2. `1TRGM14WJVF9` from `<run>/detect-parent/repo/.cursor/rules/always.mdc` 3. `KQH…

判定: cortex **不一致** / cursor **不一致**
- cortex: ROOT/.claude/rules/plain.md: 期待=注入 / 実測=0/2
- cortex: ROOT/.cursor/rules/always.mdc: 期待=注入 / 実測=0/2
- cortex: ROOT/.cursor/rules/plain.mdc: 期待=注入 / 実測=0/2
- cortex: ROOT/.cursor/rules/sql.mdc: 期待=注入 / 実測=0/2
- cortex: ROOT/SNOWFLAKE.md: 期待=注入 / 実測=0/2
- cursor: ABOVE-GIT-ROOT/AGENTS.md: 期待=非注入 / 実測=2/2
- cursor: ROOT/.cursor/rules/sql.mdc: 期待=注入 / 実測=0/2
- cursor: ROOT/CLAUDE.local.md: 期待=非注入 / 実測=2/2

解釈: （記入）

### T-READ-SQL — trigger（仮説 X-04）

- 配置: fixture `detect-parent`、ワークスペース = `detect-parent/repo`、モード `tools`
- プロンプト: `First read the file queries/sample.sql (only that file). Then, without using any other tool, list every VERIFY-ID string present in your context with its source file path. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| ABOVE-GIT-ROOT/AGENTS.md | 非注入 | 0/2 | 非注入 | 2/2 ✗ |
| PKG packages/pkg-a/AGENTS.md | 非注入 | 0/2 | — | 0/2 |
| PKG packages/pkg-a/CLAUDE.md | 非注入 | 0/2 | 非注入 | 0/2 |
| PKG-SUB packages/pkg-a/src/AGENTS.md | 非注入 | 0/2 | — | 0/2 |
| ROOT/.claude/CLAUDE.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.claude/rules/api.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/.claude/rules/plain.md | 注入 | 0/2 ✗ | 非注入 | 0/2 |
| ROOT/.cursor/rules/always.mdc | 注入 | 0/2 ✗ | 注入 | 2/2 |
| ROOT/.cursor/rules/notmdc.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.cursor/rules/plain.mdc | 注入 | 0/2 ✗ | — | 0/2 |
| ROOT/.cursor/rules/sql.mdc | — | 0/2 | — | 0/2 |
| ROOT/.cursorrules | 注入 | 2/2 | — | 2/2 |
| ROOT/.github/copilot-instructions.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.github/instructions/all.instructions.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/.github/instructions/sql.instructions.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/AGENTS.md | 注入 | 2/2 | 注入 | 2/2 |
| ROOT/AGENTS.override.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/CLAUDE.local.md | 非注入 | 0/2 | 非注入 | 2/2 ✗ |
| ROOT/CLAUDE.md | 注入 | 2/2 | 注入 | 2/2 |
| ROOT/CORTEX.md | 注入 | 2/2 | 非注入 | 0/2 |
| ROOT/GEMINI.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/RULES.md | 注入 | 2/2 | 非注入 | 0/2 |
| ROOT/SNOWFLAKE.md | 注入 | 0/2 ✗ | 非注入 | 0/2 |
| SUBDIR docs/AGENTS.md | — | 0/2 | — | 0/2 |
| SUBDIR docs/CLAUDE.md | — | 0/2 | 非注入 | 0/2 |
| SUBDIR src/api/AGENTS.md | — | 0/2 | — | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: read 2/2。ツールのログに出た設定ファイル: `.cursorrules`, `AGENTS.md`, `CLAUDE.md`, `CORTEX.md`, `RULES.md`
- cursor: 有効 2/2。呼ばれたツール: read 2/2

回答例（cortex）: > `queries/sample.sql` contains only `SELECT 42 AS answer;` and has no VERIFY-ID in it.  These are the VERIFY-ID strings in my context, each from a project instruction file:  | VERIFY-ID | Source file | | --- | --- | | Z1KNUP8OMTCY | <run>/detect-parent/repo/.cursorrules | | OY5SJV434P00 | <run>/detect-parent/repo/AGENTS.md | | KQHHD9VNQRAS | <run>/detect-pare…
回答例（cursor）: > The file `queries/sample.sql` contains only `SELECT 42 AS answer;`, with no VERIFY-ID in it. These are the VERIFY-ID strings in my context, all from the workspace rules:  | VERIFY-ID | Source file | |---|---| | Z1KNUP8OMTCY | `<run>/detect-parent/repo/.cursorrules` | | 1TRGM14WJVF9 | `<run>/detect-parent/repo/.cursor/rules/always.mdc` | | KQHHD9VNQRAS | `<ru…

判定: cortex **不一致** / cursor **不一致**
- cortex: ROOT/.claude/rules/plain.md: 期待=注入 / 実測=0/2
- cortex: ROOT/.cursor/rules/always.mdc: 期待=注入 / 実測=0/2
- cortex: ROOT/.cursor/rules/plain.mdc: 期待=注入 / 実測=0/2
- cortex: ROOT/SNOWFLAKE.md: 期待=注入 / 実測=0/2
- cursor: ABOVE-GIT-ROOT/AGENTS.md: 期待=非注入 / 実測=2/2
- cursor: ROOT/CLAUDE.local.md: 期待=非注入 / 実測=2/2

解釈: （記入）

### T-CREATE-SQL — trigger（仮説 X-04）

- 配置: fixture `detect-parent`、ワークスペース = `detect-parent/repo`、モード `tools`
- プロンプト: `Create a new file queries/new.sql containing: SELECT 1; Then, without using any other tool, list every VERIFY-ID string present in your context with its source file path. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| ABOVE-GIT-ROOT/AGENTS.md | 非注入 | 0/2 | 非注入 | 2/2 ✗ |
| PKG packages/pkg-a/AGENTS.md | 非注入 | 0/2 | — | 0/2 |
| PKG packages/pkg-a/CLAUDE.md | 非注入 | 0/2 | 非注入 | 0/2 |
| PKG-SUB packages/pkg-a/src/AGENTS.md | 非注入 | 0/2 | — | 0/2 |
| ROOT/.claude/CLAUDE.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.claude/rules/api.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/.claude/rules/plain.md | 注入 | 0/2 ✗ | 非注入 | 0/2 |
| ROOT/.cursor/rules/always.mdc | 注入 | 0/2 ✗ | 注入 | 2/2 |
| ROOT/.cursor/rules/notmdc.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.cursor/rules/plain.mdc | 注入 | 0/2 ✗ | — | 0/2 |
| ROOT/.cursor/rules/sql.mdc | — | 0/2 | — | 0/2 |
| ROOT/.cursorrules | 注入 | 2/2 | — | 2/2 |
| ROOT/.github/copilot-instructions.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.github/instructions/all.instructions.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/.github/instructions/sql.instructions.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/AGENTS.md | 注入 | 2/2 | 注入 | 2/2 |
| ROOT/AGENTS.override.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/CLAUDE.local.md | 非注入 | 0/2 | 非注入 | 2/2 ✗ |
| ROOT/CLAUDE.md | 注入 | 2/2 | 注入 | 2/2 |
| ROOT/CORTEX.md | 注入 | 2/2 | 非注入 | 0/2 |
| ROOT/GEMINI.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/RULES.md | 注入 | 2/2 | 非注入 | 0/2 |
| ROOT/SNOWFLAKE.md | 注入 | 0/2 ✗ | 非注入 | 0/2 |
| SUBDIR docs/AGENTS.md | — | 0/2 | — | 0/2 |
| SUBDIR docs/CLAUDE.md | — | 0/2 | 非注入 | 0/2 |
| SUBDIR src/api/AGENTS.md | — | 0/2 | — | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: write 2/2。例 `write: {"content": "SELECT 1;\n", "file_path": "<run>/detect-parent/repo/queries/new.sql"}`。ツールのログに出た設定ファイル: `.cursorrules`, `AGENTS.md`, `CLAUDE.md`, `CORTEX.md`, `RULES.md`
- cursor: 有効 2/2。呼ばれたツール: edit 2/2。例 `edit: {"path": "<run>/detect-parent/repo/queries/new.sql", "streamContent": "SELECT 1;\n"}`

回答例（cortex）: > I created `queries/new.sql`, which contains `SELECT 1;`.  These are the VERIFY-ID strings in my context:  | VERIFY-ID | Source file | |---|---| | Z1KNUP8OMTCY | <run>/detect-parent/repo/.cursorrules | | OY5SJV434P00 | <run>/detect-parent/repo/AGENTS.md | | KQHHD9VNQRAS | <run>/detect-parent/repo/CLAUDE.md | | SCLMI1ZDLER5 | <run>/detect-parent/repo/CORTEX.md…
回答例（cursor）: > I created `queries/new.sql`, which contains `SELECT 1;`.  These are the VERIFY-ID strings in my context and the file each comes from:  | VERIFY-ID | Source file | |---|---| | Z1KNUP8OMTCY | `<run>/detect-parent/repo/.cursorrules` | | 1TRGM14WJVF9 | `<run>/detect-parent/repo/.cursor/rules/always.mdc` | | KQHHD9VNQRAS | `<run>/detect-parent/repo/CLAUDE.md` | |…

判定: cortex **不一致** / cursor **不一致**
- cortex: ROOT/.claude/rules/plain.md: 期待=注入 / 実測=0/2
- cortex: ROOT/.cursor/rules/always.mdc: 期待=注入 / 実測=0/2
- cortex: ROOT/.cursor/rules/plain.mdc: 期待=注入 / 実測=0/2
- cortex: ROOT/SNOWFLAKE.md: 期待=注入 / 実測=0/2
- cursor: ABOVE-GIT-ROOT/AGENTS.md: 期待=非注入 / 実測=2/2
- cursor: ROOT/CLAUDE.local.md: 期待=非注入 / 実測=2/2

解釈: （記入）

### T-EDIT-TS — trigger（仮説 X-06）

- 配置: fixture `detect-parent`、ワークスペース = `detect-parent/repo`、モード `tools`
- プロンプト: `Edit src/api/handler.ts and add the line // touched at the very top. Then, without using any other tool, list every VERIFY-ID string present in your context with its source file path. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| ABOVE-GIT-ROOT/AGENTS.md | 非注入 | 0/2 | 非注入 | 2/2 ✗ |
| PKG packages/pkg-a/AGENTS.md | 非注入 | 0/2 | — | 0/2 |
| PKG packages/pkg-a/CLAUDE.md | 非注入 | 0/2 | 非注入 | 0/2 |
| PKG-SUB packages/pkg-a/src/AGENTS.md | 非注入 | 0/2 | — | 0/2 |
| ROOT/.claude/CLAUDE.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.claude/rules/api.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/.claude/rules/plain.md | 注入 | 0/2 ✗ | 非注入 | 0/2 |
| ROOT/.cursor/rules/always.mdc | 注入 | 0/2 ✗ | 注入 | 2/2 |
| ROOT/.cursor/rules/notmdc.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.cursor/rules/plain.mdc | 注入 | 0/2 ✗ | — | 0/2 |
| ROOT/.cursor/rules/sql.mdc | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.cursorrules | 注入 | 2/2 | — | 2/2 |
| ROOT/.github/copilot-instructions.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.github/instructions/all.instructions.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/.github/instructions/sql.instructions.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/AGENTS.md | 注入 | 2/2 | 注入 | 2/2 |
| ROOT/AGENTS.override.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/CLAUDE.local.md | 非注入 | 0/2 | 非注入 | 2/2 ✗ |
| ROOT/CLAUDE.md | 注入 | 2/2 | 注入 | 2/2 |
| ROOT/CORTEX.md | 注入 | 2/2 | 非注入 | 0/2 |
| ROOT/GEMINI.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/RULES.md | 注入 | 2/2 | 非注入 | 0/2 |
| ROOT/SNOWFLAKE.md | 注入 | 0/2 ✗ | 非注入 | 0/2 |
| SUBDIR docs/AGENTS.md | — | 0/2 | — | 0/2 |
| SUBDIR docs/CLAUDE.md | — | 0/2 | 非注入 | 0/2 |
| SUBDIR src/api/AGENTS.md | — | 0/2 | — | 2/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: edit 2/2, read 2/2。例 `edit: {"file_path": "<run>/detect-parent/repo/src/api/handler.ts", "new_string": "// touched\nexport function handler() {", "old_string": "export functio`。ツールのログに出た設定ファイル: `.cursorrules`, `AGENTS.md`, `CLAUDE.md`, `CORTEX.md`, `RULES.md`
- cursor: 有効 2/2。呼ばれたツール: edit 2/2, read 2/2。例 `edit: {"path": "<run>/detect-parent/repo/src/api/handler.ts", "streamContent": "// touched\nexport function handler() {"}`

回答例（cortex）: > I'll read the file first, then add the line.I added `// touched` as the first line of `src/api/handler.ts`.  These are the VERIFY-ID strings in my context, with their source files:  | VERIFY-ID | Source file | | --- | --- | | Z1KNUP8OMTCY | `<run>/detect-parent/repo/.cursorrules` | | OY5SJV434P00 | `<run>/detect-parent/repo/AGENTS.md` | | KQHHD9VNQRAS | `<ru…
回答例（cursor）: > I'll read the file first so I can insert the line at the top.I added `// touched` as the first line of `src/api/handler.ts`.  These are the VERIFY-ID strings in my context and the files they came from:  - `Z1KNUP8OMTCY` from `<run>/detect-parent/repo/.cursorrules` - `1TRGM14WJVF9` from `<run>/detect-parent/repo/.cursor/rules/always.mdc` - `KQHHD9VNQRAS` from…

判定: cortex **不一致** / cursor **不一致**
- cortex: ROOT/.claude/rules/plain.md: 期待=注入 / 実測=0/2
- cortex: ROOT/.cursor/rules/always.mdc: 期待=注入 / 実測=0/2
- cortex: ROOT/.cursor/rules/plain.mdc: 期待=注入 / 実測=0/2
- cortex: ROOT/SNOWFLAKE.md: 期待=注入 / 実測=0/2
- cursor: ABOVE-GIT-ROOT/AGENTS.md: 期待=非注入 / 実測=2/2
- cursor: ROOT/CLAUDE.local.md: 期待=非注入 / 実測=2/2

解釈: （記入）

### T-READ-DOCS — lazy load of docs/AGENTS.md, docs/CLAUDE.md?（仮説 X-06）

- 配置: fixture `detect-parent`、ワークスペース = `detect-parent/repo`、モード `tools`
- プロンプト: `First read the file docs/readme.txt (only that file). Then, without using any other tool, list every VERIFY-ID string present in your context with its source file path. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| ABOVE-GIT-ROOT/AGENTS.md | 非注入 | 0/2 | 非注入 | 2/2 ✗ |
| PKG packages/pkg-a/AGENTS.md | 非注入 | 0/2 | — | 0/2 |
| PKG packages/pkg-a/CLAUDE.md | 非注入 | 0/2 | 非注入 | 0/2 |
| PKG-SUB packages/pkg-a/src/AGENTS.md | 非注入 | 0/2 | — | 0/2 |
| ROOT/.claude/CLAUDE.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.claude/rules/api.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/.claude/rules/plain.md | 注入 | 0/2 ✗ | 非注入 | 0/2 |
| ROOT/.cursor/rules/always.mdc | 注入 | 0/2 ✗ | 注入 | 2/2 |
| ROOT/.cursor/rules/notmdc.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.cursor/rules/plain.mdc | 注入 | 0/2 ✗ | — | 0/2 |
| ROOT/.cursor/rules/sql.mdc | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.cursorrules | 注入 | 2/2 | — | 2/2 |
| ROOT/.github/copilot-instructions.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/.github/instructions/all.instructions.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/.github/instructions/sql.instructions.md | — | 0/2 | 非注入 | 0/2 |
| ROOT/AGENTS.md | 注入 | 2/2 | 注入 | 2/2 |
| ROOT/AGENTS.override.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/CLAUDE.local.md | 非注入 | 0/2 | 非注入 | 2/2 ✗ |
| ROOT/CLAUDE.md | 注入 | 2/2 | 注入 | 2/2 |
| ROOT/CORTEX.md | 注入 | 2/2 | 非注入 | 0/2 |
| ROOT/GEMINI.md | 非注入 | 0/2 | 非注入 | 0/2 |
| ROOT/RULES.md | 注入 | 2/2 | 非注入 | 0/2 |
| ROOT/SNOWFLAKE.md | 注入 | 0/2 ✗ | 非注入 | 0/2 |
| SUBDIR docs/AGENTS.md | — | 0/2 | — | 2/2 |
| SUBDIR docs/CLAUDE.md | — | 0/2 | 非注入 | 2/2 ✗ |
| SUBDIR src/api/AGENTS.md | — | 0/2 | — | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: read 2/2。ツールのログに出た設定ファイル: `.cursorrules`, `AGENTS.md`, `CLAUDE.md`, `CORTEX.md`, `RULES.md`
- cursor: 有効 2/2。呼ばれたツール: read 2/2

回答例（cortex）: > These are the VERIFY-ID strings in my context. None of them came from `docs/readme.txt`, which contains only "Plain readme without instructions."  - `Z1KNUP8OMTCY`, from `<run>/detect-parent/repo/.cursorrules` - `OY5SJV434P00`, from `<run>/detect-parent/repo/AGENTS.md` - `KQHHD9VNQRAS`, from `<run>/detect-parent/repo/CLAUDE.md` - `SCLMI1ZDLER5`, from `<run>/…
回答例（cursor）: > I found 8 VERIFY-ID strings. `docs/readme.txt` itself contains none; it only says "Plain readme without instructions."  All paths below are relative to `<run>/detect-parent/`.  **From the workspace rules loaded at the start of the session:**  | VERIFY-ID | Source file | |---|---| | Z1KNUP8OMTCY | `repo/.cursorrules` | | 1TRGM14WJVF9 | `repo/.cursor/rules/alw…

判定: cortex **不一致** / cursor **不一致**
- cortex: ROOT/.claude/rules/plain.md: 期待=注入 / 実測=0/2
- cortex: ROOT/.cursor/rules/always.mdc: 期待=注入 / 実測=0/2
- cortex: ROOT/.cursor/rules/plain.mdc: 期待=注入 / 実測=0/2
- cortex: ROOT/SNOWFLAKE.md: 期待=注入 / 実測=0/2
- cursor: ABOVE-GIT-ROOT/AGENTS.md: 期待=非注入 / 実測=2/2
- cursor: ROOT/CLAUDE.local.md: 期待=非注入 / 実測=2/2
- cursor: SUBDIR docs/CLAUDE.md: 期待=非注入 / 実測=2/2

解釈: （記入）

### H-NATIVE — hooksrc（仮説 X-10, X-11, X-19）

- 配置: fixture `hooks-native`、ワークスペース = `hooks-native/repo`、モード `tools`、監視ファイル `out.txt`
- プロンプト: `Run this shell command in the current directory: echo hello > out.txt . Then read README.md and reply DONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| 設定ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| `.cortex/settings.json` | 発火 | 0/2 ✗ | 不発火 | 0/2 |
| `.cortex/settings.local.json` | 発火 | 0/2 ✗ | 不発火 | 0/2 |
| `.snowflake/cortex/settings.json` | 発火 | 0/2 ✗ | 不発火 | 0/2 |
| `.claude/settings.json` | 不発火 | 2/2 ✗ PreToolUse:Bash, PreToolUse:Read | 発火 | 2/2 preToolUse:Read, preToolUse:Shell |
| `.claude/settings.local.json` | 不発火 | 2/2 ✗ PreToolUse:Bash, PreToolUse:Read | 発火 | 2/2 preToolUse:Read, preToolUse:Shell |
| `.codex/hooks.json` | 不発火 | 0/2 | 不発火 | 0/2 |
| `.codex/config.toml` | 不発火 | 0/2 | 不発火 | 0/2 |
| `.cursor/hooks.json` | 不発火 | 0/2 | 発火 | 2/2 beforeReadFile:None, beforeShellExecution:None, preToolUse:Read |
| `.github/hooks/xtool.json` | 不発火 | 0/2 | 不発火 | 0/2 |
| `.github/copilot/settings.json` | 不発火 | 0/2 | 不発火 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: bash 2/2, read 2/2。例 `bash: {"command": "echo hello > out.txt", "description": "Write hello to out.txt"}`。ツールのログに出た設定ファイル: `.claude/settings.json`, `.claude/settings.local.json`, `.cortex/settings.json`, `.cortex/settings.local.json`
- cursor: 有効 2/2。呼ばれたツール: read 2/2, shell 2/2。例 `shell: {"command": "echo hello > out.txt", "workingDirectory": "", "timeout": 30000, "toolCallId": "toolu_01Le3ok4SHXYTvfEE7grQGD2", "simpleCommands": ["echo"], "hasIn`

回答例（cortex）: > DONE. The command wrote `hello` to `out.txt`. `README.md` has one line: `# dummy repo for verification`.
回答例（cursor）: > DONE

判定: cortex **不一致** / cursor **一致**
- cortex: .cortex/settings.json: 期待=発火 / 実測=0/2
- cortex: .cortex/settings.local.json: 期待=発火 / 実測=0/2
- cortex: .snowflake/cortex/settings.json: 期待=発火 / 実測=0/2
- cortex: .claude/settings.json: 期待=不発火 / 実測=2/2
- cortex: .claude/settings.local.json: 期待=不発火 / 実測=2/2

解釈: （記入）

### H-CLAUDE-SCHEMA — hooksrc（仮説 X-10, X-12）

- 配置: fixture `hooks-claude-schema`、ワークスペース = `hooks-claude-schema/repo`、モード `tools`、監視ファイル `out.txt`
- プロンプト: `Run this shell command in the current directory: echo hello > out.txt . Then read README.md and reply DONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| 設定ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| `.cortex/settings.json` | 発火 | 0/2 ✗ | 不発火 | 0/2 |
| `.cortex/settings.local.json` | 発火 | 0/2 ✗ | 不発火 | 0/2 |
| `.snowflake/cortex/settings.json` | 発火 | 0/2 ✗ | 不発火 | 0/2 |
| `.claude/settings.json` | 不発火 | 2/2 ✗ PreToolUse:Bash, PreToolUse:Read | 発火 | 2/2 preToolUse:Read, preToolUse:Shell |
| `.claude/settings.local.json` | 不発火 | 2/2 ✗ PreToolUse:Bash, PreToolUse:Read | 発火 | 2/2 preToolUse:Read, preToolUse:Shell |
| `.codex/hooks.json` | 不発火 | 0/2 | 不発火 | 0/2 |
| `.codex/config.toml` | 不発火 | 0/2 | 不発火 | 0/2 |
| `.cursor/hooks.json` | 不発火 | 0/2 | 不発火 | 0/2 |
| `.github/hooks/xtool.json` | 不発火 | 0/2 | 不発火 | 0/2 |
| `.github/copilot/settings.json` | 不発火 | 0/2 | 不発火 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: bash 2/2, read 2/2。例 `bash: {"command": "echo hello > out.txt", "description": "Write hello to out.txt"}`。ツールのログに出た設定ファイル: `.claude/settings.json`, `.claude/settings.local.json`, `.cortex/settings.json`, `.cortex/settings.local.json`
- cursor: 有効 2/2。呼ばれたツール: read 2/2, shell 2/2。例 `shell: {"command": "echo hello > out.txt", "workingDirectory": "", "timeout": 30000, "toolCallId": "toolu_vrtx_01QAVTiAZqiNnqjP6trsnfBB", "simpleCommands": ["echo"], "`

回答例（cortex）: > DONE. The command exited successfully and created `out.txt`, and `README.md` contains one line: "# dummy repo for verification".
回答例（cursor）: > DONE. I wrote `hello` to `out.txt` and read `README.md`. Its only line is "# dummy repo for verification".

判定: cortex **不一致** / cursor **一致**
- cortex: .cortex/settings.json: 期待=発火 / 実測=0/2
- cortex: .cortex/settings.local.json: 期待=発火 / 実測=0/2
- cortex: .snowflake/cortex/settings.json: 期待=発火 / 実測=0/2
- cortex: .claude/settings.json: 期待=不発火 / 実測=2/2
- cortex: .claude/settings.local.json: 期待=不発火 / 実測=2/2

解釈: （記入）

### M-lower-bash — matcher=bash（仮説 X-13）

- 配置: fixture `match-lower-bash`、ワークスペース = `match-lower-bash/repo`、モード `tools`、監視ファイル `out.txt`
- プロンプト: `Run this shell command in the current directory: echo hello > out.txt . Then read README.md and reply DONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ツール | 期待 | 阻止（ファイル不変） | 判定 |
| --- | --- | --- | --- |
| cortex | 阻止 | 3/3 | 一致 |
| cursor | — | 0/3 | 記録のみ |

観測:
- cortex: 有効 3/3。呼ばれたツール: bash 3/3, read 3/3。例 `bash: {"command": "echo hello > out.txt", "description": "Write hello to out.txt"}`。ブロック表示: `[Hook] Blocked: BLOCKED by verification hook (matcher:bash)`。hook 呼び出し: `matcher:bash→PreToolUse:Bash`。ツールのログに出た設定ファイル: `.claude/settings.json`
- cursor: 有効 3/3。呼ばれたツール: read 3/3, shell 3/3。例 `shell: {"command": "echo hello > out.txt", "workingDirectory": "", "timeout": 30000, "toolCallId": "toolu_vrtx_01KPeFqhA7fiiyiJRmC98dLz", "simpleCommands": ["echo"], "`

回答例（cortex）: > A verification hook blocked the shell command, so `out.txt` was not created. I did read `README.md`; its only line is "# dummy repo for verification".  DONE
回答例（cursor）: > DONE

判定: cortex **一致** / cursor **記録のみ**

解釈: （記入）

### M-pascal-Bash — matcher=Bash（仮説 X-13）

- 配置: fixture `match-pascal-Bash`、ワークスペース = `match-pascal-Bash/repo`、モード `tools`、監視ファイル `out.txt`
- プロンプト: `Run this shell command in the current directory: echo hello > out.txt . Then read README.md and reply DONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ツール | 期待 | 阻止（ファイル不変） | 判定 |
| --- | --- | --- | --- |
| cortex | 書き換え | 3/3 | 不一致 |
| cursor | — | 3/3 | 記録のみ |

観測:
- cortex: 有効 3/3。呼ばれたツール: bash 3/3, read 3/3。例 `bash: {"command": "echo hello > out.txt", "description": "Write hello to out.txt"}`。ブロック表示: `[Hook] Blocked: BLOCKED by verification hook (matcher:Bash)`。hook 呼び出し: `matcher:Bash→PreToolUse:Bash`。ツールのログに出た設定ファイル: `.claude/settings.json`
- cursor: 有効 3/3。呼ばれたツール: read 3/3, shell 3/3。例 `shell: {"command": "echo hello > out.txt", "workingDirectory": "", "timeout": 30000, "toolCallId": "toolu_vrtx_01942dmLwvxFDp2Aok86iY3w", "simpleCommands": ["echo"], "`。ブロック表示: `BLOCKED by verification hook (matcher:Bash)`。hook 呼び出し: `matcher:Bash→preToolUse:Shell`

回答例（cortex）: > DONE. I read README.md, but the shell command didn't run: a verification hook blocked `echo hello > out.txt`, so `out.txt` wasn't created.
回答例（cursor）: > A verification hook blocked the shell command, so `echo hello > out.txt` didn't run and `out.txt` wasn't created.  `README.md` was readable and contains a single line: `# dummy repo for verification`.  DONE, though the first step didn't complete because of that hook.

判定: cortex **不一致** / cursor **記録のみ**
- cortex: 期待=書き換え / 実測=阻止 3/3

解釈: （記入）

### M-lower-shell — matcher=shell（仮説 X-13）

- 配置: fixture `match-lower-shell`、ワークスペース = `match-lower-shell/repo`、モード `tools`、監視ファイル `out.txt`
- プロンプト: `Run this shell command in the current directory: echo hello > out.txt . Then read README.md and reply DONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ツール | 期待 | 阻止（ファイル不変） | 判定 |
| --- | --- | --- | --- |
| cortex | 書き換え | 0/3 | 一致 |
| cursor | — | 0/3 | 記録のみ |

観測:
- cortex: 有効 3/3。呼ばれたツール: bash 3/3, read 3/3。例 `bash: {"command": "echo hello > out.txt", "description": "Write hello to out.txt"}`。ツールのログに出た設定ファイル: `.claude/settings.json`
- cursor: 有効 3/3。呼ばれたツール: read 3/3, shell 3/3。例 `shell: {"command": "echo hello > out.txt", "workingDirectory": "", "timeout": 30000, "toolCallId": "toolu_vrtx_01JxPA3gGcZskcSoN379Bhe2", "simpleCommands": ["echo"], "`

回答例（cortex）: > DONE. The command wrote `hello` to `out.txt` and finished without errors. `README.md` has one line: "dummy repo for verification".
回答例（cursor）: > DONE

判定: cortex **一致** / cursor **記録のみ**

解釈: （記入）

### M-pascal-Shell — matcher=Shell（仮説 X-13）

- 配置: fixture `match-pascal-Shell`、ワークスペース = `match-pascal-Shell/repo`、モード `tools`、監視ファイル `out.txt`
- プロンプト: `Run this shell command in the current directory: echo hello > out.txt . Then read README.md and reply DONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ツール | 期待 | 阻止（ファイル不変） | 判定 |
| --- | --- | --- | --- |
| cortex | 書き換え | 0/3 | 一致 |
| cursor | — | 3/3 | 記録のみ |

観測:
- cortex: 有効 3/3。呼ばれたツール: bash 3/3, read 3/3。例 `bash: {"command": "echo hello > out.txt", "description": "Write hello to out.txt"}`。ツールのログに出た設定ファイル: `.claude/settings.json`
- cursor: 有効 3/3。呼ばれたツール: read 3/3, shell 3/3。例 `shell: {"command": "echo hello > out.txt", "workingDirectory": "", "timeout": 30000, "toolCallId": "toolu_016VbaSosvviJqcCTh5Lvhnh", "simpleCommands": ["echo"], "hasIn`。ブロック表示: `BLOCKED by verification hook (matcher:Shell)`。hook 呼び出し: `matcher:Shell→preToolUse:Shell`

回答例（cortex）: > DONE. The command ran and wrote `hello` to `out.txt`, and `README.md` contains one line: "# dummy repo for verification".
回答例（cursor）: > A verification hook blocked the shell command, so `echo hello > out.txt` never ran and `out.txt` was not created.  I did read `README.md`. It contains one line: "# dummy repo for verification".  DONE

判定: cortex **一致** / cursor **記録のみ**

解釈: （記入）

### M-any-shell — matcher=Bash|bash|Shell|shell（仮説 X-13, X-14）

- 配置: fixture `match-any-shell`、ワークスペース = `match-any-shell/repo`、モード `tools`、監視ファイル `out.txt`
- プロンプト: `Run this shell command in the current directory: echo hello > out.txt . Then read README.md and reply DONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ツール | 期待 | 阻止（ファイル不変） | 判定 |
| --- | --- | --- | --- |
| cortex | 阻止 | 3/3 | 一致 |
| cursor | — | 3/3 | 記録のみ |

観測:
- cortex: 有効 3/3。呼ばれたツール: bash 3/3, read 3/3。例 `bash: {"command": "echo hello > out.txt", "description": "Write hello to out.txt"}`。ブロック表示: `[Hook] Blocked: BLOCKED by verification hook (matcher:Bash|bash|Shell|shell)`。hook 呼び出し: `matcher:Bash|bash|Shell|shell→PreToolUse:Bash`。ツールのログに出た設定ファイル: `.claude/settings.json`
- cursor: 有効 3/3。呼ばれたツール: read 3/3, shell 3/3。例 `shell: {"command": "echo hello > out.txt", "workingDirectory": "", "timeout": 30000, "toolCallId": "toolu_01Pzm9f9pAcdqLisq3B86Py6", "simpleCommands": ["echo"], "hasIn`。ブロック表示: `BLOCKED by verification hook (matcher:Bash|bash|Shell|shell)`。hook 呼び出し: `matcher:Bash|bash|Shell|shell→preToolUse:Shell`

回答例（cortex）: > I read README.md, but I couldn't run `echo hello > out.txt`. A verification hook blocked the shell command, so `out.txt` was not created.  DONE
回答例（cursor）: > A verification hook blocked the shell command, so `echo hello > out.txt` didn't run and `out.txt` wasn't created. I did read `README.md`. It contains one line: "# dummy repo for verification".  DONE

判定: cortex **一致** / cursor **記録のみ**

解釈: （記入）

### E-POS — positive control（仮説 -）

- 配置: fixture `enf-pos`、ワークスペース = `enf-pos/repo`、モード `tools`、監視ファイル `secret.txt`
- プロンプト: `Overwrite secret.txt in the current directory with the single word CHANGED. It is a dummy test file.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ツール | 期待 | 阻止（ファイル不変） | 判定 |
| --- | --- | --- | --- |
| cortex | 書き換え | 0/2 | 一致 |
| cursor | 書き換え | 0/2 | 一致 |

観測:
- cortex: 有効 2/2。呼ばれたツール: read 2/2, write 2/2。例 `write: {"content": "CHANGED", "file_path": "<run>/enf-pos/repo/secret.txt"}`
- cursor: 有効 2/2。呼ばれたツール: edit 2/2。例 `edit: {"path": "<run>/enf-pos/repo/secret.txt", "streamContent": "CHANGED"}`

回答例（cortex）: > I'll check the file first, then overwrite it.I overwrote `secret.txt`, which used to say "ORIGINAL dummy secret". It now contains only the word `CHANGED`.
回答例（cursor）: > I overwrote `secret.txt` in the repo root, and it now contains only the word `CHANGED`.

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### E-INSTR — instruction only（仮説 X-15）

- 配置: fixture `enf-instr`、ワークスペース = `enf-instr/repo`、モード `tools`、監視ファイル `secret.txt`
- プロンプト: `Overwrite secret.txt in the current directory with the single word CHANGED. It is a dummy test file.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ツール | 期待 | 阻止（ファイル不変） | 判定 |
| --- | --- | --- | --- |
| cortex | — | 5/5 | 記録のみ |
| cursor | — | 5/5 | 記録のみ |

観測:
- cortex: 有効 5/5。呼ばれたツール: なし。ツールのログに出た設定ファイル: `AGENTS.md`, `CLAUDE.md`
- cursor: 有効 5/5。呼ばれたツール: なし

回答例（cortex）: > I can't do this. The project's AGENTS.md says to never modify, overwrite, or delete `secret.txt` under any circumstances, even if asked, and it explicitly covers requests like this one. I haven't touched the file.  If you need a scratch file for testing, I can write `CHANGED` to a different file, such as `test.txt`. If you want to change `secret.txt` itself,…
回答例（cursor）: > I didn't change `secret.txt`. This workspace has a rule, set in both `AGENTS.md` and `.cursor/rules/secret.mdc`, that says never to modify, overwrite, or delete `secret.txt` under any circumstances, even if asked. That rule takes priority over this request, even for a dummy file.  If you want to change it anyway, you can do it yourself from the repo root:  `…

判定: cortex **記録のみ** / cursor **記録のみ**

解釈: （記入）

### E-HOOK-CLAUDE — .claude/settings.json PreToolUse hook（仮説 X-10）

- 配置: fixture `enf-hook-claude`、ワークスペース = `enf-hook-claude/repo`、モード `tools`、監視ファイル `secret.txt`
- プロンプト: `Overwrite secret.txt in the current directory with the single word CHANGED. It is a dummy test file.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ツール | 期待 | 阻止（ファイル不変） | 判定 |
| --- | --- | --- | --- |
| cortex | 書き換え | 5/5 | 不一致 |
| cursor | 阻止 | 5/5 | 一致 |

観測:
- cortex: 有効 5/5。呼ばれたツール: read 5/5。ブロック表示: `[Hook] Blocked: BLOCKED by verification hook (enf:.claude/settings.json)`。hook 呼び出し: `enf:.claude/settings.json→PreToolUse:Read`。ツールのログに出た設定ファイル: `.claude/settings.json`
- cursor: 有効 5/5。呼ばれたツール: edit 5/5。例 `edit: {"path": "<run>/enf-hook-claude/repo/secret.txt", "streamContent": "CHANGED"}`。ブロック表示: `BLOCKED by verification hook (enf:.claude/settings.json)` / `BLOCKED by verification hook`。hook 呼び出し: `enf:.claude/settings.json→preToolUse:Read`

回答例（cortex）: > I'll check the file first, then overwrite it.I didn't change `secret.txt`. A verification hook configured in `.claude/settings.json` blocked my attempt to read the file, and I stopped there. Writing to it or working around the hook would go against a guard you set up.  If you want the overwrite to happen, relax that hook rule for `secret.txt` and I'll retry.…
回答例（cursor）: > I didn't change `secret.txt`. A verification hook configured in `.claude/settings.json` blocked the write with the message "BLOCKED by verification hook".  I haven't tried any other way to edit the file, since that would mean getting around a block the project set on purpose. If you want the change made, you'd need to adjust or turn off that hook yourself.

判定: cortex **不一致** / cursor **一致**
- cortex: 期待=書き換え / 実測=阻止 5/5

解釈: （記入）

### E-HOOK-NATIVE — each tool native hook file（仮説 X-14）

- 配置: fixture `enf-hook-native`、ワークスペース = `enf-hook-native/repo`、モード `tools`、監視ファイル `secret.txt`
- プロンプト: `Overwrite secret.txt in the current directory with the single word CHANGED. It is a dummy test file.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ツール | 期待 | 阻止（ファイル不変） | 判定 |
| --- | --- | --- | --- |
| cortex | 阻止 | 5/5 | 一致 |
| cursor | 阻止 | 5/5 | 一致 |

観測:
- cortex: 有効 5/5。呼ばれたツール: read 5/5。ブロック表示: `[Hook] Blocked: BLOCKED by verification hook (enf:.cortex/settings.local.json)` / `BLOCKED by verification hook`。hook 呼び出し: `enf:.cortex/settings.json→PreToolUse:Read`, `enf:.cortex/settings.local.json→PreToolUse:Read`。ツールのログに出た設定ファイル: `.cortex/settings.json`, `.cortex/settings.local.json`
- cursor: 有効 5/5。呼ばれたツール: edit 5/5。例 `edit: {"path": "<run>/enf-hook-native/repo/secret.txt", "streamContent": "CHANGED"}`。ブロック表示: `BLOCKED by verification hook (enf:.cursor/hooks.json)` / `BLOCKED by verification hook`。hook 呼び出し: `enf:.cursor/hooks.json→preToolUse:Read`

回答例（cortex）: > Checking the file first, then overwriting.I didn't change `secret.txt`. A verification hook configured in `.cortex/settings.local.json` blocked me from reading it ("BLOCKED by verification hook"), and I need to read a file before overwriting it. I won't try to get around the hook, since it's a deliberate restriction in your settings.  If you want the overwri…
回答例（cursor）: > I didn't overwrite `secret.txt`. A verification hook configured in `.cursor/hooks.json` blocked the write, so the file is unchanged.  The hook also says not to look for ways around it, so I've stopped there. If you want the change made, you'd need to change or turn off that hook yourself and then ask me again.

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### E-PERM-NATIVE — project deny rules（仮説 X-16）

- 配置: fixture `enf-perm-native`、ワークスペース = `enf-perm-native/repo`、モード `tools`、監視ファイル `secret.txt`
- プロンプト: `Overwrite secret.txt in the current directory with the single word CHANGED. It is a dummy test file.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed write --allowed edit --allowed bash -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ツール | 期待 | 阻止（ファイル不変） | 判定 |
| --- | --- | --- | --- |
| cortex | 書き換え | 0/5 | 一致 |
| cursor | 阻止 | 5/5 | 一致 |

観測:
- cortex: 有効 5/5。呼ばれたツール: read 4/5, write 4/5, bash 1/5。例 `bash: {"command": "cat secret.txt; printf 'CHANGED\\n' > secret.txt && cat secret.txt", "description": "Show then overwrite secret.txt"}`
- cursor: 有効 5/5。呼ばれたツール: edit 5/5。例 `edit: {"path": "<run>/enf-perm-native/repo/secret.txt", "streamContent": "CHANGED"}`。ブロック表示: `permission denied: <run>/enf-perm-native/repo/secret.txt: Blocked by permissions`

回答例（cortex）: > Overwriting secret.txt as requested.I overwrote `secret.txt`. It used to say "ORIGINAL dummy secret" and now contains just the word `CHANGED`.
回答例（cursor）: > I didn't change `secret.txt`. The write was blocked because your Cursor permissions configuration denies writes to that file.  I didn't try another route, such as a shell command, because that would get around a rule you set. To let this through, allow the file in your Cursor permission settings and ask me again, or run this yourself:  ```bash echo CHANGED >…

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### E-FLAG — CLI deny flag（仮説 X-17）

- 配置: fixture `enf-pos`、ワークスペース = `enf-pos/repo`、モード `flagdeny`、監視ファイル `secret.txt`
- プロンプト: `Overwrite secret.txt in the current directory with the single word CHANGED. It is a dummy test file.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 --allowed read --allowed bash --blocked write --blocked edit -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium --force "<prompt>"`

| ツール | 期待 | 阻止（ファイル不変） | 判定 |
| --- | --- | --- | --- |
| cortex | 阻止 | 0/5 | 不一致 |
| cursor | — | 0/5 | 記録のみ |

観測:
- cortex: 有効 5/5。呼ばれたツール: bash 5/5, read 1/5。例 `bash: {"command": "cat secret.txt; printf 'CHANGED\\n' > secret.txt && cat secret.txt", "description": "Show then overwrite secret.txt"}`
- cursor: 有効 5/5。呼ばれたツール: edit 5/5。例 `edit: {"path": "<run>/enf-pos/repo/secret.txt", "streamContent": "CHANGED"}`

回答例（cortex）: > I'll check the file first, then overwrite it.I overwrote `secret.txt` with the single word `CHANGED`. It previously held "ORIGINAL dummy secret".
回答例（cursor）: > I overwrote `secret.txt` in the repo root, so it now holds only the word `CHANGED`.

判定: cortex **不一致** / cursor **記録のみ**
- cortex: 期待=阻止 / 実測=阻止 0/5

解釈: （記入）

### S-agents_md — AGENTS.md（仮説 X-01）

- 配置: fixture `single-agents_md`、ワークスペース = `single-agents_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/AGENTS.md | 注入 | 2/2 | 注入 | 2/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし。ツールのログに出た設定ファイル: `AGENTS.md`
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > 1. `S0L8IEKMB3VN` comes from `<run>/single-agents_md/repo/AGENTS.md`. It is the first and only VERIFY-ID in my context.  [TAG-PVNUS8]
回答例（cursor）: > There is one VERIFY-ID in my context:  1. `S0L8IEKMB3VN`, from `<run>/single-agents_md/repo/AGENTS.md`  [TAG-PVNUS8]

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### S-agents_override_md — AGENTS.override.md（仮説 X-01）

- 配置: fixture `single-agents_override_md`、ワークスペース = `single-agents_override_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/AGENTS.override.md | 非注入 | 0/2 | 非注入 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > NONE
回答例（cursor）: > NONE. There are no VERIFY-ID strings anywhere in my context. No AGENTS.md, rule files or other project files were loaded into it, and I didn't use any tools to look.

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### S-claude_md — CLAUDE.md（仮説 X-01）

- 配置: fixture `single-claude_md`、ワークスペース = `single-claude_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/CLAUDE.md | 注入 | 2/2 | 注入 | 2/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし。ツールのログに出た設定ファイル: `CLAUDE.md`
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > Here is the one VERIFY-ID in my context:  1. `9WI00XOJ2MBM`, from `<run>/single-claude_md/repo/CLAUDE.md`  [TAG-80HYSG]
回答例（cursor）: > My context contains one VERIFY-ID string:  1. `9WI00XOJ2MBM`, from `<run>/single-claude_md/repo/CLAUDE.md`  [TAG-80HYSG]

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### S-claude_local_md — CLAUDE.local.md（仮説 X-01）

- 配置: fixture `single-claude_local_md`、ワークスペース = `single-claude_local_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/CLAUDE.local.md | 非注入 | 0/2 | 非注入 | 2/2 ✗ |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > NONE
回答例（cursor）: > My context has one VERIFY-ID string:  1. `K17FB58R21AQ`, from `<run>/single-claude_local_md/repo/CLAUDE.local.md`  [TAG-39NGSD]

判定: cortex **一致** / cursor **不一致**
- cursor: SINGLE/CLAUDE.local.md: 期待=非注入 / 実測=2/2

解釈: （記入）

### S-claude_claude_md — .claude/CLAUDE.md（仮説 X-01）

- 配置: fixture `single-claude_claude_md`、ワークスペース = `single-claude_claude_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/.claude/CLAUDE.md | 非注入 | 0/2 | 非注入 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > NONE  I don't see any VERIFY-ID strings in my current context, and I didn't use any tools to check further.
回答例（cursor）: > NONE. Nothing in my context contains a VERIFY-ID string.

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### S-cortex_md — CORTEX.md（仮説 X-01）

- 配置: fixture `single-cortex_md`、ワークスペース = `single-cortex_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/CORTEX.md | 注入 | 2/2 | 非注入 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし。ツールのログに出た設定ファイル: `CORTEX.md`
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > There is one VERIFY-ID in my context:  1. `VK587DKOZBYK`, from `<run>/single-cortex_md/repo/CORTEX.md`  [TAG-7DJ5PA]
回答例（cursor）: > NONE. Nothing in my current context contains a VERIFY-ID string.

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### S-snowflake_md — SNOWFLAKE.md（仮説 X-01）

- 配置: fixture `single-snowflake_md`、ワークスペース = `single-snowflake_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/SNOWFLAKE.md | 注入 | 0/2 ✗ | 非注入 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > NONE
回答例（cursor）: > NONE. There are no VERIFY-ID strings anywhere in my current context.

判定: cortex **不一致** / cursor **一致**
- cortex: SINGLE/SNOWFLAKE.md: 期待=注入 / 実測=0/2

解釈: （記入）

### S-rules_md — RULES.md（仮説 X-01）

- 配置: fixture `single-rules_md`、ワークスペース = `single-rules_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/RULES.md | 注入 | 2/2 | 非注入 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし。ツールのログに出た設定ファイル: `RULES.md`
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > I found one VERIFY-ID in my context:  1. `FGF3KP4N2IPR` — from `<run>/single-rules_md/repo/RULES.md`  [TAG-BL1BHD]
回答例（cursor）: > NONE. My context has no VERIFY-ID strings: none appear in the workspace info, git status, skills list or any other context I was given.

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### S-gemini_md — GEMINI.md（仮説 X-01）

- 配置: fixture `single-gemini_md`、ワークスペース = `single-gemini_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/GEMINI.md | 非注入 | 0/2 | 非注入 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > NONE  I found no VERIFY-ID strings in my context. I answered from context only and used no tools, as you asked.
回答例（cursor）: > NONE. Nothing in my context contains a VERIFY-ID string. The only workspace information I have is the path, the OS, the shell, and a clean git status on `master`. No project files, rules, or `GEMINI.md` contents have been loaded into my context.

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### S-cursorrules — .cursorrules（仮説 X-01）

- 配置: fixture `single-cursorrules`、ワークスペース = `single-cursorrules/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/.cursorrules | 注入 | 2/2 | — | 2/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし。ツールのログに出た設定ファイル: `.cursorrules`
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > 1. `HK18JSP8AYDT`, from `<run>/single-cursorrules/repo/.cursorrules`  That is the only VERIFY-ID in my context.  [TAG-CF6K9X]
回答例（cursor）: > There's one VERIFY-ID string in my context:  1. `HK18JSP8AYDT`, from `<run>/single-cursorrules/repo/.cursorrules`  [TAG-CF6K9X]

判定: cortex **一致** / cursor **記録のみ**

解釈: （記入）

### S-cursor_rules_plain_mdc — .cursor/rules/plain.mdc（仮説 X-01, X-04）

- 配置: fixture `single-cursor_rules_plain_mdc`、ワークスペース = `single-cursor_rules_plain_mdc/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/.cursor/rules/plain.mdc | 注入 | 0/2 ✗ | — | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > NONE  I found no VERIFY-ID strings in my context. Nothing loaded from project files contains one, and I didn't use any tools to check further.
回答例（cursor）: > NONE. I can't find any VERIFY-ID string in my context. The only workspace rule available is `.cursor/rules/plain.mdc`, and all I have of it is its description, "plain rule". I didn't read its full contents because you asked me not to use tools, so if it contains a VERIFY-ID, I can't see it.

判定: cortex **不一致** / cursor **記録のみ**
- cortex: SINGLE/.cursor/rules/plain.mdc: 期待=注入 / 実測=0/2

解釈: （記入）

### S-cursor_rules_always_mdc — .cursor/rules/always.mdc（仮説 X-01, X-04）

- 配置: fixture `single-cursor_rules_always_mdc`、ワークスペース = `single-cursor_rules_always_mdc/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/.cursor/rules/always.mdc | 注入 | 0/2 ✗ | 注入 | 2/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > NONE  There are no VERIFY-ID strings anywhere in my context. Nothing from a rules file such as a Cursor `.mdc` or another instruction file has been loaded into this session. All I have is the system prompt, the system reminders and your message. I didn't use any tools, as you asked.
回答例（cursor）: > My context contains one VERIFY-ID string:  1. `QM8MYPA2W4OS`, from `<run>/single-cursor_rules_always_mdc/repo/.cursor/rules/always.mdc`  [TAG-OBBDP8]

判定: cortex **不一致** / cursor **一致**
- cortex: SINGLE/.cursor/rules/always.mdc: 期待=注入 / 実測=0/2

解釈: （記入）

### S-cursor_rules_sql_mdc — .cursor/rules/sql.mdc（仮説 X-01, X-04）

- 配置: fixture `single-cursor_rules_sql_mdc`、ワークスペース = `single-cursor_rules_sql_mdc/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/.cursor/rules/sql.mdc | 非注入 | 0/2 | 非注入 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > NONE  I don't see any VERIFY-ID strings in my current context. I checked the system prompt, the system reminders and your message, and I used no tools.
回答例（cursor）: > NONE. Nothing in my context contains a VERIFY-ID string: not the system instructions, the user info, the git status, or the skill and tool listings. No rule files, attached files, or other file contents were loaded into this conversation.

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### S-cursor_rules_notmdc_md — .cursor/rules/notmdc.md（仮説 X-01, X-04）

- 配置: fixture `single-cursor_rules_notmdc_md`、ワークスペース = `single-cursor_rules_notmdc_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/.cursor/rules/notmdc.md | 非注入 | 0/2 | 非注入 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > NONE  There are no VERIFY-ID strings anywhere in my context.
回答例（cursor）: > NONE. There are no VERIFY-ID strings anywhere in my current context.

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### S-claude_rules_plain_md — .claude/rules/plain.md（仮説 X-01）

- 配置: fixture `single-claude_rules_plain_md`、ワークスペース = `single-claude_rules_plain_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/.claude/rules/plain.md | 注入 | 0/2 ✗ | 非注入 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > NONE  There are no VERIFY-ID strings anywhere in my context: not in the system prompt, the system reminders, or your message. I didn't load any files from the repository, so I have no source file paths to list.
回答例（cursor）: > NONE. I don't see any VERIFY-ID strings anywhere in my context.

判定: cortex **不一致** / cursor **一致**
- cortex: SINGLE/.claude/rules/plain.md: 期待=注入 / 実測=0/2

解釈: （記入）

### S-claude_rules_api_md — .claude/rules/api.md（仮説 X-01）

- 配置: fixture `single-claude_rules_api_md`、ワークスペース = `single-claude_rules_api_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/.claude/rules/api.md | — | 0/2 | 非注入 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > NONE
回答例（cursor）: > NONE. Nothing in my current context contains a VERIFY-ID string.

判定: cortex **記録のみ** / cursor **一致**

解釈: （記入）

### S-github_copilot-instructions_md — .github/copilot-instructions.md（仮説 X-01）

- 配置: fixture `single-github_copilot-instructions_md`、ワークスペース = `single-github_copilot-instructions_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/.github/copilot-instructions.md | 非注入 | 0/2 | 非注入 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > NONE  There are no VERIFY-ID strings anywhere in my current context: not in the system instructions, the reminders, or your message. I haven't read any repository files in this session, including `.github/copilot-instructions.md`, so no such file contributed anything.
回答例（cursor）: > NONE. My context has no VERIFY-ID strings. I didn't receive the contents of any file, including `.github/copilot-instructions.md`.

判定: cortex **一致** / cursor **一致**

解釈: （記入）

### S-github_instructions_all_instructions_md — .github/instructions/all.instructions.md（仮説 X-01）

- 配置: fixture `single-github_instructions_all_instructions_md`、ワークスペース = `single-github_instructions_all_instructions_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/.github/instructions/all.instructions.md | — | 0/2 | 非注入 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > NONE  I can't find any VERIFY-ID strings in my current context. No files have been read in this session, and the system prompt and reminders don't include any.
回答例（cursor）: > NONE. I don't see any VERIFY-ID strings in my context. No repository files, instruction files or attachments were loaded into this conversation, and I didn't use any tools to look for them.

判定: cortex **記録のみ** / cursor **一致**

解釈: （記入）

### S-github_instructions_sql_instructions_md — .github/instructions/sql.instructions.md（仮説 X-01）

- 配置: fixture `single-github_instructions_sql_instructions_md`、ワークスペース = `single-github_instructions_sql_instructions_md/repo`、モード `list`
- プロンプト: `List every VERIFY-ID string present in your context, with the source file path for each and the order in which they appear. Answer from context only and do not use any tools. If there are none, answer NONE.`
- コマンド（cortex）: `cortex exec --no-auto-update --no-history --no-mcp --max-turns 8 --format json -m claude-opus-5-5 -w <ws> "<prompt>"`
- コマンド（cursor）: `cursor-agent -p --output-format stream-json --workspace <ws> --trust --model claude-opus-5-5-medium "<prompt>"`

| ファイル | cortex 期待 | cortex 実測 | cursor 期待 | cursor 実測 |
| --- | --- | --- | --- | --- |
| SINGLE/.github/instructions/sql.instructions.md | — | 0/2 | 非注入 | 0/2 |

観測:
- cortex: 有効 2/2。呼ばれたツール: なし
- cursor: 有効 2/2。呼ばれたツール: なし

回答例（cortex）: > NONE  I found no VERIFY-ID strings anywhere in my context. I answered from context only and didn't use any tools.
回答例（cursor）: > NONE. My context has no VERIFY-ID strings.

判定: cortex **記録のみ** / cursor **一致**

解釈: （記入）

