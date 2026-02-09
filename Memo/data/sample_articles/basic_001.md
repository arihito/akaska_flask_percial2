# FlaskにおけるBlueprint分割設計の基本

## はじめに

Flaskアプリケーションが大規模化するにつれ、すべての機能を単一の`app.py`に詰め込むと保守性が著しく低下します。Blueprint機能を活用することで、機能ごとにモジュールを分割し、見通しの良いプロジェクト構造を実現できます。

## Blueprintとは

Blueprintは、Flaskアプリケーションを複数の独立したコンポーネントに分割するための仕組みです。各Blueprintは独自のルート、テンプレート、静的ファイルを持つことができます。

### 基本的な使い方

```python
from flask import Blueprint

# Blueprintの定義
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login():
    return 'ログインページ'
```

### メインアプリへの登録

```python
from flask import Flask
from auth.views import auth_bp

app = Flask(__name__)
app.register_blueprint(auth_bp)
```

## ディレクトリ構成のベストプラクティス

推奨されるプロジェクト構造は以下の通りです：

```
myproject/
├── app.py
├── config.py
├── models.py
├── auth/
│   ├── __init__.py
│   └── views.py
├── blog/
│   ├── __init__.py
│   └── views.py
└── templates/
    ├── auth/
    └── blog/
```

## 循環インポート問題の回避

Blueprint分割時によく発生する循環インポート問題は、Application Factoryパターンで解決できます。

```python
# app.py
def create_app():
    app = Flask(__name__)
    
    from auth.views import auth_bp
    from blog.views import blog_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(blog_bp)
    
    return app
```

## まとめ

Blueprintを活用することで、大規模なFlaskアプリケーションを管理しやすい単位に分割できます。各機能が独立したモジュールとして動作するため、チーム開発やテストも容易になります。次のステップとして、各Blueprint内でのフォーム処理やデータベース操作を実装していきましょう。
