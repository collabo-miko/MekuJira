# デプロイガイド

本番環境へのデプロイ手順を説明します。

## 目次

- [Docker Compose（推奨）](#docker-compose推奨)
- [AWS EC2へのデプロイ](#aws-ec2へのデプロイ)
- [その他の環境](#その他の環境)
- [データのバックアップ](#データのバックアップ)
- [監視・メンテナンス](#監視メンテナンス)

## Docker Compose（推奨）

### 前提条件

- Docker 24.0以上
- Docker Compose 2.20以上
- メモリ: 2GB以上推奨
- ディスク: 10GB以上

### 本番用設定

1. `.env` ファイルを作成:

```bash
cp .env.example .env
```

2. `.env` ファイルを編集:

```bash
# 必須
PAGEINDEX_API_KEY=your_production_api_key

# サーバー設定
HOST=0.0.0.0
PORT=8000

# 確信度閾値（必要に応じて調整）
DEFAULT_CONFIDENCE_THRESHOLD=0.70

# CORS設定（本番ドメインに変更）
CORS_ORIGINS=["https://your-domain.com"]
```

3. 本番用ビルド:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

4. 動作確認:

```bash
# ヘルスチェック
curl http://localhost:8000/health

# ログ確認
docker-compose -f docker-compose.prod.yml logs -f
```

## AWS EC2へのデプロイ

### 推奨スペック

| 用途 | インスタンスタイプ | メモリ | ストレージ |
|------|-------------------|--------|-----------|
| 開発・検証 | t3.small | 2GB | 20GB |
| 本番（小規模） | t3.medium | 4GB | 50GB |
| 本番（中規模） | t3.large | 8GB | 100GB |

### セキュリティグループ設定

| ポート | プロトコル | ソース | 用途 |
|--------|-----------|--------|------|
| 22 | TCP | 管理用IP | SSH |
| 80 | TCP | 0.0.0.0/0 | HTTP |
| 443 | TCP | 0.0.0.0/0 | HTTPS |

### デプロイ手順

1. **EC2インスタンスにSSH接続**:

```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

2. **Dockerをインストール**:

```bash
# Amazon Linux 2
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

3. **リポジトリをクローン**:

```bash
git clone <repo-url> security-check-assistant
cd security-check-assistant
```

4. **環境変数を設定**:

```bash
cp .env.example .env
nano .env  # 編集
```

5. **データディレクトリを作成**:

```bash
mkdir -p data/documents data/uploads data/imports
```

6. **起動**:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Nginx リバースプロキシ設定（オプション）

HTTPS対応やドメイン設定にはNginxを使用します。

1. **Nginxをインストール**:

```bash
sudo amazon-linux-extras install nginx1 -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

2. **設定ファイルを作成** `/etc/nginx/conf.d/security-check.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # HTTP to HTTPS redirect
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # File upload size
        client_max_body_size 20M;
    }
}
```

3. **SSL証明書を取得（Let's Encrypt）**:

```bash
sudo yum install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## その他の環境

### ローカルサーバー

Docker Composeが使用できない環境では、直接実行も可能です。

**バックエンド**:

```bash
cd backend
pip install -r requirements.txt
pip install gunicorn

# 本番実行
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

**フロントエンド**:

```bash
cd frontend
npm ci
npm run build

# Node.js + Adapter-nodeの場合
node build
```

### Systemdサービス化

サーバー再起動後も自動起動させる場合:

1. **サービスファイルを作成** `/etc/systemd/system/security-check.service`:

```ini
[Unit]
Description=Security Check Assistant
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/security-check-assistant
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
Restart=always

[Install]
WantedBy=multi-user.target
```

2. **サービスを有効化**:

```bash
sudo systemctl daemon-reload
sudo systemctl enable security-check
sudo systemctl start security-check
```

## データのバックアップ

### SQLiteデータベース

```bash
# 手動バックアップ
cp data/knowledge.db data/backups/knowledge_$(date +%Y%m%d_%H%M%S).db
```

### 定期バックアップ（cron）

1. **バックアップスクリプト** `scripts/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/ec2-user/security-check-assistant/data/backups"
DATA_DIR="/home/ec2-user/security-check-assistant/data"
RETENTION_DAYS=30

# バックアップディレクトリ作成
mkdir -p $BACKUP_DIR

# データベースバックアップ
cp $DATA_DIR/knowledge.db $BACKUP_DIR/knowledge_$(date +%Y%m%d_%H%M%S).db

# ドキュメントバックアップ
tar -czf $BACKUP_DIR/documents_$(date +%Y%m%d_%H%M%S).tar.gz $DATA_DIR/documents/

# 古いバックアップを削除
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $(date)"
```

2. **cron設定**:

```bash
chmod +x scripts/backup.sh
crontab -e

# 毎日午前2時にバックアップ
0 2 * * * /home/ec2-user/security-check-assistant/scripts/backup.sh >> /var/log/backup.log 2>&1
```

### S3へのバックアップ（推奨）

```bash
# AWS CLIでS3にアップロード
aws s3 sync data/backups/ s3://your-bucket/security-check-backups/
```

## 監視・メンテナンス

### ヘルスチェック

```bash
# APIヘルスチェック
curl -f http://localhost:8000/health || echo "Backend is down"
```

### ディスク使用量監視

```bash
# データディレクトリのサイズ確認
du -sh data/

# アップロードファイルのクリーンアップ（30日以上前）
find data/uploads -type f -mtime +30 -delete
```

### ログローテーション

Dockerのログは肥大化する可能性があります。`/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

設定後、Dockerを再起動:

```bash
sudo systemctl restart docker
```

### アップデート手順

1. **バックアップ実行**:

```bash
./scripts/backup.sh
```

2. **更新を取得**:

```bash
git pull origin main
```

3. **コンテナを再ビルド**:

```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

4. **動作確認**:

```bash
curl http://localhost:8000/health
docker-compose -f docker-compose.prod.yml logs -f
```
