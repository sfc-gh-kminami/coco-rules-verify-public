# CoCo CLI 指示ファイル検証 — ローカル再検証（v1.2.43）

- 実施: 2026-11-11（macOS 26.6.2、Cortex Code CLI v1.2.43、`-m claude-opus-5-5`、`CORTEX_ENABLE_MEMORY=false`、`--no-history --no-mcp`）
- 方法: サンドボックス検証（`../report.md`）と同じハーネス（`harness.py` / `setup.py` / `runabc.py` / `phaseD.py`）をパスだけ書き換えて使用。原則 N=5。
- 試行: 176 件（無効 0 件）。結果は `results.jsonl`、各試行の生ログは `logs/`、集計は `summary.txt`。
- ユーザースコープ: `~/AGENTS.md` などを一時作成し、終了後に削除。`backup_restore.json` で前後のハッシュ一致（match=true）を確認。既存の `~/.snowflake/cortex/settings.json` と `hooks.json` は変更していない。
- 注入の判定: ツールを使わせずに VERIFY-ID を列挙させる。ツール結果経由の ID は除外。陰性対照（存在しない ID）での捏造は 0/5。

## 結果（n/N は有効試行）

### 検出・注入
| TC | 配置 | v1.2.43 | サンドボックス v0.x-sandbox |
| --- | --- | --- | --- |
| TC-01 | AGENTS.md | 注入 5/5、タグ 5/5（hello 5/5） | 同じ |
| TC-02 | CLAUDE.md / CORTEX.md / RULES.md / .cursorrules | 各 5/5 注入・タグ遵守 | 同じ |
| TC-02 | SNOWFLAKE.md / .cursor/rules/x.mdc / .claude/rules/x.md | 各 0/5 | 同じ |
| ログ | 探索パターン | `using patterns: ["AGENTS.md","CLAUDE.md","CORTEX.md","RULES.md",".cursorrules"]` | 記載なし |
| TC-04 | agents.md / Claude.md / cortex.MD | 3ファイルとも 5/5（大文字小文字を区別しない） | 同じ |
| TC-W1 | gitルートの親の AGENTS.md（P-ABOVE） | **注入 5/5** | 不注入（違い） |
| 追加 | gitルートの 1〜3 階層上 | 3階層上まですべて注入 2/2 | 未実施 |
| 追加 | git 管理外のディレクトリ | 作業ディレクトリのみ。親は読まない 2/2 | 未実施 |
| 追加 | 入れ子の git（outer/inner） | 両方注入 2/2 | 未実施 |
| TC-05/09 | packages/pkg-a を作業ディレクトリに | ルート5件＋pkg-a/AGENTS.md＋P-ABOVE 5/5。pkg-a/src/AGENTS.md は不注入 | 上方向は gitルートまで |
| TC-07/08 | docs/AGENTS.md（起動時・docs 内ファイルを read 後） | 不注入 5/5（遅延読込なし） | 同じ |
| TC-10 | repo/src を作業ディレクトリに | 上方向に探索して 6 件 5/5 | 同じ（gitルートまで） |
| TC-14a/b | 6万字×2、12万字×1 | 先頭・末尾の ID まで全文注入 5/5。スキップ・警告なし | 同じ |
| TC-24 | `.cortex/settings.json` の `chat.instructionFilePatterns: ["TEAM.md"]` | TEAM.md 不注入 0/5（NONE と回答） | 同じ |
| TC-38 | 陰性対照 | 「存在しない」5/5、捏造 0 | 同じ（有効 2） |

### 条件付きルール・遅延読込
| TC | 操作 | v1.2.43 |
| --- | --- | --- |
| TC-16 | `@queries/sample.sql` をメンション | sql.mdc / sql.instructions.md 不注入 0/5 |
| TC-17 | read で .sql を読む | 不注入 0/5 |
| TC-18 | write で .sql を新規作成 | 不注入 0/5 |
| TC-21 | handler.ts を read＋edit（`.claude/rules/api.md` の paths に一致） | 編集は 5/5 成功、api.md は不注入 0/5 |

### ユーザースコープ
| TC | 内容 | v1.2.43 |
| --- | --- | --- |
| TC-12/13 | ws の AGENTS.md・CLAUDE.md と ~/AGENTS.md・~/CLAUDE.md・~/.claude/CLAUDE.md・~/.snowflake/cortex/AGENTS.md | 6件すべて注入 5/5（同名でもユーザー版をスキップしない） |
| F-14/15 | ~/.claude/rules/u.md、~/.cursor/rules/u.mdc | 不注入 0/5 |
| 注入順 | ログと回答 3/3 | ~/AGENTS.md → ~/CLAUDE.md → ~/.claude/CLAUDE.md → ~/.snowflake/cortex/AGENTS.md → ワークスペース（上の階層から順、同じ階層内はドット始まり→アルファベット順） |
| TC-11 | ws「英語で」と ~/.snowflake/cortex「日本語で」 | 英語 5/5。対照（ws に指示なし）は日本語 5/5。矛盾時は後から入るワークスペース側が勝つ |

### 強制（hooks / permissions）
| TC | 仕組み | v1.2.43 |
| --- | --- | --- |
| 陽性対照 | 制御なし | 書き換え 3/3 |
| TC-29 | AGENTS.md の指示文だけで禁止 | 未改変 5/5（ツール呼び出し 0。モデルが従っただけ） |
| TC-30 | `.cortex/settings.json` PreToolUse（`edit\|write`、exit 2） | ブロック 5/5 |
| TC-26 | `.claude/settings.json` のみ | ブロック 5/5（changelog 1.1.47 と矛盾） |
| TC-27b | ワークスペースの `.snowflake/cortex/settings.json` | ブロック 0/5（書き換え 5/5。hook が読まれない） |
| TC-28 | matcher `bash` / `Bash` | どちらもブロック 5/5。hook に渡る tool_name は `Bash`・`Write`（先頭大文字）。matcher は大文字小文字を区別しない模様 |
| TC-31 | `--blocked write,edit` ＋ `--allowed read` | 未改変 5/5（bash での回避を 5/5 試み、許可外として拒否） |

## サンドボックス結果からの変更点
1. **gitルートより上も読む（v1.2.43）**。git 管理下では作業ディレクトリから上方向に、少なくとも3階層上まで AGENTS.md 等を読む。git 管理外では作業ディレクトリだけ。サンドボックス v0.x-sandbox は gitルートで止まっていた。
2. それ以外の主要結論（読まれる5形式、条件付きルールなし、同名スキップなし、ユーザー→ワークスペースの順、上限なし、`.claude/settings.json` の hook 有効、matcher の大小無視、ws の `.snowflake/cortex/settings.json` は無効、`--blocked` 有効）は、N=5 でローカルでも再現した。

## 注意・限界
- gitルートより上の探索が「どこで止まるか」（ホームまでか、ファイルシステムのルートまでか）は未確認。ホーム配下のリポジトリで作業すると、`~/AGENTS.md` がユーザー指示とプロジェクト指示の両方として二重に入る可能性がある（未検証）。
- Desktop は未実施。条件付きルール（globs / applyTo）や `chat.instructionFilePatterns` は Desktop docs の記述であり、CLI で効かないことは Desktop で効かないことを意味しない。
- compaction 後の残存、UI の Rules の保存先は未検証。
- 試行数は N=5（追加ケースは 2）。率ではなく件数で扱う。
