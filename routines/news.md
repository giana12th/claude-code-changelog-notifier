# Routine B: Anthropic News

## タスク

Anthropic Newsの新着記事を日本語要約してDiscordに投稿する。

## 実行手順

1. `state/last_news.txt` を読み、最後に通知した記事URLを取得する
2. `https://www.anthropic.com/news` をフェッチして記事一覧を取得する
3. 前回URLより新しい記事を特定する（ページ上部が最新）
4. 新着記事それぞれの本文をフェッチする
5. 下記フォーマットの投稿テキストを組み立てる
6. `pending/news.txt` に投稿テキストを書き出す（既存ファイルがあれば追記）
7. 最新記事のURLを `state/last_news.txt` に書き込む
8. `pending/news.txt` と `state/last_news.txt` をまとめて作業ブランチに commit & push し、main 向けの PR を作成する

新着がない場合は `pending/` にも `state/` にも何も書かず終了する。
PR 作成後の auto-merge と Discord 投稿は GitHub Actions が行う。ルーティーン側では関知しない。

## 要約スタイル

- 何の発表か1文で書く
- 背景・詳細を2〜3文で補足する
- 固有名詞・製品名は英語のまま残す

## Discord投稿フォーマット

新着が1件の場合：

```
📢 **Anthropic ニュース**
**（記事タイトルの日本語訳）**
（2〜3文の要約）
🔗 （記事URL）
```

新着が複数件の場合：まとめて1投稿。記事ごとに空行で区切る。

```
📢 **Anthropic ニュース**
**（タイトル1）**
（要約）
🔗 （URL1）

**（タイトル2）**
（要約）
🔗 （URL2）
```

## pending への書き出し

```bash
# 既存の pending がある場合は追記する（前回Discord投稿が失敗して残っているケース）
cat >> pending/news.txt <<'EOF'
（投稿テキスト）
EOF
```

> `>>` で追記する点に注意（`>` で上書きすると前回未送信分が消える）。

## state更新とPR作成

```bash
echo "https://www.anthropic.com/news/..." > state/last_news.txt
git add pending/news.txt state/last_news.txt
git commit -m "notify: news"
# 作業ブランチに push して main 向けの PR を作成する
```

PR が作られたら GitHub Actions が auto-merge し、同じ workflow 内で `pending/news.txt` を読んで Discord に投稿、成功したらファイルを削除する。auto-merge も Discord 投稿もルーティーン側では関知しない。
