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
