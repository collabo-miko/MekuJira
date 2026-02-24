# MekuJira

macOS メニューバーに常駐し、JIRA Cloud の課題を管理するデスクトップアプリ。

## 機能

- **メニューバー常駐**: トレイアイコンから左クリックでポップアップ表示（フルスクリーン対応）
- **ブックマーク**: 集中する課題をピックアップしてポップアップに常時表示
- **対象課題一覧**: JQLフィルタで課題を取得・表示（独立ウィンドウ）
- **自動更新**: バックグラウンドポーリングで課題データを自動取得
- **セキュア**: APIトークンはmacOS Keychainに暗号化保存

## 技術スタック

- **フレームワーク**: Tauri 2.x
- **バックエンド**: Rust
- **フロントエンド**: Svelte 5 + TypeScript (SvelteKit)
- **対象OS**: macOS 13 (Ventura) 以降
- **JIRA**: Cloud (atlassian.net)、API Token (Basic Auth)

## セットアップ

### 前提条件

- [Rust](https://www.rust-lang.org/tools/install)
- [Node.js](https://nodejs.org/) (v18+)
- macOS 13+

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

### 初回セットアップ: Tauri署名鍵の生成

アプリ内自動更新のために、Tauri独自の署名鍵ペアが必要です（Apple Developer Accountとは無関係）。

```bash
# 鍵ペアを生成（パスワードを聞かれるので設定する）
npx tauri signer generate -w ~/.tauri/mekujira.key
```

生成されるファイル:
- `~/.tauri/mekujira.key` — 秘密鍵（ビルド時に使用）
- `~/.tauri/mekujira.key.pub` — 公開鍵（`tauri.conf.json` の `pubkey` に設定）

公開鍵を `src-tauri/tauri.conf.json` の `plugins.updater.pubkey` に設定してください。

### リリースビルド

```bash
# 秘密鍵を設定
export TAURI_SIGNING_PRIVATE_KEY=$(cat ~/.tauri/mekujira.key)

# パスワードを設定（特殊文字 !$` 等を含む場合は read を使う）
read -s TAURI_SIGNING_PRIVATE_KEY_PASSWORD
export TAURI_SIGNING_PRIVATE_KEY_PASSWORD

# リリーススクリプトを実行
./scripts/release.sh
```

> **Note**: `read -s` はパスワードを非表示で入力できます。シェルの特殊文字（`!`, `$`, `` ` `` 等）による問題を回避できます。

スクリプトは以下を自動で行います:
1. `tauri.conf.json` からバージョンを読み取り
2. 署名付きビルド（DMG + `.tar.gz` + `.sig`）
3. `latest.json` の自動生成

### GitHub Releases へのアップロード

1. `src-tauri/tauri.conf.json` の `version` を更新
2. `./scripts/release.sh` でビルド
3. ビルド完了後、スクリプトが GitHub Releases へのアップロードを確認します（`y` で自動実行）

スクリプトが自動で行うこと:
- `git tag vX.Y.Z && git push --tags`
- `gh release create` で DMG + `.tar.gz` + `.sig` + `latest.json` をアップロード

> **前提**: `gh` (GitHub CLI) がインストール・認証済みであること。未導入の場合: `brew install gh && gh auth login`

### チーム向けインストール手順（初回）

1. [GitHub Releases](https://github.com/collabo-miko/MekuJira/releases) から最新の DMG をダウンロード
2. DMG を開き、MekuJira.app を `/Applications` にドラッグ
3. Gatekeeper を回避（コード署名なしのため）:
   ```bash
   xattr -cr /Applications/MekuJira.app
   ```
4. MekuJira を起動し、JIRA 接続設定を行う

### 更新（2回目以降）

アプリ起動時に自動で更新チェックが行われます。新しいバージョンがある場合は自動的にダウンロード・インストールされます。
