# Routine C: Anthropic Research

## タスク

Anthropic Researchの新着論文・レポートを日本語要約してDiscordに投稿する。

## 実行手順

1. `state/last_research.txt` を読み、最後に通知した記事URLを取得する
2. `https://www.anthropic.com/research` をフェッチして記事一覧を取得する
3. 前回URLより新しい記事を特定する（ページ上部が最新）
4. 新着記事それぞれの本文をフェッチする
5. 下記フォーマットの投稿テキストを組み立てる
6. `pending/research.txt` に投稿テキストを書き出す（既存ファイルがあれば追記）
7. 最新記事のURLを `state/last_research.txt` に書き込む
8. `pending/research.txt` と `state/last_research.txt` をまとめて作業ブランチに commit & push し、main 向けの PR を作成する

新着がない場合は `pending/` にも `state/` にも何も書かず終了する。
PR 作成後の auto-merge と Discord 投稿は GitHub Actions が行う。ルーティーン側では関知しない。

## 要約スタイル

以下の3点を必ず含める：
1. 何を調べたか / 何を作ったか（研究の対象・方法）
2. 何がわかったか / 何ができるようになったか（主な発見・成果）
3. なぜ重要か / どんな意味があるか（AI安全性・実用上の含意）

分量は300〜500字程度。技術的な内容でも平易な言葉で書く。
専門用語は初出時だけ英語を併記する（例：解釈可能性（Interpretability））。

## Discord投稿フォーマット

```
🔬 **Anthropic Research**
**（記事タイトルの日本語訳）** `（カテゴリ: Interpretability / Alignment / Economic Research 等）`

（本文 300〜500字）

🔗 （記事URL）
```

新着が複数件の場合：まとめて1投稿。記事ごとに `---` で区切る。

## pending への書き出し

```bash
# 既存の pending がある場合は追記する（前回Discord投稿が失敗して残っているケース）
cat >> pending/research.txt <<'EOF'
（投稿テキスト）
EOF
```

> `>>` で追記する点に注意（`>` で上書きすると前回未送信分が消える）。

## state更新とPR作成

```bash
echo "https://www.anthropic.com/research/..." > state/last_research.txt
git add pending/research.txt state/last_research.txt
git commit -m "notify: research"
# 作業ブランチに push して main 向けの PR を作成する
```

PR が作られたら GitHub Actions が auto-merge し、同じ workflow 内で `pending/research.txt` を読んで Discord に投稿、成功したらファイルを削除する。auto-merge も Discord 投稿もルーティーン側では関知しない。
