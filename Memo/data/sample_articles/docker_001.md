# DockerによるFlaskアプリのコンテナ化

## Dockerとは

Docker はアプリケーションとその依存関係を「コンテナ」として一まとめにし、どの環境でも同じように動作させる仮想化技術です。「開発環境では動くが本番では動かない」問題を根本から解消し、環境構築の再現性を保証します。

## Dockerfileの作成

```dockerfile
# Dockerfile
FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# 依存関係のインストール（キャッシュ最適化のため先にコピー）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリコードをコピー
COPY . .

# 環境変数
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# ポート公開
EXPOSE 5000

# 起動コマンド（本番はGunicorn推奨）
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### .dockerignore の設定

不要なファイルをイメージに含めないよう `.dockerignore` を作成します。

```
__pycache__/
*.pyc
.env
.git
instance/
venv/
*.sqlite
```

## Docker Compose による複数サービス管理

Flask アプリ・データベース・Redis などを一括管理するには `docker-compose.yml` を使います。

```yaml
# docker-compose.yml
version: '3.9'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=postgresql://postgres:password@db:5432/appdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - .:/app  # 開発時はホストのコードをマウント
      - upload_data:/app/static/uploads

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
  upload_data:
```

```bash
# 全サービスをビルド＆起動
docker compose up --build

# バックグラウンドで起動
docker compose up -d

# ログ確認
docker compose logs -f web

# 停止
docker compose down
```

## 開発用コンテナの活用

開発時はホストのコードをボリュームマウントすることで、コンテナを再ビルドせずにコード変更を即時反映できます。

```yaml
# docker-compose.dev.yml
services:
  web:
    environment:
      - FLASK_DEBUG=1
    command: flask run --host=0.0.0.0
    volumes:
      - .:/app
```

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

本番用の `docker-compose.yml` と開発用オーバーライドを分離することで、環境ごとの設定を明確に管理できます。

## DBマイグレーションの実行

```bash
# コンテナ内でマイグレーション
docker compose exec web flask db upgrade

# または起動時に自動実行（CMD で指定）
CMD ["sh", "-c", "flask db upgrade && gunicorn -w 4 -b 0.0.0.0:5000 app:app"]
```

## まとめ

Docker によるコンテナ化は、Flask アプリの開発・テスト・本番環境の一貫性を保証します。`docker-compose.yml` で複数サービスを宣言的に定義し、`docker compose up` 一発で全環境を再現できます。チーム開発における「環境依存のバグ」を排除し、新メンバーのオンボーディングも大幅に簡略化されます。

## マルチステージビルド

イメージサイズを削減するためにマルチステージビルドを使います。

```dockerfile
# ビルドステージ
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 実行ステージ（軽量イメージ）
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

ビルドに必要なツール（コンパイラ等）を最終イメージに含めないため、イメージサイズを大幅に削減できます。本番環境での攻撃面を最小化するセキュリティ上のメリットもあります。

## ヘルスチェックの設定

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1
```

```python
# app.py にヘルスチェックエンドポイントを追加
@app.route('/health')
def health():
    return {'status': 'ok'}, 200
```

Docker Compose や Kubernetes がコンテナの死活監視に使います。ヘルスチェックが失敗すると自動的にコンテナが再起動されます。
