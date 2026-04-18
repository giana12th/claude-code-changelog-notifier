# anthropic-discord-notifier

Anthropicの一次情報（Changelog / News / Research / Engineering Blog）を定期取得し、日本語要約してDiscordに配信するシステム。[Claude Code Routines](https://code.claude.com/docs/en/routines) で実行する。

## 概要

| Routine | 対象 | スケジュール（JST） |
|---------|------|---------------------|
| A | Claude Code Changelog | 毎日 6:00 |
| B | Anthropic News | 毎日 7:00 |
| C | Anthropic Research | 月・水・金 15:00 |
| D | Engineering Blog | 月・木 15:30 |

新着がない日は投稿しない。

## アーキテクチャ

Routine（Anthropic VM）→ `pending/<routine>.txt` と `state/last_*.txt` を作業ブランチに commit → main 向け PR を作成 → GitHub Actions が PR を検知 → 変更が `pending/**` と `state/**` のみなら auto-merge → 同じ workflow 内で Discord に投稿 → 成功したら pending を削除して main に commit。

Anthropic VM から Discord に直接POSTすると DNS cache overflow が発生するため、Discord投稿だけ GitHub Actions に分離している。ルーティーンは作業ブランチにしか push できない（インフラ仕様）ため、main への反映は PR 経由とし、auto-merge も同じ Actions に統合している。

## リポジトリ構成

```
.
├── CLAUDE.md                        # Routine共通指示
├── notify.py                        # Discord投稿スクリプト（Actionsが使用）
├── .github/workflows/
│   └── discord-notify.yml           # PR を検知して auto-merge と Discord 投稿を行う
├── routines/
│   ├── changelog.md                 # Routine A 指示
│   ├── news.md                      # Routine B 指示
│   ├── research.md                  # Routine C 指示
│   └── engineering.md               # Routine D 指示
├── pending/                         # Routine が書き出す未送信メッセージ（投稿後Actionsが削除）
├── state/
│   ├── last_changelog.txt           # 最後に通知したバージョン番号
│   ├── last_news.txt                # 最後に通知した記事URL
│   ├── last_research.txt            # 最後に通知した記事URL
│   └── last_engineering.txt         # 最後に通知した記事URL
└── docs/
    └── routine-setup.md             # セットアップ手順書
```

## セットアップ

### 1. Environment を作成する

[claude.ai/code](https://claude.ai/code) → Settings → Environments → New environment

```
名前: anthropic-notifier
ネットワーク: Custom
  許可ドメイン:
    code.claude.com
    www.anthropic.com
  "Also include default list" → オフ
環境変数: （設定不要）
```

> Discord 投稿は GitHub Actions が行うため、Environment に `DISCORD_WEBHOOK_URL` や `discord.com` の許可は **不要**。

### 2. state ファイルに初期値をセット

通知済み扱いにする直近の値を手動で書き込む。ここより新しい記事が配信対象になる。  

```bash
echo "2.1.109" > state/last_changelog.txt
echo "https://www.anthropic.com/news/google-broadcom-partnership-compute" > state/last_news.txt
echo "https://www.anthropic.com/research/trustworthy-agents" > state/last_research.txt
echo "https://www.anthropic.com/engineering/claude-code-auto-mode" > state/last_engineering.txt

git add state/
git commit -m "init: set initial state"
git push origin main
```

上記urlは例です。最新情報を確認してください。  

### 3. GitHub Actions の設定

リポジトリ → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| 項目 | 値 |
|------|----|
| Name | `DISCORD_WEBHOOK_URL` |
| Value | Discord Webhook URL |

リポジトリ → **Settings** → **Actions** → **General** → **Workflow permissions**

- **Read and write permissions** を選択（workflow が PR を merge し、pending 削除 commit を push するため）

リポジトリ → **Settings** → **General** → **Pull Requests**

- **Allow merge commits** を有効にする（workflow の `gh pr merge --merge` で使用）

設定後、Actions タブに "Auto-merge routine PR and notify" workflow が表示されることを確認する。変更が `pending/**` と `state/**` のみの PR に限り auto-merge が走る（手動 PR の誤マージ防止）。

### 4. Routine を4本作成する

[claude.ai/code/routines](https://claude.ai/code/routines) → New routine

| 項目 | 値 |
|------|----|
| リポジトリ | このリポジトリ |
| Allow unrestricted branch pushes | **オン** |
| Environment | anthropic-notifier |
| Connectors | すべて外す |

| Routine | 名前 | プロンプト | スケジュール |
|---------|------|-----------|-------------|
| A | anthropic-changelog | `routines/changelog.md を読んで実行してください。` | Daily 21:00 UTC |
| B | anthropic-news | `routines/news.md を読んで実行してください。` | Daily 22:00 UTC |
| C | anthropic-research | `routines/research.md を読んで実行してください。` | 月・水・金 06:00 UTC |
| D | anthropic-engineering | `routines/engineering.md を読んで実行してください。` | 月・木 06:30 UTC |

設定後、各Routineで **Run now** を実行して動作確認する。

## notify.py の使い方

通常は GitHub Actions が起動するのでユーザーが直接実行することはない。手元でのデバッグ用：

```bash
# 標準入力（改行・特殊文字を安全に扱える）
python -X utf8 notify.py <<'EOF'
メッセージ本文（Markdown可）
EOF

# 引数
python notify.py "投稿したいテキスト"

# dry-run（送信せずpayloadを確認）
python notify.py --dry-run <<'EOF'
テスト
EOF
```

- 標準ライブラリのみ使用（`pip install` 不要）
- 2000字超えは自動分割して複数POST
- `DISCORD_WEBHOOK_URL` 環境変数が必要（GitHub Actions Secrets に登録）
- 投稿失敗時は exit 1（Actions が pending を残して再試行可能にする）

## Discord 投稿サンプル

```
🔧 **Claude Code アップデート**
**v2.1.109**
・新機能: ...
🔗 https://code.claude.com/docs/en/changelog#2-1-109

📢 **Anthropic ニュース**
**Google・Broadcom とのコンピュートパートナーシップ**
AnthropicはGoogleおよびBroadcomと...
🔗 https://www.anthropic.com/news/google-broadcom-partnership-compute

🔬 **Anthropic Research**
**信頼できるエージェント** `Alignment`
...
🔗 https://www.anthropic.com/research/trustworthy-agents
```

## ライセンス

MIT
