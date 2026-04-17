# Anthropic情報収集 → Discord配信 設計書

## 概要

Anthropicの一次情報を定期取得・日本語要約してDiscordに配信するシステム。
Claude Code Routinesで実行し、要約・翻訳はClaudeが担当。

---

## 購読対象ソース

| # | ソース | URL | 更新頻度 | 内容 |
|---|--------|-----|----------|------|
| A | Claude Code Changelog | `code.claude.com/docs/en/changelog` | 週数回 | CLIのバージョンアップ内容 |
| B | Anthropic News | `anthropic.com/news` | 不定期 | 製品発表・アナウンス |
| C | Anthropic Research | `anthropic.com/research` | 月4〜8本 | 安全性・解釈可能性・社会影響の研究 |
| D | Anthropic Engineering Blog | `anthropic.com/engineering` | 月2〜4本 | 実装・エージェント・eval等の技術記事 |

---

## Routines構成（4本に分割）

障害の局所化・頻度の個別最適化・プロンプトのシンプル化のため、ソースごとに独立したRoutineを立てる。

| Routine | 対象 | 実行頻度 | 理由 |
|---------|------|----------|------|
| A | Claude Code Changelog | 毎日 | 更新頻度が高い |
| B | Anthropic News | 毎日 | 重要発表を早く知りたい |
| C | Anthropic Research | 週3回 | 月数本ペース、毎日は過剰 |
| D | Anthropic Engineering | 週2回 | 月数本ペース、毎日は過剰 |

Proプランのデイリー5回制限（ResearchとEngineeringが同日に重なる日は4回）に収まる。

---

## 役割分担

### Pythonスクリプトが担当すること

- Discord Webhookへの投稿のみ（`urllib`で実装、外部ライブラリ不要）
- 引数で受け取ったテキストをそのままPOSTする薄いスクリプト
- 2000字超えの場合は自動分割して複数POST

```bash
# Claudeからの呼び出し方
python notify.py "投稿したいテキスト"
```

### Claudeが担当すること

- インデックスページのフェッチ（記事一覧の取得）
- 新着記事の本文フェッチ
- 日本語要約・翻訳
- stateファイルの読み書き（`cat` / `echo` で直接操作）
- `notify.py` の呼び出し（Discord投稿）
- stateファイルのgit commit & push

---

## リポジトリ構成

```
anthropic-discord-notifier/
├── CLAUDE.md                    # 全Routine共通の基本指示
├── routines/
│   ├── changelog.md             # Routine A 個別指示
│   ├── news.md                  # Routine B 個別指示
│   ├── research.md              # Routine C 個別指示
│   └── engineering.md           # Routine D 個別指示
├── notify.py                    # Discord投稿 & state管理スクリプト
└── state/
    ├── last_changelog.txt       # 前回通知済み（バージョン or URL）
    ├── last_news.txt            # 前回通知済みURL
    ├── last_research.txt        # 前回通知済みURL
    └── last_engineering.txt     # 前回通知済みURL
```

---

## Routine別プロンプト（概要）

各Routineのプロンプトは `routines/*.md` の内容を読んで実行する構成。

```
# 共通フロー（CLAUDE.md）
1. 対象Routineの指示ファイルを読む
2. notify.py でstateを確認（新着URLリストを取得）
3. 新着記事の本文をフェッチ
4. 日本語で要約（フォーマットは各指示ファイルに従う）
5. notify.py で Discord に投稿
6. state を更新し git commit & push
```

---

## Discord投稿フォーマット

チャンネルは1本にまとめる。ヘッダーでソースを区別する。

| Routine | ヘッダー |
|---------|---------|
| A Changelog | `🔧 Claude Code アップデート` |
| B News | `📢 Anthropic ニュース` |
| C Research | `🔬 Anthropic Research` |
| D Engineering | `⚙️ Engineering Blog` |

---

## Environment設定

### 環境変数

```
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxxx/yyyy
```

### ネットワーク（Custom）

```
code.claude.com
www.anthropic.com
discord.com
```

「Also include default list」は**オフ**（最小権限）。

---

## stateファイル構成

ソースごとに独立したtxtファイル。中身は1行1値。

```
state/
├── last_changelog.txt    # 最後に通知したバージョン番号（例: 2.1.91）
├── last_news.txt         # 最後に通知した記事URL
├── last_research.txt     # 最後に通知した記事URL
└── last_engineering.txt  # 最後に通知した記事URL
```

**保存する値：**
- Changelog のみバージョン番号（ページ内セクションIDで管理するため）
- それ以外は記事の絶対URL

**初回運用：**
- 分岐なし・自動初期化なし
- 運用開始前に手動で直近の値をセットしておく

```
# 例: last_news.txt の初期値
https://www.anthropic.com/news/claude-code-routines
```

**日時は保存しない：** URLの前後関係だけで新着判定できるため不要。

---

## ブランチ・state更新の方針

### Allow unrestricted branch pushes をオンにする

Routinesはデフォルトで `claude/` ブランチにしかpushできない。
Routine作成時に **Allow unrestricted branch pushes** を有効化して、mainへの直接pushを許可する。

### stateファイルの更新フロー

```
1. Claudeが echo "URL" > state/last_xxx.txt で直接書き込む
2. git add state/ && git commit -m "update state: last_xxx" && git push origin main
```

### 判断理由

- stateリポジトリに入るのはURLだけのtxtファイルのみ
- 壊れても git revert 1発で復元可能
- PR → マージのフローを挟む必要がない

---

## 未決事項

- [ ] notify.py の詳細実装
- [ ] 各Routineのプロンプト詳細

---

## 要約プロンプト

各 `routines/*.md` に記載する指示の本体。ソースの性質に合わせて4種類。

---

### A. Claude Code Changelog（`routines/changelog.md`）

```
## タスク
Claude Code Changelogの新着バージョンを日本語訳してDiscordに投稿する。

## 要約スタイル
- 変更内容をそのまま日本語に訳す（意訳・省略しない）
- 箇条書きの構造はそのまま保持する
- 技術用語（コマンド名・フラグ・固有名詞）は英語のまま残す

## Discord投稿フォーマット
新着が1件の場合：

🔧 **Claude Code アップデート**
**vX.Y.Z**
・（変更点1）
・（変更点2）
🔗 https://code.claude.com/docs/en/changelog#X-Y-Z

新着が複数件の場合：まとめて1投稿にする。バージョンごとに区切る。

🔧 **Claude Code アップデート**
**vX.Y.Z**
・（変更点）

**vX.Y.W**
・（変更点）
🔗 https://code.claude.com/docs/en/changelog
```

---

### B. Anthropic News（`routines/news.md`）

```
## タスク
Anthropic Newsの新着記事を日本語要約してDiscordに投稿する。

## 要約スタイル
- 何の発表か1文で書く
- 背景・詳細を2〜3文で補足する
- 「要するに：」は不要（Newsは事実の伝達が主なので）
- 固有名詞・製品名は英語のまま残す

## Discord投稿フォーマット
📢 **Anthropic ニュース**
**（記事タイトルの日本語訳）**
（2〜3文の要約）
🔗 （記事URL）

新着が複数件の場合：まとめて1投稿。記事ごとに空行で区切る。
```

---

### C. Anthropic Research（`routines/research.md`）

```
## タスク
Anthropic Researchの新着論文・レポートを日本語要約してDiscordに投稿する。

## 要約スタイル
以下の3点を必ず含める：
1. 何を調べたか / 何を作ったか（研究の対象・方法）
2. 何がわかったか / 何ができるようになったか（主な発見・成果）
3. なぜ重要か / どんな意味があるか（AI安全性・実用上の含意）

分量は300〜500字程度。技術的な内容でも平易な言葉で書く。
専門用語は初出時だけ英語を併記する（例：解釈可能性（Interpretability））。
最後に「**要するに：**」で1〜2文にまとめる。

## Discord投稿フォーマット
🔬 **Anthropic Research**
**（記事タイトルの日本語訳）** `（カテゴリ: Interpretability / Alignment / Economic Research 等）`

（本文 300〜500字）

**要するに：**（1〜2文）
🔗 （記事URL）

新着が複数件の場合：まとめて1投稿。記事ごとに `---` で区切る。
```

---

### D. Anthropic Engineering Blog（`routines/engineering.md`）

```
## タスク
Anthropic Engineering Blogの新着記事を日本語要約してDiscordに投稿する。

## 要約スタイル
以下の3点を必ず含める：
1. 何の問題を解こうとしているか（背景・課題）
2. どんなアプローチ・発見があったか（手法・実験・結果）
3. 開発者にとって何が使えるか / 何を意識すべきか（実践的な示唆）

分量は300〜500字程度。コマンドやコード例が記事にある場合は1つだけ引用してよい。
「要するに：」で締める。

## Discord投稿フォーマット
⚙️ **Engineering Blog**
**（記事タイトルの日本語訳）**

（本文 300〜500字）

**要するに：**（1〜2文）
🔗 （記事URL）

新着が複数件の場合：まとめて1投稿。記事ごとに `---` で区切る。
```

---

### 共通ルール（CLAUDE.mdに記載）

```
## 要約の共通ルール

- 新着なし の場合はDiscordに投稿しない（空投稿しない）
- 要約は日本語で書く。ただし以下は英語のまま残す：
  - コマンド・フラグ・変数名
  - 製品名・モデル名（Claude / Sonnet / Opus 等）
  - 論文タイトル
- 記事の主張を忠実に反映する（自分の解釈や評価を混ぜない）
```

