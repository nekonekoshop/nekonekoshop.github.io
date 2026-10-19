# ねこねこショップ☆ お知らせHP

| ページ | ファイル |
|---|---|
| お知らせ（ランク・おまとめ特典・画風・発送・Q&A） | `index.html` |
| 制作可能キャラ一覧（検索・五十音インデックス付き） | `list.html` |

## よくある更新

- **お知らせを追加する**：`index.html` の `<ul class="news">` の一番上に `<li>` を1行足す。古いものは「過去のお知らせ」（`<details class="older">`）へ移す。
- **発送お休み日**：`index.html` の `class="holiday"` の文章を書き換える。
- **キャラ一覧を更新する**：ODS を編集してから、下のコマンドを実行する（`assets/data/chars.js` が作り直される）。
  ```
  python tools/build_list.py
  ```
  表記ゆれの統合は `ALIAS`、版権NG作品は `NG`、外すキャラは `NG_CHARS` で調整する。
- **アイコンやロゴを変えたとき**：`index.html` を直したあとに `python tools/sync_sprite.py` を実行すると、`list.html` にも反映される。

## 公開（GitHub Pages）

1. GitHub のアカウントを作り、Public リポジトリ（例：`nekoneko-shop`）を作成する。
2. このフォルダの中身（`tools` フォルダと README は無くても動く）をリポジトリにアップロードする。
3. リポジトリの Settings → Pages で「Deploy from a branch」→ `main` / `(root)` を選んで保存する。
4. 数分後に `https://<ユーザー名>.github.io/nekoneko-shop/` で見られるようになる。
5. `D:\出品csv\商品説明.txt` のリンク先を新しいURLに差し替える。

※ GitHub の規約により、露骨な成人向け画像は載せない（画風見本も今の程度にとどめる）。
