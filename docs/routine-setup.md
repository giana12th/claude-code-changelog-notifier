# Routine 設定手順書

---

## 事前準備（1回だけ）

### 1. Environmentを作成する

[claude.ai/code/routines](https://claude.ai/code/routines) でRoutine作成フォームを開く → **Select an environment** ステップ → **Add environment**

または、既存Routineの環境名をクリック → **Add environment**

```
名前: anthropic-notifier
ネットワーク: Full
環境変数: （設定不要）
Setup script: （空でよい）
```

ネットワークはFullにしないとサイト検索ができない  

**Environmentが表示されないとき**  
リポジトリにclaudeのGithub-appをインストールしてみる  
https://github.com/apps/claude  

ブラウザのキャッシュクリアしてリロードする(Ctrl+F5)  
-> めちゃくちゃ画面変わって設定が出てきた   


### 2. stateファイルに初期値をセット

リポジトリをローカルでcloneし、手動で直近の値を書き込む。  
下記は例です。最新のurlを確認してください。  

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
  - 理由：workflow が PR を merge し、投稿成功後に `pending/*.txt` を削除して main に commit/push する
- **Allow GitHub Actions to create and approve pull requests** は不要（チェック不要。PR 作成はルーティーン側が行う）

#### 3-3. Merge 戦略の有効化

リポジトリ → **Settings** → **General** → **Pull Requests**

- **Allow merge commits** を有効にする
  - 理由：workflow が `gh pr merge --merge` で merge commit 方式で merge するため
- Squash / Rebase は任意（無効でも本システムの動作には影響しない）

#### 3-4. 動作確認

`.github/workflows/discord-notify.yml` が main にある状態で、リポジトリの **Actions** タブに "Auto-merge routine PR and notify" workflow が表示されることを確認する。
初回は `workflow_dispatch` で手動起動してテストできる（PR が無い場合は何もせず終了する）。

**安全策:** workflow は PR 差分が `pending/**` と `state/**` のみの場合に限り auto-merge する。通常の開発 PR（コードを変更する PR）は自動マージされない。

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
| Environment | anthropic-notifier |
| スケジュール | 月・水・金 / 06:00 UTC（15:00 JST） |
|cron式(UTC)|0 6 * * 1,3,5|
| Connectors | すべて外す |

---

### Routine D: Anthropic Engineering Blog

| 項目 | 値 |
|------|----|
| 名前 | anthropic-engineering |
| プロンプト | `routines/engineering.md を読んで実行してください。` |
| リポジトリ | このリポジトリ |
| Environment | anthropic-notifier |
| スケジュール | 月・木 / 06:30 UTC（15:30 JST） |
|cron式(UTC)|30 6 * * 1,5|
| Connectors | すべて外す |

---

## 確認チェックリスト

```
□ Environmentのネットワーク設定が Full になっている
□ GitHub Secrets に DISCORD_WEBHOOK_URL が登録されている
□ GitHub Actions の Workflow permissions が "Read and write" になっている
□ Actions タブに "Discord Notify" workflow が表示されている
□ 4本すべて Connectors がすべて外れている
□ state/*.txt に初期値が手動でセットされている
□ 各Routineで Run now を実行して動作確認
```

---

## スケジュール早見表

| Routine | UTC | JST | 曜日 |
|---------|-----|-----|------|
| A Changelog   | 21:00 | 6:00  | 毎日 |
| B News        | 22:00 | 7:00  | 毎日 |
| C Research    | 06:00 | 15:00 | 月・水・金 |
| D Engineering | 06:30 | 15:30 | 月・木 |

> Web画面の時刻入力がローカルタイムゾーン換算される場合は要確認。
