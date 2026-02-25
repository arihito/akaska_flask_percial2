# GunicornとNginxによる本番デプロイ

## 開発環境と本番環境の違い

Flask の組み込みサーバー（`flask run`）は開発用途のみで、シングルスレッドかつセキュリティ対策が不十分です。本番環境では WSGI サーバーの **Gunicorn** と リバースプロキシの **Nginx** を組み合わせるのが標準的な構成です。

## Gunicornのセットアップ

### インストール
```bash
pip install gunicorn
```

### 基本的な起動コマンド
```bash
gunicorn -w 4 -b 127.0.0.1:8000 app:app
```

- `-w 4`：ワーカープロセス数（CPUコア数 × 2 + 1 が目安）
- `-b`：バインドアドレスとポート
- `app:app`：モジュール名:アプリインスタンス名

### gunicorn.conf.py による設定管理
```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "/var/log/gunicorn/access.log"
errorlog  = "/var/log/gunicorn/error.log"
loglevel  = "info"
```

```bash
gunicorn -c gunicorn.conf.py app:app
```

## systemd によるサービス管理

Gunicornをサーバー起動時に自動実行するには systemd サービスとして登録します。

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=Gunicorn instance for MyApp
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/myapp
Environment="PATH=/var/www/myapp/venv/bin"
EnvironmentFile=/var/www/myapp/.env
ExecStart=/var/www/myapp/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable myapp
sudo systemctl start myapp
sudo systemctl status myapp
```

## Nginxの設定

GunicornはHTTPを直接公開せず、Nginxをリバースプロキシとして前段に置きます。

```nginx
# /etc/nginx/sites-available/myapp
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/myapp/static;
        expires 30d;
        add_header Cache-Control "public";
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t   # 設定確認
sudo systemctl reload nginx
```

## Let's Encrypt で SSL/TLS を設定

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d example.com
```

Certbot が Nginx 設定を自動更新し、443番ポートへのリダイレクト設定も追加します。証明書は90日有効で、自動更新クロンが登録されます。

## 環境変数の管理

本番環境では `.env` ファイルを直接使わず、systemd の `EnvironmentFile` や OS の環境変数で管理します。

```bash
# 絶対に Git にコミットしない
SECRET_KEY=本番用の複雑な秘密鍵
DATABASE_URL=postgresql://user:password@localhost/myapp
FLASK_ENV=production
```

## まとめ

Gunicorn + Nginx の構成は、Flask アプリの本番デプロイにおける定番です。Gunicorn が Python WSGI を処理し、Nginx が静的ファイル配信・SSL終端・ロードバランシングを担当します。systemd による自動起動設定と Let's Encrypt による HTTPS 化まで行うことで、本番運用に耐えうるサーバー環境が整います。

## GitHub Actionsによる自動デプロイ

コードをプッシュするたびに自動デプロイするCI/CDパイプラインを構築します。

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy via SSH
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /var/www/myapp
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            flask db upgrade
            sudo systemctl restart myapp
```

`secrets` に SSH 秘密鍵やサーバー情報を登録しておくことで、mainブランチへのマージをトリガーに自動デプロイが実行されます。マイグレーションも自動実行されるため、デプロイ漏れを防ぎます。

## Flaskの本番設定

本番環境では必ず `DEBUG=False` に設定し、エラーの詳細が外部に漏洩しないようにします。

```python
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True      # HTTPS限定
    SESSION_COOKIE_HTTPONLY = True    # JS からアクセス不可
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF軽減
    REMEMBER_COOKIE_SECURE = True
```

`PREFERRED_URL_SCHEME = 'https'` を設定すると、`url_for()` が生成するURLが自動的に https スキームになります。
