# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 概要

Anthropicの一次情報（Changelog / News / Research / Engineering Blog）を定期取得し、日本語要約してDiscordに配信するシステム。Claude Code Routinesで実行する。

## リポジトリ構成

```
anthropic-discord-notifier/
├── CLAUDE.md                    # 全Routine共通の基本指示（このファイル）
├── notify.py                    # Discord投稿スクリプト（GitHub Actions が使用）
├── .github/workflows/
│   └── discord-notify.yml       # pending/** の push を検知して Discord 投稿
├── routines/
│   ├── changelog.md             # Routine A: Claude Code Changelog
│   ├── news.md                  # Routine B: Anthropic News
│   ├── research.md              # Routine C: Anthropic Research
│   └── engineering.md           # Routine D: Engineering Blog
├── pending/                     # Routine が書き出す未送信メッセージ置き場
│   ├── changelog.txt            # （投稿後に Actions が削除）
│   ├── news.txt
│   ├── research.txt
│   └── engineering.txt
└── state/
    ├── last_changelog.txt       # 最後に通知したバージョン番号（例: 2.1.91）
    ├── last_news.txt            # 最後に通知した記事URL
    ├── last_research.txt        # 最後に通知した記事URL
    └── last_engineering.txt     # 最後に通知した記事URL
```

## 実行フロー（全Routine共通）

1. 対象Routineの指示ファイル（`routines/*.md`）を読む
2. `state/last_*.txt` を読んで前回通知済みの値を確認する
3. 対象ソースのインデックスページをフェッチして記事一覧を取得する
4. 前回値より新しい記事を特定し、本文をフェッチする
5. 日本語で要約する（フォーマットは各指示ファイルに従う）
6. 要約テキストを `pending/<routine>.txt` に **追記** する（`>>` を使う）
   - 既存ファイルがある場合は前回Discord投稿失敗分が残っているので、それに続けて書く
7. `state/last_*.txt` を更新する
8. `pending/<routine>.txt` と `state/last_*.txt` を一括 commit し、作業ブランチに push して main 向けの PR を作成する

PR 作成後、GitHub Actions（`.github/workflows/discord-notify.yml`）が PR を検知して起動する。ファイル差分が `pending/**` と `state/**` のみであれば auto-merge し、同じ workflow 内で pending ファイルを読んで Discord に POST する。成功したら Actions が pending ファイルを削除して main に commit する。ルーティーンは auto-merge と Discord 投稿の成否に関与しない。

**新着なしの場合は `pending/` にも `state/` にも何も書かず終了する。**

## notify.py の使い方

ルーティーンから notify.py を呼ぶ必要はない（pending ファイルに書くだけ）。
GitHub Actions 側が pending を入力として notify.py を起動する。

参考：notify.py の呼び出し仕様

```bash
# 標準入力で渡す（改行・特殊文字を安全に扱える）
python -X utf8 notify.py <<'EOF'
メッセージ本文（Markdown可）
EOF

# 引数で渡す
python notify.py "投稿したいテキスト"

# dry-run（送信せずpayloadを確認）
python notify.py --dry-run <<'EOF'
テスト
EOF
```

- 標準ライブラリ（`urllib`）のみ使用、`pip install` 不要
- Discordの2000字制限を超える場合は **自動分割して複数POST**
- 環境変数 `DISCORD_WEBHOOK_URL` が必要（GitHub Actions Secrets に登録）
- 投稿失敗時は exit 1（Actions が pending を残して再試行可能にする）

## pending / state ファイルの更新

```bash
# pending に追記（上書きではなく >> を使う）
cat >> pending/changelog.txt <<'EOF'
（投稿テキスト）
EOF

# state を更新
echo "2.1.91" > state/last_changelog.txt

# pending と state を同じ commit にまとめて作業ブランチに push、main 向け PR を作成
git add pending/changelog.txt state/last_changelog.txt
git commit -m "notify: changelog 2.1.91"
# 作業ブランチに push して main 向けの PR を作成する
```

- `pending/<routine>.txt` は Actions が投稿成功時に削除する
- `state/` に入るのはURLまたはバージョン番号のみ
- 日時は保存しない（URL/バージョンの前後関係だけで新着判定）
- 初期値は手動でセット済み前提。自動初期化ロジック不要

## エラーハンドリング

### Discord投稿が失敗したとき
- ルーティーン側では感知しない（pending を書いて PR を作成した時点で責務完了）
- GitHub Actions 側で `notify.py` が exit 1 した場合、`pending/<routine>.txt` は **削除せず残す**（PR は既に merge 済み）
- 次回ルーティーン実行時、pending が残っていれば追記する形で新着分が足され、新しい PR 経由で一括再送される
- 連続失敗は Discord通知が届かないことでユーザーが気づく（Actions の実行履歴も確認できる）

### 記事取得・要約が失敗したとき
- 失敗した旨を `pending/<routine>.txt` に書き出して PR を作成する
  例：`⚠️ [Routine名] 記事取得に失敗しました: <エラー内容>`
- `state/last_*.txt` は更新しない
- エラー内容を見てユーザーが適宜対応する

## 要約の共通ルール

- 要約は日本語で書く。ただし以下は英語のまま残す：
  - コマンド・フラグ・変数名
  - 製品名・モデル名（Claude / Sonnet / Opus 等）
  - 論文タイトル
- 記事の主張を忠実に反映する（自分の解釈・評価を混ぜない）
- 2000字を超えてもnotify.pyが自動分割するので対処不要  

## Discordヘッダー対応表

| Routine | ヘッダー |
|---------|---------|
| A Changelog | `🔧 Claude Code アップデート` |
| B News | `📢 Anthropic ニュース` |
| C Research | `🔬 Anthropic Research` |
| D Engineering | `⚙️ Engineering Blog` |

## 環境変数

| 変数 | 用途 | 設定場所 |
|------|------|---------|
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL | GitHub Actions Secrets（Routine Environment では **不要**） |

## Routine スケジュール

| Routine | 対象 | UTC | JST | 曜日 |
|---------|------|-----|-----|------|
| A | Changelog   | 21:00 | 6:00  | 毎日 |
| B | News        | 22:00 | 7:00  | 毎日 |
| C | Research    | 06:00 | 15:00 | 月・水・金 |
| D | Engineering | 06:30 | 15:30 | 月・木 |
