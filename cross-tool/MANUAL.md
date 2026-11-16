# IDE での手作業検証（Cursor IDE / Copilot in VS Code / CoCo Desktop）

CLI と同じ fixture・プロンプトを使い、結果を同じ形式で `results/` に記録します。

## 共通の手順（1 試行ごと）

```sh
cd cross-tool
python3 fixtures.py                              # 未作成なら
python3 record_manual.py prepare --case D-ALL-W1
```

1. 表示されたフォルダを IDE で **新しいウィンドウのワークスペースとして開く**（前の試行のウィンドウは閉じる）。
2. **新しいチャット**を開き、エージェントモードにして、表示されたプロンプトを一字一句そのまま貼る。
3. 「mode」の指示どおりにツール実行の許可・拒否をする（`list` は全部拒否）。
4. 回答をテキストファイルに保存し、記録する。

```sh
python3 record_manual.py record --tool cursor-ide --trial <表示された trial> --answer-file answer.txt \
  --model "<IDE に表示されているモデル>" --version "<IDE のバージョン>" --screenshot <任意>
```

ツール名は `cursor-ide` / `copilot-vscode` / `coco-desktop` を使ってください（CLI の結果と別の列になります）。

## 優先して実施するケース

| 優先 | ケース | 試行数 | 目的 |
| --- | --- | --- | --- |
| 1 | `D-ALL-W1` | 3 | 全候補ファイルのうち何が注入されるか |
| 1 | `D-NEG` | 3 | 捏造しないことの確認（陰性対照） |
| 1 | `E-POS` → `E-HOOK-CLAUDE` → `E-HOOK-NATIVE` | 各 3 | 陽性対照を通してから、共有 hook とネイティブ hook の阻止 |
| 2 | `H-NATIVE`、`H-CLAUDE-SCHEMA` | 各 2 | どの hook 設定ファイルが発火するか（`_hooks/invocations.log` に残る） |
| 2 | `T-MENTION-SQL`、`T-EDIT-TS`、`T-READ-DOCS` | 各 2 | 条件付きルール・サブディレクトリの遅延読込 |
| 3 | `S-*` | 各 1 | 個別ファイル |
| 3 | `U-*` | 各 2 | `user_scope.py apply` 後に実施。終わったら必ず `restore` |

`T-MENTION-SQL` は、プロンプト先頭の `@queries/sample.sql` を IDE の @メンション機能で付け直してください（テキストのままだと添付になりません）。

## 画面で確認して記録するもの

| IDE | 見る場所 | `--note` に書く内容 |
| --- | --- | --- |
| Cursor IDE | Settings → Rules（ルール一覧と状態）、Hooks タブ、Output パネルの「Hooks」チャネル、Third-Party Imports 設定の値 | 一覧に出たルール・hook のファイル名 |
| Copilot in VS Code | チャットの「References / 使用した指示」、Output → GitHub Copilot Chat、設定 `chat.instructionsFilesLocations` 等の値 | 参照された指示ファイル名 |
| CoCo Desktop | Agent Settings → Rules → Instruction Files タブ、Hooks 画面 | 表示されたファイルとスコープ |

画面の表示と、ID で判定した注入結果が一致するかも比べてください（表示されたのに注入されない、またはその逆があれば重要な差分です）。

## 注意

- 検証中は、他のプロジェクトの指示やメモリ機能が混ざらないよう、IDE のメモリ／カスタム指示（ユーザールール）を空にするか、内容を記録してください。Cursor のユーザールールは UI 上の設定で、ファイルではありません。
- モデルは試行間で変えないでください。Auto 選択しかできない場合は、その旨を `--model "auto"` として記録します。
- ツール実行の承認ダイアログで「常に許可」を選ぶと、以降の試行に影響します。毎回「今回だけ許可」を選んでください。
