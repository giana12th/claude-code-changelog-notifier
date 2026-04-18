# Routine 設定手順書

---

## 事前準備（1回だけ）

### 1. Environmentを作成する

`claude.ai/code/routines` でRoutine作成フォームを開く → **Select an environment** ステップ → **Add environment**

または、既存Routineの環境名をクリック → **Add environment**

```
名前: anthropic-notifier
ネットワーク: Custom
  許可ドメイン（1行1ドメイン）:
    www.anthropic.com
  "Also include default list of common package managers" → オフ
環境変数: （設定不要）
Setup script: （空でよい）
```

> Pythonは標準でインストール済みのため Setup script 不要。
> Discord への投稿は GitHub Actions が行うため、Routine Environment に `DISCORD_WEBHOOK_URL` や `discord.com` の許可ドメインは **不要**。ルーティーンは `pending/<routine>.txt` にメッセージを書いて push するだけ。

**Environmentが表示されないとき**  
リポジトリにclaudeのGithub-appをインストールしてみる  
https://github.com/apps/claude  

ブラウザのキャッシュクリアしてリロードする(Ctrl+F5)  
-> めちゃくちゃ画面変わって設定が出てきた   


### 2. stateファイルに初期値をセット

リポジトリをローカルでcloneし、手動で直近の値を書き込む。

```bash
echo "2.1.91" > state/last_changelog.txt
echo "https://www.anthropic.com/news/claude-code-routines" > state/last_news.txt
echo "https://www.anthropic.com/research/emotion-concepts-function" > state/last_research.txt
echo "https://www.anthropic.com/engineering/infrastructure-noise" > state/last_engineering.txt

git add state/
git commit -m "init: set initial state"
git push origin main
```

> 初回分岐なし。初期値より新しい記事が配信対象になる。

---

### 3. GitHub Actions の設定

Discord 投稿は GitHub Actions（`.github/workflows/discord-notify.yml`）が行う。リポジトリ側で下記を設定する。

#### 3-1. Secret の登録

リポジトリ → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| 項目 | 値 |
|------|----|
| Name | `DISCORD_WEBHOOK_URL` |
| Value | Discord Webhook URL（`https://discord.com/api/webhooks/xxxx/yyyy`） |

#### 3-2. Workflow permissions

リポジトリ → **Settings** → **Actions** → **General** → **Workflow permissions**

- **Read and write permissions** を選択
  - 理由：workflow が投稿成功後に `pending/*.txt` を削除して commit/push する
- **Allow GitHub Actions to create and approve pull requests** は不要（チェック不要）

#### 3-3. 動作確認

`.github/workflows/discord-notify.yml` が main にある状態で、リポジトリの **Actions** タブに "Discord Notify" workflow が表示されることを確認する。
初回は `workflow_dispatch` で手動起動してテストできる（pending ファイルが空なら何も起きずに成功終了する）。

---

## Routine作成（4本それぞれ）

`claude.ai/code/routines` → New routine

---

### Routine A: Claude Code Changelog

| 項目 | 値 |
|------|----|
| 名前 | anthropic-changelog |
| プロンプト | `routines/changelog.md を読んで実行してください。` |
| リポジトリ | このリポジトリ |
| Allow unrestricted branch pushes | **オン** |
| Environment | anthropic-notifier |
| スケジュール | Daily / 21:00 UTC（6:00 JST） |
| Connectors | すべて外す |

---

### Routine B: Anthropic News

| 項目 | 値 |
|------|----|
| 名前 | anthropic-news |
| プロンプト | `routines/news.md を読んで実行してください。` |
| リポジトリ | このリポジトリ |
| Allow unrestricted branch pushes | **オン** |
| Environment | anthropic-notifier |
| スケジュール | Daily / 22:00 UTC（7:00 JST） |
| Connectors | すべて外す |

---

### Routine C: Anthropic Research

| 項目 | 値 |
|------|----|
| 名前 | anthropic-research |
| プロンプト | `routines/research.md を読んで実行してください。` |
| リポジトリ | このリポジトリ |
| Allow unrestricted branch pushes | **オン** |
| Environment | anthropic-notifier |
| スケジュール | 月・水・金 / 06:00 UTC（15:00 JST） |
| Connectors | すべて外す |

---

### Routine D: Anthropic Engineering Blog

| 項目 | 値 |
|------|----|
| 名前 | anthropic-engineering |
| プロンプト | `routines/engineering.md を読んで実行してください。` |
| リポジトリ | このリポジトリ |
| Allow unrestricted branch pushes | **オン** |
| Environment | anthropic-notifier |
| スケジュール | 月・木 / 06:30 UTC（15:30 JST） |
| Connectors | すべて外す |

---

## 確認チェックリスト

```
□ Environmentのネットワーク設定が Custom になっている
□ www.anthropic.com が許可されている（discord.com は不要）
□ Routine Environment に DISCORD_WEBHOOK_URL は設定していない
□ GitHub Secrets に DISCORD_WEBHOOK_URL が登録されている
□ GitHub Actions の Workflow permissions が "Read and write" になっている
□ pending/ ディレクトリ（.gitkeep 入り）がリポジトリに存在する
□ Actions タブに "Discord Notify" workflow が表示されている
□ 4本すべて Allow unrestricted branch pushes がオン
□ 4本すべて Connectors がすべて外れている
□ state/*.txt に初期値が手動でセットされている
□ 各Routineで Run now を実行して動作確認
```

## 既存運用から移行する場合（任意）

旧運用で設定済みの以下は削除してよい（残しても害はない）：

- Routine Environment の環境変数 `DISCORD_WEBHOOK_URL`
- Routine Environment の許可ドメイン `discord.com`

---

## スケジュール早見表

| Routine | UTC | JST | 曜日 |
|---------|-----|-----|------|
| A Changelog   | 21:00 | 6:00  | 毎日 |
| B News        | 22:00 | 7:00  | 毎日 |
| C Research    | 06:00 | 15:00 | 月・水・金 |
| D Engineering | 06:30 | 15:30 | 月・木 |

> Web画面の時刻入力がローカルタイムゾーン換算される場合は要確認。
