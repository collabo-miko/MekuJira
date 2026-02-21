# Menubar Template

macOS メニューバー常駐アプリのテンプレート。Tauri 2 + Svelte 5 + NSPanel。

## 機能

- トレイアイコン（メニューバーに常駐）
- 左クリック → NSPanel ポップアップ（フルスクリーン対応）
- 右クリック → Settings / Quit メニュー
- 設定ウィンドウ

## セットアップ

```bash
npm install
npm run tauri dev
```

## ディレクトリ構成

```
src/                    # フロントエンド (Svelte 5)
├── routes/popup/       # ポップアップ画面
└── routes/settings/    # 設定画面

src-tauri/src/          # バックエンド (Rust)
├── lib.rs              # エントリポイント
└── tray/               # トレイアイコン + NSPanel
    ├── mod.rs          # メニュー構成
    ├── panel.rs        # NSPanel 制御
    └── window.rs       # ウィンドウ生成
```

## カスタマイズ

1. `src-tauri/tauri.conf.json` の `productName`, `identifier` を変更
2. `src-tauri/Cargo.toml` の `name`, `[lib] name` を変更
3. `src-tauri/src/main.rs` のクレート名を合わせる
4. `src/routes/popup/+page.svelte` でポップアップの内容を実装
5. `src/routes/settings/+page.svelte` で設定画面を実装
