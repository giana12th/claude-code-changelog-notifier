# Routine A: Claude Code Changelog

## タスク

Claude Code Changelogの新着バージョンを日本語訳してDiscordに投稿する。

## 実行手順

1. `state/last_changelog.txt` を読み、最後に通知したバージョン番号を取得する
2. `https://code.claude.com/docs/en/changelog` をフェッチしてバージョン一覧を取得する
3. 前回バージョンより新しいバージョンを特定する（ページ上部が最新）
4. 新着バージョンそれぞれの変更内容を取得する
5. 下記フォーマットの投稿テキストを組み立てる
6. `pending/changelog.txt` に投稿テキストを書き出す（既存ファイルがあれば追記）
7. 最新バージョン番号を `state/last_changelog.txt` に書き込む
8. `pending/changelog.txt` と `state/last_changelog.txt` をまとめてmainブランチにgit commit & push する

新着がない場合は `pending/` にも `state/` にも何も書かず終了する。
Discordへの実際の投稿は GitHub Actions（`.github/workflows/discord-notify.yml`）が push を検知して行う。

## 要約スタイル

- 変更内容をそのまま日本語に訳す（意訳・省略しない）
- 箇条書きの構造はそのまま保持する
- 技術用語（コマンド名・フラグ・固有名詞）は英語のまま残す

## Discord投稿フォーマット

新着が1件の場合：

```
🔧 **Claude Code アップデート**
**vX.Y.Z**
・（変更点1）
・（変更点2）
🔗 https://code.claude.com/docs/en/changelog#X-Y-Z
```

新着が複数件の場合：まとめて1投稿にする。バージョンごとに空行で区切る。

```
🔧 **Claude Code アップデート**
**vX.Y.Z**
・（変更点）

**vX.Y.W**
・（変更点）
🔗 https://code.claude.com/docs/en/changelog
```

## pending への書き出し

```bash
# 既存の pending がある場合は追記する（前回Discord投稿が失敗して残っているケース）
cat >> pending/changelog.txt <<'EOF'
（投稿テキスト）
EOF
```

> `>>` で追記する点に注意（`>` で上書きすると前回未送信分が消える）。

## state更新とgit push

```bash
echo "X.Y.Z" > state/last_changelog.txt
git add pending/changelog.txt state/last_changelog.txt
git commit -m "notify: changelog X.Y.Z"
git push origin main
```

push 後は GitHub Actions が `pending/changelog.txt` を読んで Discord に投稿し、成功したらファイルを削除する。投稿成否はルーティーン側では関知しない。
