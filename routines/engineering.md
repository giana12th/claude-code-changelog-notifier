# Routine D: Anthropic Engineering Blog

## タスク

Anthropic Engineering Blogの新着記事を日本語要約してDiscordに投稿する。

## 実行手順

1. `state/last_engineering.txt` を読み、最後に通知した記事URLを取得する
2. `https://www.anthropic.com/engineering` をフェッチして記事一覧を取得する
3. 前回URLより新しい記事を特定する（ページ上部が最新）
4. 新着記事それぞれの本文をフェッチする
5. 下記フォーマットでDiscordに投稿する
6. 最新記事のURLを `state/last_engineering.txt` に書き込む
7. git commit & push する

新着がない場合はDiscordに投稿せず、stateも更新しない。

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

## notify.py の呼び出し

```bash
python -X utf8 notify.py <<'EOF'
（投稿テキスト）
EOF
```

## state更新とgit push

```bash
echo "https://www.anthropic.com/engineering/..." > state/last_engineering.txt
git add state/last_engineering.txt
git commit -m "update state: last_engineering"
git push origin main
```
