# MekuJira

macOS / Windows のシステムトレイに常駐し、JIRA Cloud の課題を管理するデスクトップアプリ。

## 機能

- **システムトレイ常駐**: トレイアイコンから左クリックでポップアップ表示（フルスクリーン対応）
- **ブックマーク**: 集中する課題をピックアップしてポップアップに常時表示
- **対象課題一覧**: JQLフィルタで課題を取得・表示（独立ウィンドウ）
- **自動更新**: バックグラウンドポーリングで課題データを自動取得
- **セキュア**: APIトークンはAES-256-GCMで暗号化しローカルファイルに保存

## 技術スタック

- **フレームワーク**: Tauri 2.x
- **バックエンド**: Rust
- **フロントエンド**: Svelte 5 + TypeScript (SvelteKit)
- **対象OS**: macOS 13+, Windows 10+
- **JIRA**: Cloud (atlassian.net)、API Token (Basic Auth)

## セットアップ

### 前提条件

- [Rust](https://www.rust-lang.org/tools/install)
- [Node.js](https://nodejs.org/) (v18+)
- macOS 13+ または Windows 10+

### インストール

```bash
npm install
```

### 開発

```bash
npm run tauri dev
```

### ビルド

```bash
npm run tauri build
```

## リリース・配布

### 初回セットアップ

#### 1. Tauri署名鍵の生成

アプリ内自動更新のために、Tauri独自の署名鍵ペアが必要です。

```bash
npx tauri signer generate -w ~/.tauri/mekujira.key
```

生成されるファイル:
- `~/.tauri/mekujira.key` — 秘密鍵
- `~/.tauri/mekujira.key.pub` — 公開鍵（`tauri.conf.json` の `pubkey` に設定済み）

#### 2. GitHub Secrets の設定

リポジトリの Settings → Secrets and variables → Actions で以下を登録:

| Secret名 | 値 |
|---|---|
| `TAURI_SIGNING_PRIVATE_KEY` | `~/.tauri/mekujira.key` の内容 |
| `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | 鍵生成時に設定したパスワード |

#### 3. Workflow permissions の設定

Settings → Actions → General → Workflow permissions で **Read and write permissions** を有効にしてください。

### リリース手順

1. `src-tauri/tauri.conf.json` と `src-tauri/Cargo.toml` の `version` を更新
2. コミット & プッシュ
3. タグを作成してプッシュ:
   ```bash
   git tag v0.X.Y && git push --tags
   ```

GitHub Actions が自動で macOS + Windows をビルドし、GitHub Releases にアップロードします。

## チーム向けインストール手順

### macOS

1. [GitHub Releases](https://github.com/collabo-miko/MekuJira/releases) から最新の DMG をダウンロード
2. DMG を開き、MekuJira.app を `/Applications` にドラッグ
3. Gatekeeper を回避（コード署名なしのため）:
   ```bash
   xattr -cr /Applications/MekuJira.app
   ```
4. MekuJira を起動し、JIRA 接続設定を行う

### Windows

1. [GitHub Releases](https://github.com/collabo-miko/MekuJira/releases) から最新の `.exe` インストーラーをダウンロード
2. インストーラーを実行
3. MekuJira を起動し、JIRA 接続設定を行う

### 更新（2回目以降）

アプリ起動時に自動で更新チェックが行われます。新しいバージョンがある場合は自動的にダウンロード・インストールされます。
