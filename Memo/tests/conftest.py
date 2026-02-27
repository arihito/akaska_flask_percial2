import pytest
from app import create_app
from models import db as _db, User, Category

TEST_CONFIG = {
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'WTF_CSRF_ENABLED': False,
    'SECRET_KEY': 'test-secret-key',
    'MAIL_SUPPRESS_SEND': True,
    'STRIPE_SECRET_KEY': '',
    'GOOGLE_CLIENT_ID': 'dummy',
    'GOOGLE_CLIENT_SECRET': 'dummy',
}


@pytest.fixture(scope='session')
def app():
    """セッション全体で1つのアプリインスタンスを共有する。"""
    flask_app = create_app(TEST_CONFIG)
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()


@pytest.fixture(autouse=True)
def db_rollback(app):
    """各テスト後に DB をロールバックしてデータをリセットする。"""
    with app.app_context():
        yield
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def client(app):
    """Flask テストクライアント。"""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """テスト用一般ユーザーを作成して返す。"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
        )
        user.set_password('Password1!')
        _db.session.add(user)
        _db.session.commit()
        _db.session.refresh(user)
        return user


@pytest.fixture
def other_user(app):
    """別のテスト用ユーザー（認可テスト用）。"""
    with app.app_context():
        user = User(
            username='otheruser',
            email='other@example.com',
        )
        user.set_password('Password1!')
        _db.session.add(user)
        _db.session.commit()
        _db.session.refresh(user)
        return user


@pytest.fixture
def auth_client(app, client, test_user):
    """ログイン済みテストクライアント。"""
    client.post('/auth/', data={
        'email': 'test@example.com',
        'password': 'Password1!',
    }, follow_redirects=False)
    return client


@pytest.fixture
def test_category(app):
    """テスト用カテゴリーを作成して返す。"""
    with app.app_context():
        cat = Category(name='TestCat', color='#123456')
        _db.session.add(cat)
        _db.session.commit()
        _db.session.refresh(cat)
        return cat
