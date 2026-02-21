# macOS Menu Bar Apps

macOS メニューバー常駐アプリのプロジェクト。

## 構成

| ディレクトリ | 説明 |
|-------------|------|
| `MekuJira/` | JIRA Cloud 課題管理アプリ |
| `template/` | 最小構成メニューバーアプリ テンプレート |

## 技術スタック

- **Tauri 2** + **Svelte 5** + **TypeScript**
- **NSPanel** によるフルスクリーン対応ポップアップ
- macOS 13 (Ventura) 以降

## 始め方

```bash
# MekuJira を開発
cd MekuJira && npm install && npm run tauri dev

# テンプレートから新しいアプリを作る
cp -r template MyApp
cd MyApp && npm install && npm run tauri dev
```
