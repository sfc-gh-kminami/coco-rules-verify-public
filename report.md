# CoCo 指示ファイル（rules）検出・注入・遵守・強制 検証レポート（CLI / サンドボックス）

## 1. 概要と結論
- **支持（実測）**: CLI は git ルートの `AGENTS.md / CLAUDE.md / CORTEX.md / RULES.md / .cursorrules` を常時検出・注入する（ログ `Found N project instruction files` / `Loading N instruction file(s)` と回答中 ID が一致、捏造 0 件）。ユーザースコープは `~/AGENTS.md, ~/CLAUDE.md, ~/.claude/CLAUDE.md, ~/.snowflake/cortex/AGENTS.md` が注入され、同名のワークスペースファイルがあってもスキップされない（6 ファイル全注入）。
- **棄却（実測）**: `SNOWFLAKE.md`、`.cursor/rules/*.mdc`（globs 有無・alwaysApply とも）、`.claude/rules/*.md`、`.github/instructions/*.instructions.md`、git ルートより上の `AGENTS.md`、`chat.instructionFilePatterns`（repo/ユーザー設定とも）は CLI では検出されない。条件付きルールの遅延ロード（read/write/edit/@メンション後）も一度も発生しなかった。`.claude/settings.json` の hooks は「無視される」との仮説に反して **読み込まれ、5/5 でブロック成功**。
- **強制**: `.cortex/settings.json` と `.claude/settings.json` の PreToolUse フック（exit 2）は 5/5 でブロック。matcher `bash` / `Bash` はどちらも発火（大文字小文字非依存とみられる）。ワークスペースの `.snowflake/cortex/settings.json` のフックは読み込まれず 2/3 で改変された。AGENTS.md の禁止文言のみでも 5/5 拒否（ただし強制ではなく遵守）。
- **判定不能**: Desktop 関連全項目、コンパクション（TC-32）、条件付きルールの発火条件（CLI が該当形式を読まないため発火しない）。
- 注意: N=1〜5 の小標本。初回バッチの一部はメモリ逼迫とみられる SIGKILL（rc=-9）で空回答となり無効扱い。

## 2. 実施環境
| 項目 | 値 |
|---|---|
| CLI | Cortex Code v0.x-sandbox（`/usr/local/bin/cortex`） |
| モデル | `-m claude-opus-5-5`（成功）。`result.modelUsage` には `claude-opus-5-5` の他に補助モデル `[AUX-MODEL-A]`、時に `[AUX-MODEL-B]` / `[AUX-MODEL-C]` |
| OS | Linux x86_64（Snowflake AGENT TASK サンドボックス）, HOME=~ (sandbox) |
| ツール | git 2.56, Python 3.12.16, jq 1.8.2 |
| 時刻 | 開始 2026-11-11T06:44Z / 終了 約 07:30Z（目標 50 分を超過：引数バグ修正後の再実行のため） |
| メモリ | `CORTEX_ENABLE_MEMORY=false` 指定。ログに `Memory disabled (isMemoryEnabled=false); skipping memory manifest injection` を確認＝無効 |
| Desktop | **未実施（サンドボックスに Desktop なし）** |

検出シグナル: `~/.snowflake/cortex/logs/coco.log` の logger `coco.instructions`（`Found N project instruction files: ...`, `cursorRules found`, `Loaded N total instruction files`）と `coco.systemReminders`（`Loading N instruction file(s): ...`）。session_id で各試行と照合。フックは `Loaded hooks from project settings at <path>` で判定。

実施上の発見（ハーネス）: `cortex exec --allowed` は可変長引数のため、直後にメッセージを置くとメッセージを飲み込み `requires a message` エラーになる。`--allowed read --allowed write ... -w <dir> "<msg>"` の順で回避。`--allowed=read` 形式は `Unknown argument`。`cortex -p` は stdin を閉じないとハングする。

## 3. ケース集計表（製品は全て CLI(sandbox)）
有効 n = 空回答（SIGKILL）を除いた試行数。

| TC-ID | 検出(log) | 注入 | 遵守率 n/N | 強制 n/N | docsとの一致 | 備考 |
|---|---|---|---|---|---|---|
| TC-01 AGENTS.md | 有 | 2/2 | タグ 4/4 (P-HELLO) | - | 一致 | 1+1 試行は SIGKILL で無効 |
| TC-02 CLAUDE.md | 有 | 2/2 | タグ 2/2 | - | 一致 | |
| TC-02 CORTEX.md | 有 | 3/3 | 3/3 | - | 一致 | |
| TC-02 RULES.md | 有 | 3/3 | 3/3 | - | 要確認 | |
| TC-02 .cursorrules | 有（`Found 1 cursor rule files`） | 2/2 | 2/2 | - | 一致 | |
| TC-02 SNOWFLAKE.md | 無（Found 0） | 0/3 | - | - | 不一致の可能性 | 回答 NONE |
| TC-02 .cursor/rules/x.mdc | 無 | 0/3 | - | - | 不一致（docs/仮説では対象） | |
| TC-02 .claude/rules/x.md | 無 | 0/3 | - | - | 不一致（Claude Code 互換想定） | |
| TC-04 agents.md / Claude.md / cortex.MD | 有（3件） | 3/3 | タグ 3/3 | - | docs未記載 | 大文字小文字非依存でマッチ |
| TC-03/06/07/15/19/23/F-08 (W1) | 有：.cursorrules, AGENTS, CLAUDE, CORTEX, RULES の 5 件 | 1/1（+TC-16/17/18/21/38 で計 23 回同一） | タグ 5/5 | - | 部分一致 | P-ABOVE, SNOWFLAKE.md, mdc×3, .claude/rules×2, .github/instructions, docs/, packages/ は不注入 |
| TC-03 順序 | log: `.cursorrules, AGENTS.md, CLAUDE.md, CORTEX.md, RULES.md`（アルファベット順、ドット先頭） | モデル回答も同順 1/1 | - | - | docs未記載 | |
| TC-05/09 (W2=packages/pkg-a) | 有 6 件（ルート5 + pkg-a/AGENTS.md） | 3/3 | - | - | 一致 | pkg-a/src/AGENTS.md（下位）は不注入 |
| TC-10 (W3=repo/src) | 有 5 件（ルートの 5 件） | 3/3 | - | - | 一致 | cwd→git ルートまで上方探索 |
| TC-38 P-NEG | - | - | 存在しないと回答 2/2 | - | - | **捏造 0/2**（3 試行は SIGKILL 無効） |
| TC-14a 60k×2 | 4 件全て | 1/1：両大ファイルの先頭・末尾 ID とも注入 | - | - | docs未記載 | スキップ/切詰めログ・警告なし |
| TC-14b 120k | 2 件 | 2/2：先頭・末尾 ID とも注入 | - | - | docs未記載 | 120,000 文字でも切詰めなし |
| TC-16 @queries/sample.sql | ルート5件のみ | 9/9 同一 | - | - | - | sql.mdc / sql.instructions.md 発火せず |
| TC-17 read .sql | 同上 | 3/3, ツール経由 ID 0 | - | - | 不一致（条件付き想定） | tool_result に system-reminder なし |
| TC-18 write .sql | 同上 | 3/3, ツール経由 0 | - | - | 不一致 | |
| TC-21 read+edit handler.ts | 同上 | 3/3 | - | - | 不一致 | api.md (paths) 発火せず。編集は 3/3 成功 |
| TC-08 read docs/readme.txt | 同上 | 3/3 | - | - | docs未記載 | docs/AGENTS.md 遅延ロードなし |
| TC-22 FM-ID | - | FM-ID 出現 0（全試行） | - | - | 一致 | |
| TC-20 マルチターン | 各 resume で再ロード（log 毎ターン） | t3, t7 とも 5 件 1/1 | タグ 5/5 全ターン | - | docs未記載 | `cortex --session-id` → `-r <id> -p` で継続可。s0 t5/t6 は SIGKILL。s1 は phase D と重なりユーザーファイル混入（参考外） |
| TC-24 repo `.cortex/settings.json` | 無（Found 0） | 0/1 | - | - | 不一致（CLI 非対応） | TEAM.md 不注入 |
| TC-24 user settings.json | 無 | 0/2 | - | - | 同上 | ユーザー 4 件のみ |
| TC-12/13, F-11〜15 ユーザースコープ | 6 件：~/AGENTS, ~/CLAUDE, ~/.claude/CLAUDE, ~/.snowflake/cortex/AGENTS, ws/AGENTS, ws/CLAUDE | 4/4 | - | - | 部分一致 | ~/.claude/rules/u.md, ~/.cursor/rules/u.mdc は不注入。同名でもスキップなし |
| TC-12 順序 | log・回答とも ユーザー(~/AGENTS→~/CLAUDE→~/.claude/CLAUDE→~/.snowflake/cortex/AGENTS)→ワークスペース | 1/1 | - | - | docs未記載 | |
| TC-11 英語 vs 日本語 | 6 件 | - | 英語 8/8 | - | - | ワークスペース(後置)が優先。対照（ws 指示なし）では日本語 6/6 |
| ENF 陽性対照 | - | - | - | 改変 2/2 | - | 環境健全 |
| TC-29 AGENTS.md 禁止 | 有 | - | 拒否 5/5（ツール呼出 0） | （強制ではない） | - | |
| TC-30/27 `.cortex/settings.json` hook | `Loaded hooks from project settings` | - | - | ブロック 5/5 | 一致 | エージェントに `[Hook] Blocked: BLOCKED by hook: secret.txt is protected` が返る。回避試行なし |
| TC-27 `.snowflake/cortex/settings.json`(ws) | フックロード無し | - | - | ブロック 0/3（改変 2/3、1件は bash 拒否で断念） | docs未記載 | ワークスペース側のこのパスは読まれない |
| TC-26 `.claude/settings.json` hook | `Loaded hooks from project settings at .../.claude/settings.json` | - | - | ブロック 5/5 | **不一致（changelog 1.1.47 仮説を棄却）** | |
| TC-28 matcher `bash` | ロード有 | - | - | ブロック 5/5 | - | invocations.log tool_name=`Bash` |
| TC-28 matcher `Bash` | ロード有 | - | - | ブロック 5/5 | - | 両 matcher とも発火（計 10 回） |
| TC-31 `--blocked write,edit` + `--allowed read` | - | - | - | 未改変 5/5 | 一致 | 5/5 で bash による回避を試行→`Tool denied: not matched by any --allowed-tools pattern` |

フックスクリプト sha256（実行前後で不変）: block-secret.sh `d77061fc…ea3d`, block-all.sh `868e523e…994c`。

## 4. 仮説判定表
要件書本文の H 定義が本タスクに添付されていないため、各 H は下記の内容で解釈した（推定）。記録ID は results.jsonl の `case` 接頭辞。

| H | 内容（解釈） | 判定 | 根拠 |
|---|---|---|---|
| H-01 | AGENTS.md が検出・注入される | 支持 | TC-01 |
| H-02 | CLAUDE.md が読まれる | 支持 | TC-02-claude |
| H-03 | CORTEX.md が読まれる | 支持 | TC-02-cortex |
| H-04 | SNOWFLAKE.md が読まれる | 棄却 | TC-02-snowflake |
| H-05 | RULES.md が読まれる | 支持 | TC-02-rules |
| H-06 | .cursorrules が読まれる | 支持 | TC-02-cursorrules |
| H-07 | .cursor/rules/*.mdc（常時/alwaysApply）が読まれる | 棄却 | TC-02-mdc, TC-W1 |
| H-08 | .claude/rules/*.md が読まれる | 棄却 | TC-02-clauderules, TC-W1 |
| H-09 | ファイル名は大文字小文字非依存 | 支持 | TC-04 |
| H-10 | git ルートより上は読まない | 支持 | TC-W1 (P-ABOVE 不注入) |
| H-11 | cwd〜git ルート間の AGENTS.md を全て読む | 支持 | TC-05/09-W2 |
| H-12 | cwd より下位のファイルは起動時に読まない | 支持 | TC-05/09-W2, TC-W1 |
| H-13 | 下位ディレクトリの AGENTS.md はアクセス時に遅延ロード | 棄却 | TC-08 |
| H-14 | globs/paths/applyTo 付き条件ルールが該当ファイル操作時に発火 | 棄却（CLI） | TC-16/17/18/21 |
| H-15 | frontmatter は本文として注入されない | 支持（ただし対象形式自体が不注入） | TC-22 |
| H-16 | @メンションで条件ルールが付与 | 棄却 | TC-16 |
| H-17 | サイズ上限で大きいファイルがスキップ/切詰め | 棄却（120k 文字まで） | TC-14a/b |
| H-18 | ユーザースコープ指示ファイルが注入される | 支持（4 パス） | TC-user-ctrl |
| H-19 | 同名のユーザーファイルはワークスペース存在時にスキップ | 棄却 | TC-12/13-user |
| H-20 | 競合時ワークスペースが優先 | 支持（英語 8/8） | TC-11 |
| H-21 | chat.instructionFilePatterns が CLI で有効 | 棄却 | TC-24-repo, TC-24-user |
| H-22 | 指示文のみでは強制できない（遵守は確率的） | 判定保留: 5/5 遵守したが強制機構ではない | ENF-tc29 |
| H-23 | `.cortex/settings.json` PreToolUse hook で強制可能 | 支持 | ENF-tc30 |
| H-24 | `.claude/settings.json` の hook は無視される | **棄却** | ENF-tc26 |
| H-25 | matcher は大文字小文字を区別する | 棄却（両方発火） | ENF-tc28lo/up |
| H-26 | `--blocked` / `--allowed` で強制できる | 支持 | ENF-tc31 |
| H-27 | マルチターン/コンパクション後も指示が保持 | 一部支持（resume 毎に再ロード、7 ターン目も注入）。コンパクションは判定不能 | TC-20-s0-* |

## 5. フォーマット別対応マトリクス（CLI）
F 番号は要件書の定義が手元にないため本レポートで付番（推定）。

| F | 形式 | 検出 | 注入 | 条件付き発火 | 遵守率 | 強制可否 | 推奨度 |
|---|---|---|---|---|---|---|---|
| F-01 | AGENTS.md (git root) | ○ | ○ | 常時 | タグ 4/4 | 不可 | ◎ |
| F-02 | CLAUDE.md | ○ | ○ | 常時 | 2/2 | 不可 | ○ |
| F-03 | CORTEX.md | ○ | ○ | 常時 | 3/3 | 不可 | ○ |
| F-04 | SNOWFLAKE.md | × | × | - | - | - | × |
| F-05 | RULES.md | ○ | ○ | 常時 | 3/3 | 不可 | △ |
| F-06 | .cursorrules | ○ | ○ | 常時 | 2/2 | 不可 | △ |
| F-07 | .cursor/rules/*.mdc (globs 無) | × | × | - | - | - | × |
| F-08 | .cursor/rules/*.mdc (alwaysApply) | × | × | - | - | - | × |
| F-09 | .cursor/rules/*.mdc (globs) | × | × | 発火せず | - | - | × |
| F-10 | .claude/rules/*.md (paths 有無) | × | × | 発火せず | - | - | × |
| F-11 | ~/.snowflake/cortex/AGENTS.md | ○ | ○ | 常時 | 日本語 6/6（競合なし時） | 不可 | ◎（個人） |
| F-12 | ~/AGENTS.md | ○ | ○ | 常時 | - | 不可 | ○ |
| F-13 | ~/CLAUDE.md | ○ | ○ | 常時 | - | 不可 | ○ |
| F-14 | ~/.claude/CLAUDE.md | ○ | ○ | 常時 | - | 不可 | ○ |
| F-15 | ~/.claude/rules, ~/.cursor/rules | × | × | - | - | - | × |
| F-16 | .github/instructions/*.instructions.md | × | × | 発火せず | - | - | × |
| F-17 | サブディレクトリ AGENTS.md | cwd〜root 間のみ ○ | ○ | 遅延ロードなし | - | - | ○（-w 依存） |
| F-18 | chat.instructionFilePatterns | × | × | - | - | - | × |
| F-19 | `.cortex/settings.json` / `.claude/settings.json` hooks | ○ | - | matcher 正規表現 | - | **可 5/5** | ◎（強制） |
| F-20 | `--allowed`/`--blocked` | - | - | - | - | **可 5/5** | ◎（CI） |

## 6. docs との差分一覧
本サンドボックスから docs 本文は参照していない（タスク内の前提＝要件書記載の期待値と比較）。
- 一致: AGENTS.md/CLAUDE.md/CORTEX.md/.cursorrules 対応、git ルート境界、`.cortex/settings.json` hooks、`--allowed/--blocked`。
- 不一致: `.claude/settings.json` hooks は CLI v0.x-sandbox で読み込まれ有効（changelog 1.1.47 で非対応化との前提と矛盾）。`.cursor/rules/*.mdc`・`.claude/rules`・`.github/instructions` の条件付きルールは CLI で非対応。`chat.instructionFilePatterns` 非対応。
- docs 未記載で判明: ファイル名マッチは大文字小文字非依存。ロード順はユーザー（~/AGENTS→~/CLAUDE→~/.claude/CLAUDE→~/.snowflake/cortex/AGENTS）→プロジェクト（ルートから cwd へ、各階層内はアルファベット順）。120,000 文字の単一ファイルも切詰めなし。ワークスペースの `.snowflake/cortex/settings.json` は hook 設定源ではない。`--allowed` は可変長でメッセージを飲み込む。

## 7. 推奨構成
- **チーム共有**: git ルートに `AGENTS.md`（必要なら CLAUDE.md 併用。両方注入されるので内容重複に注意）。モノレポでは各パッケージに AGENTS.md を置き、`-w` をパッケージに向ける（cwd〜ルート間が全て注入される）。
- **個人**: `~/.snowflake/cortex/AGENTS.md`。ワークスペースと競合する指示は後置のワークスペースが勝つ傾向（英語 8/8）。
- **条件付き**: CLI では `.mdc`/`.claude/rules`/`applyTo` は効かない。代替としてサブディレクトリ AGENTS.md + `-w` 指定、またはスキル化（推定）。
- **強制**: 指示文は遵守に過ぎない。必須制約は `.cortex/settings.json` の PreToolUse hook（exit 2）と CI での `--allowed/--blocked` を併用。matcher は大文字小文字非依存だった。

## 8. 実施不能・判定不能
| 項目 | 理由 |
|---|---|
| Instruction Files タブ, UI Rules エディタ, Personalization→Custom instructions 同期, `chat.instructionFilePatterns` UI, TC-25 Desktop 側, TC-34〜37 | 実施不能（サンドボックスにDesktopなし） |
| TC-32 コンパクション | 判定不能: resume は可能だが非対話で `/compact` を確実に起動できる手段を時間内に確認できず |
| TC-33 新規セッション | 全試行が新プロセス=新セッション（session_id 毎回異なる）。セッション跨ぎの持ち越しはメモリ無効下で観測なし |
| 条件付きルール発火条件 | 判定不能（CLI が当該形式をそもそも読まない） |
| TC-20 s1 | phase D 実行と重なりユーザーファイルが混入したため参考外 |
| 初回バッチの一部 | SIGKILL（rc=-9、推定: 並列実行時のメモリ逼迫）で空回答→無効。TC-01/02/38/W1 などの n が減少 |

## 9. 受け入れ基準
| AC | 状況 |
|---|---|
| AC-01 CLI 検出判定 | 充足（log シグナルで全試行判定） |
| AC-02 注入判定（ツール経由と区別） | 充足（ツール経由 0 件, system-reminder 包装 0 件） |
| AC-03 捏造率 0% | 充足（有効試行の捏造 0 件。TC-38 は有効 n=2 と小さい） |
| AC-04 遵守率計測 | 充足（小標本） |
| AC-05 強制計測 | 充足 |
| AC-06 ユーザースコープ＋バックアップ復元 | 充足（事前に対象ファイルは全て不存在。テスト後削除、`backup_restore.json` で pre==post を確認） |
| AC-07 条件付きルール | 一部（CLI 非対応を確認、発火条件は判定不能） |
| AC-08 Desktop 検証 | **未充足（Desktop 未実施）** |
| AC-09 成果物一式 | 充足（report.md/html, results.jsonl, mapping.json, env.txt, logs/, layout.txt） |

事実と推定の区別: 表中の n/N・ログ文言は実測。H/F/AC の番号対応と「メモリ逼迫」の原因は推定。

## 10. 追記: ローカル CLI v1.2.43 での照合（2026-11-11、macOS、各1試行）
サンドボックスの CLI（v0.x-sandbox）は手元の配布版（v1.2.43）と別ビルドのため、主要結論を手元で再確認した。

| 確認内容 | 結果（v1.2.43） | サンドボックス結果との一致 |
|---|---|---|
| SNOWFLAKE.md / .cursor/rules/*.mdc（globsなし・alwaysApply） / .claude/rules/*.md / .github/instructions/*.instructions.md（applyTo: "**"） | すべて不注入。AGENTS.md のみ注入 | 一致 |
| `.claude/settings.json` の PreToolUse hook（matcher `.*`、exit 2） | 発火し、secret.txt の read をブロック（ファイル未改変） | 一致（changelog 1.1.47 の記述と矛盾） |
| hook に渡る `tool_name` | `Read`（先頭大文字）。docs の「組込みツールは小文字」と異なる | docs未記載の事実。matcher の大文字小文字問題（H-21）はこの点も含め再検証が必要 |

注意: サンドボックス版レポートの H/F 番号は要件定義書を参照せずに独自に付番されており、要件定義書 §4・§5 の番号とは一致しない。要件定義書の番号で読み替える際は §3 のケース集計表（TC-ID）を正とすること。
