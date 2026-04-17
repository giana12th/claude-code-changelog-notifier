# Routine C: Anthropic Research

## タスク

Anthropic Researchの新着論文・レポートを日本語要約してDiscordに投稿する。

## 実行手順

1. `state/last_research.txt` を読み、最後に通知した記事URLを取得する
2. `https://www.anthropic.com/research` をフェッチして記事一覧を取得する
3. 前回URLより新しい記事を特定する（ページ上部が最新）
4. 新着記事それぞれの本文をフェッチする
5. 下記フォーマットでDiscordに投稿する
6. 最新記事のURLを `state/last_research.txt` に書き込む
7. git commit & push する

新着がない場合はDiscordに投稿せず、stateも更新しない。

## 要約スタイル

以下の3点を必ず含める：
1. 何を調べたか / 何を作ったか（研究の対象・方法）
2. 何がわかったか / 何ができるようになったか（主な発見・成果）
3. なぜ重要か / どんな意味があるか（AI安全性・実用上の含意）

分量は300〜500字程度。技術的な内容でも平易な言葉で書く。
専門用語は初出時だけ英語を併記する（例：解釈可能性（Interpretability））。
最後に「**要するに：**」で1〜2文にまとめる。

## Discord投稿フォーマット

```
🔬 **Anthropic Research**
**（記事タイトルの日本語訳）** `（カテゴリ: Interpretability / Alignment / Economic Research 等）`

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
echo "https://www.anthropic.com/research/..." > state/last_research.txt
git add state/last_research.txt
git commit -m "update state: last_research"
git push origin main
```
