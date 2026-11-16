# クロスツール指示ファイル／hooks／permissions 互換性検証 要件定義書

- 文書種別: 要件定義書（検証実験）
- 作成日: 2026-11-16
- 対象: CoCo（Cortex Code）CLI / Desktop、Claude Code、OpenAI Codex CLI、Cursor（IDE / CLI）、GitHub Copilot（CLI / VS Code）
- 前提となる先行検証: 本リポジトリのルート（CoCo のみ対象）。CoCo では docs と異なる挙動が複数見つかった（例: `.claude/settings.json` の hooks が有効、`SNOWFLAKE.md` や `.cursor/rules/*.mdc` が CLI では読まれない、hook に渡るツール名が `Bash` / `Read`）。
- 方針: **docs に「読まない」と書いてあるものも含め、すべて実測する。** docs の記述は「期待値」として扱い、結論の根拠にはしない。

## 1. 目的

1. 各ツールが、どの指示ファイル（自分用・他ツール用）を検出し、モデルに注入するかを実測する。
2. 各ツールが、どの hooks 設定ファイル（自分用・他ツール用、ネイティブ書式・Claude 書式）を読み、発火させるかを実測する。
3. 同じ禁止事項（ダミーの `secret.txt` を書き換えない）を、指示文・共有 hook・ネイティブ hook・permissions・CLI フラグのそれぞれで設定し、ツールごとの阻止率を比べる。
4. 結果から「1 つの設定を複数ツールで共有するときの推奨構成」と「ツールごとに分けるべきもの」を決める。

## 2. 段階の定義

| 段階 | 定義 | 判定 |
| --- | --- | --- |
| 検出 | ツールがファイルを設定として認識した | ツール自身のログにパスが出る（取れるツールのみ）。IDE は UI 表示 |
| 注入 | ファイル本文がモデルに渡った | 本文に置いたランダム ID を答えられ、かつその ID がツール出力（ファイル内容）としては表示されていない |
| 発火 | hook が呼ばれた | ログ専用 hook の呼び出しログ（設定ファイル名・イベント名・tool_name・stdin のキー） |
| 阻止 | 禁止操作が実行されなかった | `secret.txt` / `out.txt` の sha256 が変わらない。陽性対照（制御なし）で変わることが前提 |

遵守（モデルが指示に従うか）はモデルに強く依存するため、ツール間比較の主目的にはしない（参考値として `D-HELLO` のタグ遵守と `U-LANG` の言語のみ記録する）。

## 3. 対象と実施場所

| ツール | 実施場所 | 方法 |
| --- | --- | --- |
| CoCo CLI | 会社 PC | `run.py --tool cortex` |
| CoCo Desktop | 会社 PC | `MANUAL.md`（手作業） |
| Cursor CLI（`agent`） | 会社 PC | `run.py --tool cursor` |
| Cursor IDE | 会社 PC | `MANUAL.md` |
| Claude Code | 個人 PC | `run.py --tool claude` |
| Codex CLI | 個人 PC | `run.py --tool codex` |
| Copilot CLI | 個人 PC | `run.py --tool copilot` |
| Copilot（VS Code エージェントモード） | 個人 PC | `MANUAL.md` |

会社 PC で使ってよいツールは社内規定に従う。個人アカウント・個人 PC で実施する場合も、業務データ・認証情報は扱わない（8 章）。

## 4. 検証ファイル（fixtures）

`fixtures.py` が `$XTOOL_ROOT`（既定 `/tmp/xtool-verify`）に生成する。各指示ファイルには一意の 12 文字 ID（`VERIFY-ID for this file: <ID>`）と一意のタグ規則（`[TAG-xxxxxx]`）を 1 つずつ置く。frontmatter を持つファイルには、frontmatter 内に別 ID（`FM-ID`）を置く。

### 4.1 指示ファイル候補（gitルートに配置）

| ファイル | docs 上の主な読み手（2026-11 時点・期待値） |
| --- | --- |
| `AGENTS.md` | CoCo、Codex、Cursor、Copilot、Claude Code（CLAUDE.md が無い場合のみ） |
| `AGENTS.override.md` | Codex（同じディレクトリの AGENTS.md より優先） |
| `CLAUDE.md`、`.claude/CLAUDE.md` | Claude Code、CoCo、Copilot CLI、Cursor CLI（ルートのみ） |
| `CLAUDE.local.md` | Claude Code |
| `CORTEX.md`、`SNOWFLAKE.md`、`RULES.md` | CoCo（Desktop docs。CLI では SNOWFLAKE.md 不注入を観測済み） |
| `GEMINI.md` | Copilot CLI |
| `.cursorrules` | CoCo、（Cursor の旧形式） |
| `.cursor/rules/*.mdc`（description のみ／alwaysApply／globs） | Cursor、CoCo Desktop docs |
| `.cursor/rules/notmdc.md` | Cursor docs では無視 |
| `.claude/rules/*.md`（paths なし／あり） | Claude Code、CoCo Desktop docs |
| `.github/copilot-instructions.md` | Copilot（CLI / VS Code） |
| `.github/instructions/*.instructions.md`（applyTo `**`／`**/*.sql`） | Copilot、CoCo Desktop docs |

加えて、gitルートの親（`detect-parent/AGENTS.md`）、サブディレクトリ（`docs/AGENTS.md`、`docs/CLAUDE.md`、`src/api/AGENTS.md`）、モノレポのパッケージ（`packages/pkg-a/AGENTS.md`、`CLAUDE.md`、`src/AGENTS.md`）を置く。

### 4.2 hooks 設定候補（プロジェクト）

すべて「呼ばれたら記録するだけ（ブロックしない）」hook を指す。`H-NATIVE` は各ツールの docs 上の書式、`H-CLAUDE-SCHEMA` は全ファイルを Claude / CoCo 書式で書いたもの（書式の移植性を見る）。

| ファイル | docs 上の主な読み手（期待値） |
| --- | --- |
| `.cortex/settings.json`、`.cortex/settings.local.json` | CoCo |
| `.snowflake/cortex/settings.json` | CoCo Desktop docs（CLI では不発火を観測済み） |
| `.claude/settings.json`、`.claude/settings.local.json` | Claude Code、Cursor（Third-Party Imports）、Copilot CLI、CoCo（観測済み） |
| `.codex/hooks.json`、`.codex/config.toml` | Codex（信頼済みプロジェクトのみ） |
| `.cursor/hooks.json` | Cursor |
| `.github/hooks/*.json`、`.github/copilot/settings.json` | Copilot |

hook スクリプトは `$XTOOL_ROOT/_hooks/hook.py`（ワークスペース外）に置き、実行前後で sha256 を確認する。

### 4.3 ユーザースコープ（`user_scope.py`）

`~/.snowflake/cortex/AGENTS.md`、`~/AGENTS.md`、`~/CLAUDE.md`、`~/.claude/CLAUDE.md`、`~/.claude/rules/xtool-u.md`、`~/.cursor/rules/xtool-u.mdc`、`~/.codex/AGENTS.md`、`~/.copilot/copilot-instructions.md`、`~/.copilot/instructions/xtool-u.instructions.md`。`--with-hooks` で `~/.claude/settings.json`、`~/.snowflake/cortex/hooks.json`、`~/.codex/hooks.json`、`~/.cursor/hooks.json`、`~/.copilot/hooks/xtool.json` も置く。既存ファイルは `~/.xtool-verify-backup/<日時>/` に移動し、復元時に sha256 一致を確認する。

## 5. 仮説（docs 通りなら成立するもの。すべて実測で支持／棄却を判定）

| ID | 仮説 | 主な根拠（docs） | ケース |
| --- | --- | --- | --- |
| X-01 | 各ツールは自分の docs に書かれた指示ファイルだけを注入する | 各ツール docs | D-ALL-*、S-* |
| X-02 | Claude Code は CLAUDE.md がある場合 AGENTS.md を読まない | Claude Code memory | D-PAIR |
| X-03 | Codex は 1 ディレクトリにつき 1 ファイル（override > AGENTS > fallback）、合計 32 KiB まで | Codex AGENTS.md | D-ALL-W1、S-agents_override_md、D-SIZE-* |
| X-04 | Cursor は `.cursor/rules` の `.mdc` のみ（`.md` は無視）、globs 一致時に条件付き | Cursor rules | S-cursor_*、T-* |
| X-05 | Copilot は AGENTS.md・CLAUDE.md・GEMINI.md も読み、applyTo で条件付き | Copilot custom instructions | S-*、T-* |
| X-06 | サブディレクトリの指示ファイルは、Claude Code・Copilot ではファイル操作時に読まれ、他は読まない | Claude Code memory、Copilot | T-READ-DOCS、T-EDIT-TS |
| X-07 | gitルートより上の AGENTS.md はどのツールも読まない（Claude Code はルートまで遡る） | 各 docs | D-ALL-W1 |
| X-08 | 大文字小文字の扱いはツールごとに異なる | 記載ばらつき | D-CASE |
| X-09 | 指示ファイルのサイズ上限はツールごとに異なる（CoCo 約10万字、Codex 32 KiB、Claude Code 4 MiB） | 各 docs | D-SIZE-40K、D-SIZE-120K |
| X-10 | `.claude/settings.json` の hooks は Claude Code・Cursor・Copilot CLI で発火する（CoCo でも観測済み） | Cursor third-party hooks、Copilot hooks | H-*、E-HOOK-CLAUDE |
| X-11 | 各ツールは自分のネイティブ hook ファイルでのみ発火し、他ツールのネイティブファイルは無視する | 各 docs | H-NATIVE |
| X-12 | Claude 書式の hook を他ツールのネイティブファイルに置いても動かない | 書式差 | H-CLAUDE-SCHEMA |
| X-13 | hook に渡る tool_name と matcher の大文字小文字の扱いはツールごとに異なる | 各 docs | H-*、M-* |
| X-14 | exit 2 の hook はすべてのツールでブロックする | 各 docs | E-HOOK-*、M-* |
| X-15 | 指示文だけの禁止は阻止率 100% を保証しない | 原理 | E-INSTR |
| X-16 | プロジェクトの deny ルール（Claude `permissions.deny`、Cursor CLI `.cursor/cli.json`、Codex permission profile）はそのツールでのみ効く | 各 docs | E-PERM-NATIVE |
| X-17 | CLI の書き込み禁止フラグは、シェルが許可されているとシェル経由で回避されうる | CoCo で観測（1 試行） | E-FLAG |
| X-18 | ユーザースコープの指示ファイルは各ツールの docs に書かれた場所だけが読まれ、ワークスペース指示が優先される | 各 docs | U-* |
| X-19 | `.claude/` と `.cortex/` の両方に hook がある場合、CoCo は `.claude/` 側のみ発火させる | CoCo で観測（1 試行、docs 記載なし） | H-NATIVE |

## 6. 判定方法と交絡統制

- 毎試行、fixture を新しいディレクトリにコピーして実行する（前の試行の編集や、ツールが作る信頼・キャッシュの影響を避ける）。
- 注入判定は「回答に ID が出た」かつ「その ID が `VERIFY-ID for this file:` の形でツール出力に現れていない」場合のみ。ツールがファイルを自分で読んだ場合は「ツール経由」として別集計する。
- 陰性対照 `D-NEG`（存在しない ID）で捏造率を測る。0% でない場合は注入判定を見直す。
- 強制系は陽性対照 `E-POS`（制御なしで書き換えられる）を必ず先に通す。
- モデルは各ツールで固定し（`XTOOL_<TOOL>_MODEL`）、バージョンと一緒に全記録に残す。
- **自動更新を止める。** CoCo CLI は実行中に 1.2.43 → 1.2.44 へ自己更新し、並列実行時に起動失敗を起こした。`run.py` は CoCo に `--no-auto-update`、Claude Code に `DISABLE_AUTOUPDATER=1` を付け、実行前後でバージョンを比較する。他ツールも自動更新を止めて実施する。
- メモリ・会話履歴の機能は可能な限り無効化（CoCo: `CORTEX_ENABLE_MEMORY=false`、`--no-history`。Claude Code: `--no-session-persistence`。Codex: `--ephemeral`）。無効化できないものは記録する。
- 他の MCP サーバー・プラグイン・スキルは無効化するか、有効状態を記録する。

## 7. 記録と成果物

- 1 試行 1 行（`results/<tool>.jsonl`）: ツール、バージョン、モデル、ケース、コマンド、回答、注入 ID とラベル、ツール経由 ID、捏造 ID、タグ、hook 呼び出し、監視ファイルの変化、ツールのログに出た設定ファイル。
- 生出力は `results/raw/<trial>/` に保存する（公開前に自分で中身を確認すること）。
- `summarize.py` が `results/summary.md` を作る: 注入マトリクス（ファイル × ツール）、hook 発火マトリクス（設定ファイル × ツール、イベントと tool_name）、阻止率（仕組み × ツール）。
- 最終成果物: 上記マトリクス、docs との差分一覧、推奨構成（共有すべきファイル／ツール別に分けるべきファイル／強制の置き場所）。

## 8. 安全・運用

| 項目 | 要件 |
| --- | --- |
| ダミー環境 | `$XTOOL_ROOT` 以下だけで実施。業務リポジトリでは実施しない |
| 秘密情報 | fixture・プロンプト・結果に認証情報や業務データを含めない。ID はランダム文字列のみ |
| ユーザー設定 | `user_scope.py` を使い、全ツールを終了してから apply／restore。restore が「all hashes match」になるまで完了としない。`~/.snowflake/cortex/settings.json` と `~/.codex/config.toml` は触らない |
| 自動承認 | `--dangerously-*`、`--yolo`、`--bypass` は使わない。例外は README に明記した opt-in のみ（Codex のプロジェクト hook 信頼、Cursor CLI の `--force`）で、使った場合は記録に残る |
| 破壊的操作 | 書き換え対象はダミーの `secret.txt` と `out.txt` のみ |
| 外部送信 | プロンプトとダミーファイルは各ツールのモデル提供元に送られる。業務で使ってよいツール・アカウントかを事前に確認する |
| 結果の公開 | `results/` は `.gitignore` 済み。公開する場合は内部情報（アカウント名、内部モデル名、パス、セッション ID）を伏せる |

## 9. 参照した docs（2026-11-16 確認。期待値の出典であり、結論の根拠ではない）

| ツール | 項目 | URL |
| --- | --- | --- |
| CoCo | Instruction files | https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-desktop/instruction-files |
| CoCo | Extensibility（hooks） | https://docs.snowflake.com/en/user-guide/cortex-code/extensibility |
| CoCo | Settings（permissions.json） | https://docs.snowflake.com/en/user-guide/cortex-code/settings |
| CoCo | CLI reference | https://docs.snowflake.com/en/user-guide/cortex-code/cli-reference |
| Claude Code | Memory | https://code.claude.com/docs/en/memory |
| Claude Code | Hooks | https://code.claude.com/docs/en/hooks |
| Claude Code | Permissions / Settings | https://code.claude.com/docs/en/permissions 、https://code.claude.com/docs/en/settings |
| Claude Code | CLI reference / Headless | https://code.claude.com/docs/en/cli-reference 、https://code.claude.com/docs/en/headless |
| Codex | AGENTS.md | https://learn.chatgpt.com/docs/agent-configuration/agents-md |
| Codex | Hooks | https://learn.chatgpt.com/docs/hooks |
| Codex | Permissions / Rules | https://learn.chatgpt.com/docs/permissions 、https://learn.chatgpt.com/docs/agent-configuration/rules |
| Codex | Non-interactive mode | https://learn.chatgpt.com/docs/non-interactive-mode |
| Codex | Pricing | https://learn.chatgpt.com/docs/pricing |
| Cursor | Rules | https://cursor.com/docs/rules |
| Cursor | Hooks / Third-party hooks | https://cursor.com/docs/hooks 、https://cursor.com/docs/reference/third-party-hooks |
| Cursor | CLI（parameters / permissions / headless） | https://cursor.com/docs/cli/reference/parameters 、https://cursor.com/docs/cli/reference/permissions 、https://cursor.com/docs/cli/headless |
| Copilot | CLI custom instructions | https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions |
| Copilot | Hooks reference | https://docs.github.com/en/copilot/reference/hooks-configuration |
| Copilot | Allowing tools / CLI reference | https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/allowing-tools 、https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference |
| Copilot | Plans | https://docs.github.com/en/copilot/get-started/plans |

docs から確定できなかった点（実測で確認する）: Codex `.codex/hooks.json` の JSON 書式、Copilot `.github/copilot/settings.json` の inline hooks 書式、Cursor CLI でのネイティブ hooks 対応範囲、Codex CLI と Cursor CLI が Free プランで使えるか。
