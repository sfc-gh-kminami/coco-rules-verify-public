# coco-rules-verify

Cortex Code (CoCo) CLI がどの指示ファイル（AGENTS.md / CLAUDE.md / CORTEX.md / RULES.md / .cursorrules など）を読み込むか、hooks や `--blocked` が実際に効くかを実測した検証セットです。

| ディレクトリ | 実行環境 | CLI |
|---|---|---|
| `/`（ルート） | Snowflake AGENT TASK サンドボックス | v0.x-sandbox |
| `local-1.2.43/` | macOS ローカル（N=5、176 runs） | v1.2.43 |

- レポート: `coco-rules-verify-report.html`, `report.md`, `local-1.2.43/report-local.md`, `local-1.2.43/coco-rules-verify-local-report.html`
- 生データ: `results.jsonl`（1行=1実行）、`mapping.json`（VERIFY-ID とファイルの対応）
- ハーネス: `harness.py`, `setup.py`, `runabc.py`, `phaseD.py` ほか

## 再実行（ローカル）

```sh
cd local-1.2.43
export CORTEX_BIN=$(which cortex)
python3 setup.py    # /tmp/coco-verify-local/ に検証用ワークスペースを作成
python3 runabc.py   # ワークスペーススコープのケースを実行 → results.jsonl
python3 phaseD.py   # ユーザースコープのケース（~ 配下を一時的に変更）
```

ユーザースコープ（`~/AGENTS.md` など）に一時ファイルを置くケースがあります。実行前にスクリプトを読み、バックアップ／復元の挙動（`backup_restore.json`）を確認してください。

## 伏せ字について

公開のため、次の情報を置換しています。

| 表記 | 元の内容 |
|---|---|
| `[AUX-MODEL-A/B/C]` | modelUsage に出てくる補助モデル名 |
| `[REDACTED]` | session_id |
| `[CLOUD-AUTOMATION-TASK]` | 実行に使ったクラウド自動化タスク名 |
| `~` | ホームディレクトリの絶対パス（サンドボックスの HOME を含む） |
| `v0.x-sandbox` | サンドボックスの CLI ビルド番号 |
| `(redacted)` | サンドボックスの環境変数名一覧、ホスト・カーネル情報 |

生ログ（`logs/`）は含めていません。
