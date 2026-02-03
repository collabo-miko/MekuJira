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

## ライセンス

プロプライエタリ
