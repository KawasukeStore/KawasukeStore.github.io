# 川助商店 (kawasuke store) サイト

App Store で公開している iOS アプリの紹介サイト。公開先: https://kawasukestore.github.io/

## 仕組み
- `build.py` が `i18n/` の各アプリデータと `public/assets/` の素材から、`public/` 以下に全ページ（9言語）と `robots.txt` / `sitemap.xml` / `llms.txt` を生成する静的サイトジェネレータ。
- `main` に push すると GitHub Actions（`.github/workflows/deploy.yml`）が `python build.py` を実行し、`public/` を GitHub Pages へ自動デプロイする。手元でのビルドやデプロイ作業は不要。

## 編集方法
- アプリの文言・料金・アップデート情報は `build.py` の `APPS` と `i18n/<slug>.json`、AI向けの要約・FAQは `i18n/<slug>.llmo.json` を編集する。
- 画像は `public/assets/`（アイコン `icons/`、スクショ `screens/`、家紋 `kamon.png`）に置く。
- 生成される HTML はコミットしない（`.gitignore` 済み。Actions 側で毎回生成）。

## ローカルで確認する場合
```
python build.py
# public/ をブラウザで開く、または簡易サーバ: python -m http.server -d public
```

公開URLを変える場合は `build.py` 先頭の `SITE` を書き換える（canonical / sitemap / llms.txt / 構造化データに反映）。
