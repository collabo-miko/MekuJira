# JIRA Focus

macOSメニューバーに常駐し、JIRA Cloud の課題一覧を表示するデスクトップアプリ。
ユーザーが集中して作業する課題をピックアップし、デスクトップ上にフローティングウィジェットとして常時表示する。

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

## 機能

- **メニューバー常駐**: macOSメニューバーにトレイアイコンとして常駐
- **課題一覧**: JIRA Cloud からJQLで課題を取得・表示
- **集中モード**: 課題をピックアップしてフローティングウィジェットに表示
- **自動更新**: 定期ポーリングで課題データを自動取得
- **セキュア**: APIトークンはmacOS Keychainに保存
