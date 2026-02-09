# Flask-Migrateによるデータベースマイグレーション

## マイグレーションとは

データベーススキーマの変更履歴を管理し、安全にデータベース構造を更新する仕組みです。Flask-MigrateはAlembicをFlask向けに統合したツールです。

## セットアップ

### インストール
```bash
pip install Flask-Migrate
```

### 初期化
```python
# app.py
from flask_migrate import Migrate
from models import db

migrate = Migrate(app, db)
```

### マイグレーションフォルダの作成
```bash
flask db init
```

これにより`migrations/`ディレクトリが作成されます。

## 基本的なワークフロー

### 1. マイグレーションファイルの生成

モデルを変更した後、以下のコマンドでマイグレーションファイルを自動生成します：

```bash
flask db migrate -m "Add email column to User"
```

### 2. マイグレーションの確認

生成されたファイル（`migrations/versions/xxxx.py`）を確認し、意図した変更が反映されているかチェックします。

### 3. マイグレーションの適用

```bash
flask db upgrade
```

### 4. ロールバック（必要な場合）

```bash
flask db downgrade
```

## 実践例：カラム追加

### モデルの変更
```python
# models.py（変更前）
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))

# models.py（変更後）
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)  # 追加
```

### マイグレーション実行
```bash
flask db migrate -m "Add email to User"
flask db upgrade
```

## 複雑な変更への対応

### データ移行を含むマイグレーション

自動生成されたマイグレーションファイルを編集して、データ変換ロジックを追加できます：

```python
# migrations/versions/xxxx.py
def upgrade():
    op.add_column('users', sa.Column('full_name', sa.String(100)))
    
    # 既存データの変換
    conn = op.get_bind()
    users = conn.execute('SELECT id, first_name, last_name FROM users')
    for user in users:
        full_name = f"{user.first_name} {user.last_name}"
        conn.execute(
            f"UPDATE users SET full_name = '{full_name}' WHERE id = {user.id}"
        )
```

## 本番環境での注意点

### バックアップの取得
```bash
# PostgreSQLの場合
pg_dump mydb > backup.sql
```

### ダウンタイムの最小化
1. 新カラムをNULL許可で追加
2. アプリケーションコードを更新
3. データ移行
4. NOT NULL制約を追加

## トラブルシューティング

### マイグレーション競合の解決
```bash
flask db merge heads
flask db upgrade
```

### 手動でのマイグレーション作成
```bash
flask db revision -m "Custom migration"
```

## まとめ

Flask-Migrateを使うことで、データベーススキーマの変更を安全かつ追跡可能な形で管理できます。特に本番環境では、マイグレーション前に必ずバックアップを取り、段階的に変更を適用することが重要です。
