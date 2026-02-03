# Security Check Assistant

セキュリティチェックシートへの回答作業を効率化するシステム。過去の回答データと参照ドキュメントを活用し、AIが回答案を自動生成します。

## 機能

- **Excelファイル取り込み**: セキュリティチェックシート（Excel形式）をアップロードし、質問を自動抽出
- **フォーマット自動検出**: 複数ベンダーの異なるフォーマットに対応
- **類似回答検索・回答案生成**: PageIndex（推論ベースRAG）と過去回答データベースから回答を生成
- **確信度による品質管理**: 閾値に基づく回答の自動分類
- **バッチ回答生成＋レビューフロー**: 一括生成後にユーザーがレビュー・承認
- **ナレッジベース蓄積**: 承認された回答を蓄積して将来の検索精度を向上

## 技術スタック

| 項目 | 技術 |
|------|------|
| Backend | Python / FastAPI |
| Frontend | Svelte / Tailwind CSS |
| 検索エンジン | PageIndex（推論ベースRAG） |
| データベース | SQLite |
| Excel操作 | openpyxl |

## セットアップ

### 前提条件

- Python 3.11以上
- Node.js 20以上
- (オプション) PageIndex APIキー

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker Compose

```bash
cp .env.example .env
# .env ファイルを編集してAPIキーを設定

docker-compose up -d
```

## 使い方

1. **ドキュメント準備**: PDFドキュメントをアップロードしてインデックス化
2. **Excelアップロード**: セキュリティチェックシートをアップロード
3. **回答生成**: 自動で回答案が生成される
4. **レビュー**: 確信度を確認しながら回答を承認・修正
5. **確定・エクスポート**: 回答を確定してExcelダウンロード

## API エンドポイント

### Excel関連
- `POST /api/excel/upload` - Excelファイルをアップロード
- `GET /api/excel/sessions` - セッション一覧
- `GET /api/excel/sessions/{id}` - セッション詳細

### ドキュメント管理
- `POST /api/documents/upload` - PDFをアップロード
- `GET /api/documents` - ドキュメント一覧
- `DELETE /api/documents/{id}` - ドキュメント削除

### 回答生成
- `POST /api/answer/generate` - 回答を一括生成
- `GET /api/answer/status/{session_id}` - 生成状況

### レビュー・承認
- `GET /api/review/{session_id}` - レビュー対象一覧
- `PUT /api/review/{answer_id}/approve` - 回答を承認
- `PUT /api/review/{answer_id}/modify` - 回答を修正
- `POST /api/review/{session_id}/finalize` - 確定

### エクスポート・レポート
- `GET /api/export/{session_id}/excel` - Excelエクスポート
- `GET /api/report/{session_id}` - レポート取得

## 確信度レベル

| レベル | 閾値 | 説明 |
|--------|------|------|
| 厳格 | 0.95 | ほぼ完全一致のみ |
| やや厳格 | 0.85 | 意図が明確に一致 |
| 標準（デフォルト） | 0.70 | ある程度の類似性 |

## PageIndex設定

### APIキーの取得

1. [PageIndex Dashboard](https://dash.pageindex.ai) にアクセス
2. アカウントを作成またはログイン
3. 「APIキーを生成」をクリック
4. 生成されたキーを `.env` ファイルに設定:

```bash
PAGEINDEX_API_KEY=your_api_key_here
```

### 料金について

| サービス | 単価 | 無料枠 |
|---------|------|--------|
| Tree Generation | $0.01/ページ | 200ページ |
| Chat API | $0.02/クエリ | 100クエリ |
| OCR | $0.01/ページ | 200ページ |

無料枠で十分な試用が可能です。詳細は [PageIndex Pricing](https://pageindex.ai/pricing) をご参照ください。

## データインポート

### kintoneからのCSVエクスポート

過去の回答データをkintoneからインポートする場合:

1. kintoneアプリを開く
2. 「...」→「ファイルに書き出す」→「CSV」を選択
3. 必要なフィールドを選択してエクスポート

### CSVインポート手順

1. CSVファイルを `data/imports/` ディレクトリに配置
2. インポートスクリプトを実行:

```bash
cd backend
python -m app.scripts.import_knowledge data/imports/knowledge.csv
```

### CSVフォーマット

| カラム | 説明 | 必須 |
|--------|------|------|
| question_text | 質問文 | ✓ |
| answer_text | 回答文 | ✓ |
| vendor_name | ベンダー名 | |
| source_document | 参照元 | |
| created_at | 回答日時（YYYY-MM-DD形式） | |

**サンプルCSV:**

```csv
question_text,answer_text,vendor_name,source_document,created_at
"パスワードポリシーについて教えてください","8文字以上、英数字記号を含む必要があります","ベンダーA","セキュリティポリシー.pdf",2024-01-15
```

## トラブルシューティング

### よくあるエラー

#### PageIndex APIエラー

**401 Unauthorized**
- APIキーが未設定または無効です
- `.env` の `PAGEINDEX_API_KEY` を確認してください
- APIキーが正しくコピーされているか確認

**429 Too Many Requests**
- レート制限に達しました
- しばらく待ってから再試行してください

**500 Internal Server Error**
- PageIndexサーバー側の問題の可能性があります
- しばらく待ってから再試行するか、[PageIndex Status](https://status.pageindex.ai) を確認

#### Excelアップロードエラー

**Unsupported format**
- `.xls` ファイルは非対応です
- `.xlsx` 形式で保存し直してからアップロードしてください

**フォーマット検出失敗**
- シートの構造が複雑すぎる場合に発生します
- 対処法:
  - ヘッダー行を1行目に配置
  - 結合セルを解除
  - シンプルな構造に整理

**ファイルサイズ超過**
- 最大10MBまでのファイルに対応しています
- 大きいファイルは分割してアップロードしてください

#### データベースエラー

**Database is locked**
- 複数のプロセスが同時にアクセスしている可能性があります
- アプリケーションを再起動してください

#### フロントエンドエラー

**API Connection Failed**
- バックエンドが起動しているか確認してください
- `http://localhost:8000/health` にアクセスして状態を確認
- CORS設定を確認（`.env` の `CORS_ORIGINS`）

### ログの確認

```bash
# Dockerの場合
docker-compose logs -f backend
docker-compose logs -f frontend

# ローカル実行の場合
# バックエンドのログはコンソールに出力されます
```

### データベースのリセット

問題が解決しない場合、データベースをリセットできます:

```bash
# バックアップを取ってから実行
cp data/knowledge.db data/knowledge.db.backup
rm data/knowledge.db
# アプリケーション再起動で新規作成されます
```

## ライセンス

プロプライエタリ
