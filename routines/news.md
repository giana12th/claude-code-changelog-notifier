# Routine B: Anthropic News

## タスク

Anthropic Newsの新着記事を日本語要約してDiscordに投稿する。

## 実行手順

1. `state/last_news.txt` を読み、最後に通知した記事URLを取得する
2. `https://www.anthropic.com/news` をフェッチして記事一覧を取得する
3. 前回URLより新しい記事を特定する（ページ上部が最新）
4. 新着記事それぞれの本文をフェッチする
5. 下記フォーマットでDiscordに投稿する
6. 最新記事のURLを `state/last_news.txt` に書き込む
7. git commit & push する

新着がない場合はDiscordに投稿せず、stateも更新しない。

## 要約スタイル

- 何の発表か1文で書く
- 背景・詳細を2〜3文で補足する
- 「要するに：」は不要（Newsは事実の伝達が主）
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

## notify.py の呼び出し

```bash
python -X utf8 notify.py <<'EOF'
（投稿テキスト）
EOF
```

## state更新とgit push

```bash
echo "https://www.anthropic.com/news/..." > state/last_news.txt
git add state/last_news.txt
git commit -m "update state: last_news"
git push origin main
```
