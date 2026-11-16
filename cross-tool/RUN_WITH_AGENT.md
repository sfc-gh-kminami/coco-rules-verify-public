# AI エージェントに検証を実行させる手順（Cursor / Claude Code / Codex など）

このキットを、IDE や CLI の AI エージェントに clone から実行・レポート作成まで任せるための手順と、そのまま貼れるプロンプトです。

## 考え方（大事な点）

- **エージェントは「実行係」です。測る対象は、エージェントが起動する CLI のほうです。** たとえば Cursor IDE のエージェントには Cursor CLI（`agent`）を `run.py --tool cursor` で流させます。IDE のエージェント自身の挙動（Cursor IDE がどのルールを読むか）は、自分で自分を測ることになり結果が汚れるため、[MANUAL.md](MANUAL.md) の手作業で別に測ります。
- **実行係に判定を変えさせません。** `expect.py`（期待値）・`fixtures.py`・`cases.py`・`run.py` の判定部分・`report.py` は変更禁止です。CLI のフラグが合わずに動かないときだけ `adapters.py` の修正、または `XTOOL_<TOOL>_EXTRA` の指定を認め、直した内容を報告させます。
- **ユーザースコープ（`~` のファイル入れ替え）は既定では実施しません。** 実施する場合は、人が全ツールを終了してから `user_scope.py` を自分で実行してください。
- **実行係は結果を commit しません。** `results/` と `out/` は `.gitignore` 済みです。公開する場合は、人が中身を確認して伏せ字処理をしてから `results-<日付>/` として追加します（例: [results-2026-11-16/](results-2026-11-16/)）。

## 事前準備（人がやること）

1. 対象の CLI をインストールしてログインしておく（Cursor CLI は公式 docs の手順で入れ、`agent --version` が通ること）。
2. CLI と IDE の自動更新を、検証の間だけ止める（途中でバージョンが変わると結果が混ざります）。
3. 空のフォルダを IDE で開き、エージェント（Agent モード）に下のプロンプトを貼る。

## プロンプト（Cursor 用。`<TOOL>` を変えれば他ツールにも使えます）

````text
あなたはこのタスクの「実行係」です。GitHub の検証キットを clone し、Cursor CLI（agent コマンド）の挙動を測定してレポートを作ってください。あなた自身（Cursor IDE のエージェント）の挙動は測定対象ではありません。

## 手順
1. 作業用フォルダで clone する:
   git clone https://github.com/sfc-gh-kminami/coco-rules-verify-public.git
   cd coco-rules-verify-public/cross-tool
2. cross-tool/README.md と cross-tool/RUN_WITH_AGENT.md を読む。
3. 環境を確認して報告する: `python3 --version`（3.9 以上）、`git --version`、`which agent || which cursor-agent`、`agent --version`、`agent --help` の出力のうちモデル指定・出力形式・権限に関わる部分。agent が無い、またはログインしていない場合は、ここで止めて私に伝える（インストールやログインはしない）。
4. モデルを 1 つに固定する。`agent --help` などで利用可能なモデル名が分かればそれを XTOOL_CURSOR_MODEL に設定し、分からなければ未設定（既定モデル）のまま進めて、その旨を報告する。
5. ダミー環境を作る: `python3 fixtures.py`（既にあれば `--force`）。/tmp/xtool-verify 以外には書き込まない。
6. 動作確認（各 1 試行）:
   python3 run.py --tool cursor --cases 'D-ALL-W1,H-NATIVE,E-POS,E-HOOK-CLAUDE' --n 1
   結果の判定:
   - /tmp/xtool-verify/results/cursor.jsonl の各行の rc・valid・stderr_tail・cmd を確認する。
   - D-ALL-W1 の answer が空、または valid=false なら、stderr_tail を見て原因を特定する。CLI の引数エラーなら adapters.py の Cursor クラスだけを最小限に直す（何をなぜ直したか記録する）。
   - E-POS（制御なし）で secret.txt が書き換わっていない場合、ヘッドレスでツールが承認されていない可能性がある。その場合に限り `XTOOL_CURSOR_FORCE=1`（--force を付ける）を設定して E-POS をやり直し、それで書き換わるなら以降もこの設定で実行し、報告に明記する。
   - 動作確認の結果は消して本番に進む: `rm -f /tmp/xtool-verify/results/cursor.jsonl && rm -rf /tmp/xtool-verify/results/raw/cursor-*`
7. 本番（プロジェクトスコープ全ケース。約 120 試行、1 時間前後）。ターミナルのタイムアウトを避けるため、バックグラウンドで実行してログを見る:
   nohup python3 run.py --tool cursor --parallel 2 > /tmp/xtool-cursor-run.log 2>&1 &
   数分ごとに `tail -5 /tmp/xtool-cursor-run.log` と `grep -c '^\[' /tmp/xtool-cursor-run.log` で進み具合を確認し、`done:` が出るまで待つ。途中で同じエラーが続く場合は止めて原因を報告する。
8. レポートを作る:
   python3 summarize.py && python3 report.py
   mkdir -p out && cp /tmp/xtool-verify/results/report.md /tmp/xtool-verify/results/summary.md /tmp/xtool-verify/results/cursor.jsonl out/
9. 私への報告（日本語）:
   - 実施環境（Cursor CLI のバージョン、モデル、試行数、無効数、XTOOL_* の設定、adapters.py を直したならその差分）
   - out/report.md の「仮説判定」表の要約と、docs と不一致だったケースの一覧（数値つき）
   - 特に次の点: どの指示ファイルが注入されたか（.cursor/rules の alwaysApply / globs / description、AGENTS.md、CLAUDE.md、サブディレクトリ）、どの hook 設定ファイルが発火したか（.cursor/hooks.json と .claude/settings.json）、E-* の阻止回数
   - 判定できなかったケースとその理由

## 守ること
- expect.py、fixtures.py、cases.py、report.py、summarize.py、run.py の判定ロジックは変更しない。期待と結果が違っても、それが測定結果なので直さない。
- `--yolo` や `--dangerously-*` は使わない（例外は手順 6 の XTOOL_CURSOR_FORCE=1 のみ）。
- user_scope.py は実行しない（ホームディレクトリのファイルを入れ替えるため）。
- 書き換えてよいのは /tmp/xtool-verify 以下と、このリポジトリの cross-tool/out/ と adapters.py（必要な場合のみ）だけ。git commit / push はしない。
- 結果に推測を混ぜない。数値は out/report.md と results の記録から引用する。
````

## Claude Code 用

Claude Code の対話セッション（実行係）から、測定対象の `claude -p`（ヘッドレス）を `run.py --tool claude` で起動します。実行係のセッション自体は測定対象ではありません。

```sh
git clone https://github.com/sfc-gh-kminami/coco-rules-verify-public.git
cd coco-rules-verify-public
claude
```

起動したら、次の 1 文を入力します。

```text
cross-tool/RUN_WITH_AGENT.md の「Claude Code 用の指示」に従って、Claude Code CLI の検証を最後まで実行し、日本語で報告してください。
```

### Claude Code 用の指示（実行係が読む部分）

上の「プロンプト（Cursor 用）」の手順と「守ること」に、次の読み替えで従う。

- 測定対象は Claude Code CLI（`claude -p`）。`agent` → `claude`、`--tool cursor` → `--tool claude`、`XTOOL_CURSOR_*` → `XTOOL_CLAUDE_*`、`cursor.jsonl` / `raw/cursor-*` → `claude.jsonl` / `raw/claude-*`、ログ名 `/tmp/xtool-cursor-run.log` → `/tmp/xtool-claude-run.log`。
- 手順 3 の確認コマンドは `which claude`、`claude --version`、`claude --help`（`-p`、`--output-format`、`--model`、`--allowedTools`、`--disallowedTools`、`--no-session-persistence`、`--debug-file` があるか）。
- 手順 4 のモデルは、`claude --help` やエラーメッセージで分かる正式なモデル名を XTOOL_CLAUDE_MODEL に設定する（例: Opus 系）。分からなければ未設定で進め、報告する。
- 手順 6 で Cursor の `XTOOL_CURSOR_FORCE` に当たるものはない。E-POS で secret.txt が書き換わらない場合は、stderr_tail と cmd を見て `--allowedTools` の指定を adapters.py の Claude クラスで最小限に直す。`--dangerously-skip-permissions` は使わない。
- **入れ子起動の確認**: 動作確認で、内側の `claude -p` が「別の Claude Code セッションの中では起動できない」といった趣旨のエラーで失敗した場合は、回避策を勝手に試さず、そこで止めて私に伝える（私が普通のターミナルから `python3 run.py --tool claude` を実行する）。
- 手順 9 の「特に次の点」は、CLAUDE.md と AGENTS.md の関係（D-PAIR、S-agents_md）、CLAUDE.local.md・.claude/CLAUDE.md・.claude/rules（paths あり／なし）、gitルートより上、サブディレクトリの遅延読込（T-READ-DOCS、T-EDIT-TS）、どの hook 設定ファイルが発火したか（.claude/settings.json と他ツールのファイル）、matcher（M-*）、`.claude/settings.json` の `permissions.deny`（E-PERM-NATIVE）と `--disallowedTools`（E-FLAG）の阻止回数、に置き換える。
- 結果は `cross-tool/out/` に置き、commit / push はしない。

## 他のツールで使う場合

プロンプト中の `agent` / `--tool cursor` / `XTOOL_CURSOR_*` / `cursor.jsonl` を置き換えてください。

| ツール | 実行ファイル | `--tool` | 環境変数の接頭辞 | 動作確認で E-POS が書き換わらないとき |
| --- | --- | --- | --- | --- |
| Claude Code | `claude` | `claude` | `XTOOL_CLAUDE_` | `--allowedTools` の指定を確認（`adapters.py`） |
| Codex CLI | `codex` | `codex` | `XTOOL_CODEX_` | `--sandbox workspace-write` で書けるか確認。プロジェクト hook を試すなら `XTOOL_CODEX_TRUST_HOOKS=1` |
| Copilot CLI | `copilot` | `copilot` | `XTOOL_COPILOT_` | `--allow-tool` の書式を確認 |
| CoCo CLI | `cortex` | `cortex` | `XTOOL_CORTEX_` | `--allowed` の指定を確認 |

同じ PC で複数ツールを流した場合、結果は同じ `/tmp/xtool-verify/results/` に溜まり、`report.py` が横並びにします。別の PC の結果をまとめるときは、各 PC の `results/*.jsonl` と `results/raw/` を 1 か所に集めてから `report.py` を流してください（fixture は同じ `mapping.json` を使う必要があるため、`fixtures.py` を作り直さず `fixtures/` ごとコピーします）。
