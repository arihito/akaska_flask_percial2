# Pytestによるテスト自動化

## テストの重要性

Webアプリの品質を維持するためには、変更のたびに手動でテストを繰り返すのは非効率です。Pytestを使った自動テストを導入することで、バグの早期発見・デグレ防止・リファクタリングの安全性確保が実現できます。

## Pytestのセットアップ

### インストール
```bash
pip install pytest pytest-flask
```

### ディレクトリ構成
```
project/
├── app.py
├── models.py
└── tests/
    ├── conftest.py
    ├── test_auth.py
    └── test_memo.py
```

## conftest.py の作成

テストで共通して使う fixture を `conftest.py` に定義します。

```python
# tests/conftest.py
import pytest
from app import create_app
from models import db as _db

@pytest.fixture(scope='session')
def app():
    """テスト用アプリインスタンス（セッション中1回生成）"""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret',
    })
    return app

@pytest.fixture(scope='session')
def db(app):
    """テスト用DBの初期化"""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture(autouse=True)
def db_transaction(db):
    """各テストをトランザクションで囲みロールバック（テスト間の干渉を防止）"""
    connection = db.engine.connect()
    transaction = connection.begin()
    db.session.bind = connection
    yield
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(app):
    return app.test_client()
```

`autouse=True` を使うと、全テストに自動適用されます。各テスト後にDBがロールバックされるため、テスト間でデータが混入しません。

## 単体テストの書き方

### モデルのテスト
```python
# tests/test_models.py
def test_user_password_hash(db):
    from models import User
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')

    assert user.check_password('password123') is True
    assert user.check_password('wrong') is False
    assert user.password != 'password123'  # ハッシュ化されている
```

### ビューのテスト
```python
# tests/test_auth.py
def test_login_success(client, db):
    from models import User
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.flush()

    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123',
    }, follow_redirects=True)

    assert response.status_code == 200

def test_login_fail(client):
    response = client.post('/auth/login', data={
        'email': 'notexist@example.com',
        'password': 'wrong',
    })
    assert b'パスワード' in response.data or response.status_code == 200
```

## 認証状態のテスト

Flask-Login の認証が必要なルートをテストするには、ログイン状態をセッションに設定します。

```python
from flask_login import login_user

def test_memo_create_requires_login(client):
    """未ログインではリダイレクトされる"""
    response = client.get('/memo/create')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']

def test_memo_create_logged_in(client, db):
    from models import User
    user = User(username='writer', email='writer@example.com')
    user.set_password('pass')
    db.session.add(user)
    db.session.flush()

    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)

    response = client.get('/memo/create')
    assert response.status_code == 200
```

## パラメータ化テスト

`@pytest.mark.parametrize` を使うと、複数のパターンを1つのテストでカバーできます。

```python
@pytest.mark.parametrize('email,password,expected', [
    ('valid@example.com', 'correct', 200),
    ('valid@example.com', 'wrong', 200),  # ログイン失敗でも200返す
    ('', '', 200),
])
def test_login_patterns(client, email, password, expected):
    response = client.post('/auth/login', data={
        'email': email, 'password': password,
    })
    assert response.status_code == expected
```

## テストカバレッジの計測

```bash
pip install pytest-cov
pytest --cov=. --cov-report=html tests/
```

`htmlcov/index.html` をブラウザで開くと、カバレッジレポートが確認できます。テスト対象外のコードが赤く表示されるため、テストすべき箇所が一目でわかります。

## まとめ

Pytestによる自動テストは、Flaskアプリの品質維持に不可欠です。conftest.pyでfixtureを一元管理し、DBトランザクションを使ってテストを分離することで、高速かつ信頼性の高いテストスイートを構築できます。CI/CDパイプラインに組み込むことで、プッシュのたびに自動実行される継続的品質チェックが実現します。

## モックを使ったテスト

外部サービス（メール送信・API呼び出し等）はモックで差し替えることで、テストの安定性と速度を確保します。

```python
from unittest.mock import patch, MagicMock

def test_send_welcome_email(client, db):
    with patch('auth.views.mail.send') as mock_send:
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Password1!',
            'password_confirm': 'Password1!',
        })
        # メール送信が1回呼ばれたことを確認
        mock_send.assert_called_once()
```

`patch` デコレータで対象モジュールのオブジェクトを差し替え、実際の送信処理を発生させずに呼び出し確認ができます。外部依存を排除することで、ネットワーク環境に左右されない安定したテストが実現します。

## フィクスチャのスコープ設計

Pytestのfixture は `scope` によってライフタイムが変わります。

| scope | 生存期間 |
|-------|---------|
| `function` | 各テスト関数ごと（デフォルト） |
| `class` | テストクラスごと |
| `module` | テストファイルごと |
| `session` | テストセッション全体で1回 |

重いセットアップ（DBスキーマ生成・外部サービス初期化等）は `session` スコープ、データ投入は `function` スコープで行うのが定石です。スコープが上位のfixture が下位のfixture に依存するとエラーになる点に注意が必要です。
