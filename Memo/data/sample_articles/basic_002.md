# Application Factoryパターンによる設定管理

## Application Factoryパターンとは

Flaskアプリケーションを関数内で生成するデザインパターンです。これにより、異なる設定を持つ複数のアプリインスタンスを柔軟に作成できます。

## 従来の問題点

通常、Flaskアプリは以下のように作成します：

```python
# app.py
from flask import Flask

app = Flask(__name__)
app.config['DEBUG'] = True
```

この方法では、テスト用と本番用で異なる設定を使い分けることが困難です。

## Application Factoryの実装

```python
# app.py
from flask import Flask
from config import config

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 拡張機能の初期化
    from models import db
    db.init_app(app)
    
    # Blueprintの登録
    from auth.views import auth_bp
    app.register_blueprint(auth_bp)
    
    return app
```

## 設定クラスの分離

```python
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
```

## テスト時の活用

Application Factoryパターンを使うと、テスト用の設定で独立したアプリインスタンスを作成できます：

```python
# tests/test_app.py
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
```

## 環境変数による設定切り替え

```python
# run.py
import os
from app import create_app

env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    app.run()
```

## メリットとデメリット

### メリット
- テストが書きやすい
- 設定の一元管理
- 複数インスタンスの作成が可能

### デメリット
- 初期コードが若干複雑
- グローバルな`app`オブジェクトが使えない

## まとめ

Application Factoryパターンは、Flaskアプリケーションのスケーラビリティと保守性を大幅に向上させます。特に、本番環境とテスト環境で異なる設定を使い分ける必要がある場合には必須の手法です。
