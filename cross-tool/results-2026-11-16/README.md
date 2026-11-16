# 実測結果（2026-11-16）: CoCo CLI と Cursor CLI

`cross-tool/` のキットを、同じ fixture（`mapping.json`）・同じプロンプトで 2 つの CLI に流した結果です。

| ファイル | 中身 |
| --- | --- |
| [report.md](report.md) | 実験記録（仮説判定表、配置したファイル、ケースごとのコマンド・期待・実測・観測・回答例・判定）。`report.py` の出力 |
| [summary.md](summary.md) | 横並びの集計表（`summarize.py` の出力） |
| `cortex.jsonl` / `cursor.jsonl` | 1 試行 1 行の生記録 |
| `cursor-E-PERM-NATIVE-schema-error.json` | Cursor の E-PERM-NATIVE 初回 5 試行（`.cursor/cli.json` の設定検証エラーで起動しなかった記録。集計からは除外） |
| `mapping.json` | VERIFY-ID とファイルの対応 |

## 実施条件

| 項目 | CoCo CLI | Cursor CLI |
| --- | --- | --- |
| バージョン | Cortex Code v1.2.44（`--no-auto-update`） | 2026.11.13-eacade1 |
| モデル | `claude-opus-5-5` | `claude-opus-5-5-medium` |
| 試行 | 123（無効 0） | 123（無効 0。E-PERM-NATIVE は fixture 修正後に再実行） |
| ツール許可 | `--allowed read/write/edit/bash`（ケースに応じて） | `--force`（下記） |
| 実施 | macOS、2026-11-16 | 同左 |
| 対象 | プロジェクトスコープ全 44 ケース（ユーザースコープ `U-*` は未実施） | 同左 |

Cursor CLI はヘッドレス実行で、実施者の `~/.cursor/cli-config.json`（`approvalMode: allowlist`、許可 `Shell(ls)` のみ）にないシェルコマンドを理由なしで拒否したため、CoCo で全ツールを許可したのと条件をそろえる目的で `--force` を付けました。`--force` でも hooks と `permissions.deny` は効きました。

## 主な結果（数値は有効試行の回数。詳細と docs との比較は report.md）

| 項目 | CoCo CLI 1.2.44 | Cursor CLI |
| --- | --- | --- |
| 注入された指示ファイル | AGENTS.md / CLAUDE.md / CORTEX.md / RULES.md / .cursorrules（各 3/3） | AGENTS.md / CLAUDE.md / CLAUDE.local.md / .cursorrules / `.cursor/rules/always.mdc`（alwaysApply）（各 3/3） |
| 読まれなかったもの | SNOWFLAKE.md、AGENTS.override.md、CLAUDE.local.md、.claude/CLAUDE.md、GEMINI.md、`.cursor/rules/*.mdc` 全種、`.claude/rules/*.md`、copilot-instructions.md、`.instructions.md` | CORTEX.md、SNOWFLAKE.md、RULES.md、AGENTS.override.md、.claude/CLAUDE.md、GEMINI.md、description のみ・globs の `.mdc`、`.claude/rules/*.md`、copilot-instructions.md、`.instructions.md` |
| `.mdc` の globs（`**/*.sql`） | 不注入 | @メンション・読む・作る のどれでも不注入（0/2） |
| gitルートより上の AGENTS.md | 不注入（0/3） | 注入（3/3） |
| サブディレクトリの AGENTS.md / CLAUDE.md | 起動時も操作後も不注入 | 起動時は不注入。そのディレクトリのファイルを読む／編集すると注入（2/2） |
| パッケージをワークスペースにした場合 | パッケージとルートの両方 | 同左 |
| AGENTS.md と CLAUDE.md の同時配置 | 両方注入 | 両方注入 |
| サイズ（4 万字 × 2、12 万字 × 2） | どちらも末尾まで注入 | 4 万字は末尾まで、12 万字は末尾の ID が出ない（途中で切れる） |
| 発火した hook 設定（全候補を同時配置） | `.claude/settings.json`、`.claude/settings.local.json` のみ（`.cortex/` は不発火）| `.cursor/hooks.json`、`.claude/settings.json`、`.claude/settings.local.json` |
| `.cortex/settings.json` だけに hook | 発火・阻止 5/5 | — |
| `.claude/settings.json` の matcher | `bash`・`Bash` が一致、`shell`・`Shell` は不一致 | `Bash`・`Shell` が一致、`bash`・`shell` は不一致（hook に渡る tool_name は `Shell`） |
| 阻止: `.claude/settings.json` の hook | 5/5 | 5/5 |
| 阻止: 各ツールのネイティブ hook | 5/5（`.cortex/settings.json`） | 5/5（`.cursor/hooks.json`） |
| 阻止: プロジェクトの deny ルール | 0/5（`.claude/settings.json` の `permissions.deny` は効かない） | 5/5（`.cursor/cli.json`。`allow` キーが必須） |
| 阻止: CLI の禁止フラグ | 0/5（`--blocked write,edit` を bash で回避） | 対応するフラグなし |
| 阻止: 指示文のみ | 5/5（モデルがツールを使わず拒否） | 5/5（同左） |
| 陽性対照（制御なし） | 書き換え 2/2 | 書き換え 2/2 |
| 捏造（存在しない ID） | 0/5 | 0/5 |

## 伏せ字

公開のため、次を置換しています。

| 表記 | 元の内容 |
| --- | --- |
| `~` | 実施者のホームディレクトリの絶対パス |
| `$XTOOL_ROOT` | `/tmp/xtool-verify`（macOS では `/private/tmp/xtool-verify`） |
| `[PROFILE]` | CoCo 起動時に表示された自動適用プロファイル名 |
| `<email>` | メールアドレス（今回の記録には含まれていませんでした） |

ツールの生出力（`results/raw/`）と hook の呼び出しログ（`_hooks/invocations.log`。Cursor は stdin に `user_email` を含む）は入れていません。

## 注意

- 各ケース 2〜5 試行の小標本です。率ではなく回数で読んでください。
- CoCo の期待値は Desktop docs に基づくため、CLI では「docs と不一致」が多く出ます（CLI 専用の仕様が docs に無いため）。
- CoCo の E-PERM-NATIVE は `.cursor/cli.json` 修正前の fixture で実施しました。CoCo はこのファイルを読まないため結果への影響はないと考えていますが、厳密には fixture が異なります。
- 各ケースの「解釈」欄は空です。
