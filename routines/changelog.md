# Routine A: Claude Code Changelog

## タスク

Claude Code Changelogの新着バージョンを日本語訳してDiscordに投稿する。

## 実行手順

1. `state/last_changelog.txt` を読み、最後に通知したバージョン番号を取得する
2. `https://code.claude.com/docs/en/changelog` をフェッチしてバージョン一覧を取得する
3. 前回バージョンより新しいバージョンを特定する（ページ上部が最新）
4. 新着バージョンそれぞれの変更内容を取得する
5. 下記フォーマットでDiscordに投稿する
6. 最新バージョン番号を `state/last_changelog.txt` に書き込む
7. git commit & push する

新着がない場合はDiscordに投稿せず、stateも更新しない。

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

## notify.py の呼び出し

```bash
python -X utf8 notify.py <<'EOF'
（投稿テキスト）
EOF
```

## state更新とgit push

```bash
echo "X.Y.Z" > state/last_changelog.txt
git add state/last_changelog.txt
git commit -m "update state: last_changelog"
git push origin main
```
