# Routine D: Anthropic Engineering Blog

## タスク

Anthropic Engineering Blogの新着記事を日本語要約してDiscordに投稿する。

## 実行手順

1. `state/last_engineering.txt` を読み、最後に通知した記事URLを取得する
2. `https://www.anthropic.com/engineering` をフェッチして記事一覧を取得する
3. 前回URLより新しい記事を特定する（ページ上部が最新）
4. 新着記事それぞれの本文をフェッチする
5. 下記フォーマットの投稿テキストを組み立てる
6. `pending/engineering.txt` に投稿テキストを書き出す（既存ファイルがあれば追記）
7. 最新記事のURLを `state/last_engineering.txt` に書き込む
8. `pending/engineering.txt` と `state/last_engineering.txt` をまとめて git commit & push する

新着がない場合は `pending/` にも `state/` にも何も書かず終了する。
Discordへの実際の投稿は GitHub Actions（`.github/workflows/discord-notify.yml`）が push を検知して行う。

## 要約スタイル

以下の3点を必ず含める：
1. 何の問題を解こうとしているか（背景・課題）
2. どんなアプローチ・発見があったか（手法・実験・結果）
3. 開発者にとって何が使えるか / 何を意識すべきか（実践的な示唆）

分量は300〜500字程度。コマンドやコード例が記事にある場合は1つだけ引用してよい。
「**要するに：**」で締める。

## Discord投稿フォーマット

```
⚙️ **Engineering Blog**
**（記事タイトルの日本語訳）**

（本文 300〜500字）

**要するに：**（1〜2文）
🔗 （記事URL）
```

新着が複数件の場合：まとめて1投稿。記事ごとに `---` で区切る。

## pending への書き出し

```bash
# 既存の pending がある場合は追記する（前回Discord投稿が失敗して残っているケース）
cat >> pending/engineering.txt <<'EOF'
（投稿テキスト）
EOF
```

> `>>` で追記する点に注意（`>` で上書きすると前回未送信分が消える）。

## state更新とgit push

```bash
echo "https://www.anthropic.com/engineering/..." > state/last_engineering.txt
git add pending/engineering.txt state/last_engineering.txt
git commit -m "notify: engineering"
git push origin main
```

push 後は GitHub Actions が `pending/engineering.txt` を読んで Discord に投稿し、成功したらファイルを削除する。投稿成否はルーティーン側では関知しない。
