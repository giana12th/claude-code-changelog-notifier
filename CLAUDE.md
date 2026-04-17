# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 概要

Anthropicの一次情報（Changelog / News / Research / Engineering Blog）を定期取得し、日本語要約してDiscordに配信するシステム。Claude Code Routinesで実行する。

## リポジトリ構成

```
anthropic-discord-notifier/
├── CLAUDE.md                    # 全Routine共通の基本指示（このファイル）
├── notify.py                    # Discord投稿スクリプト
├── routines/
│   ├── changelog.md             # Routine A: Claude Code Changelog
│   ├── news.md                  # Routine B: Anthropic News
│   ├── research.md              # Routine C: Anthropic Research
│   └── engineering.md           # Routine D: Engineering Blog
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
6. `notify.py` でDiscordに投稿する
7. `state/last_*.txt` を更新して mainブランチに直接 git commit & push する（PRは作らない）

**新着なしの場合はDiscordに投稿しない（空投稿しない）。** stateも更新しない。  
作業を終了する。  

## notify.py の使い方

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
- 環境変数 `DISCORD_WEBHOOK_URL` が必要

## stateファイルの更新

```bash
# 値を書き込む
echo "2.1.91" > state/last_changelog.txt
echo "https://www.anthropic.com/news/..." > state/last_news.txt

# git commit & push（mainへ直接push）
git add state/
git commit -m "update state: last_changelog"
git push origin main
```

- `state/` に入るのはURLまたはバージョン番号のみ
- 日時は保存しない（URL/バージョンの前後関係だけで新着判定）
- 初期値は手動でセット済み前提。自動初期化ロジック不要

## エラーハンドリング

### Discord投稿が失敗したとき
- そのまま終了する
- `state/last_*.txt` は更新しない
- 一時的な障害は次回実行時に自動リカバリされる
- 連続失敗はDiscord通知が届かないことでユーザーが気づいて対処する  

### 記事取得・要約が失敗したとき
- 失敗した旨をDiscordに報告して終了する
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

| 変数 | 用途 |
|------|------|
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL（Routine Environment で設定） |

## Routine スケジュール

| Routine | 対象 | UTC | JST | 曜日 |
|---------|------|-----|-----|------|
| A | Changelog   | 21:00 | 6:00  | 毎日 |
| B | News        | 22:00 | 7:00  | 毎日 |
| C | Research    | 06:00 | 15:00 | 月・水・金 |
| D | Engineering | 06:30 | 15:30 | 月・木 |
