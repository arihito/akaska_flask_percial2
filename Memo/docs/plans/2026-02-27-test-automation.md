# テスト自動化 実装計画

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** pytest + pytest-flask で単体・結合テストを整備し、GitHub Actions の Push 時に自動実行して失敗時に main をブロックする CI を構築する。

**Architecture:** `app.py` に `create_app(config_override)` ファクトリ関数を追加してテスト用設定を注入できるようにする。`tests/conftest.py` が SQLite インメモリ DB を使うテスト専用 app を生成し、既存の `factory_boy` でテストデータを作成する。`.github/workflows/test.yml` を書き換えて CI に統合する。

**Tech Stack:** pytest 8.x / pytest-flask 1.3.x / pytest-cov 6.x / factory_boy (既存) / SQLite インメモリ

---

## 前提

- 作業ディレクトリ: `Memo/`
- Python 環境: `conda activate flask2_env`
- 既存の `.env` は変更しない（テストは環境変数を上書きして動かす）

---

### Task 1: create_app() ファクトリ関数を app.py に追加する

**Files:**
- Modify: `app.py`（全体をラップ）

現在 `app.py` はモジュール直下で `app = Flask(...)` を生成している。
テスト用設定を注入できるよう `create_app(config_override=None)` 関数を追加し、
`app = create_app()` でモジュールレベルの後方互換を維持する。

**Step 1: app.py を読んで現状確認**

```bash
cat app.py
```

**Step 2: create_app 関数を追加する**

`app.py` を以下のように書き換える（`if __name__ == '__main__'` は維持）：

```python
from flask import Flask
from flask_migrate import Migrate
from models import db, User, FixedPage
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import NotFound
from errors.views import show_404_page

from public.views import public_bp
from auth.views import auth_bp
from memo.views import memo_bp
from favorite.views import favorite_bp
from docs.views import docs_bp
from fixed.views import fixed_bp
from admin.views import admin_bp
from admin.webhook import webhook_bp

import stripe
from flask_mail import Mail
from dotenv import load_dotenv
load_dotenv()


def create_app(config_override=None):
    """アプリケーションファクトリ。config_override でテスト用設定を上書き可能。"""
    app = Flask(__name__)
    app.config.from_object('config.Config')

    if config_override:
        app.config.update(config_override)

    stripe.api_key = app.config['STRIPE_SECRET_KEY']
    db.init_app(app)

    # SQLite の FOREIGN KEY 制約を有効化
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    import sqlite3

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    Mail(app)
    if not app.testing:
        DebugToolbarExtension(app)
    Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_message = '認証していません：ログインしてください'
    login_manager.login_view = 'auth.login'

    app.register_error_handler(NotFound, show_404_page)
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(memo_bp)
    app.register_blueprint(favorite_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(fixed_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(webhook_bp)

    @app.context_processor
    def inject_static_pages():
        try:
            pages = FixedPage.query.filter_by(visible=True).order_by(FixedPage.order).all()
            GLOBAL_NAV_PAGES = {p.key: p.title for p in pages if p.nav_type == 'global'}
            FOOTER_NAV_PAGES = {p.key: p.title for p in pages if p.nav_type == 'footer'}
        except Exception:
            GLOBAL_NAV_PAGES = {}
            FOOTER_NAV_PAGES = {}
        return dict(
            GLOBAL_NAV_PAGES=GLOBAL_NAV_PAGES,
            FOOTER_NAV_PAGES=FOOTER_NAV_PAGES,
            SITE_NAME=app.config['SITE_NAME'],
        )

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


# モジュールレベルの後方互換（gunicorn 等が参照）
app = create_app()

if __name__ == '__main__':
    app.run()
```

**Step 3: アプリが起動するか確認**

```bash
FLASK_DEBUG=1 python app.py &
sleep 2
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/
# 期待: 200
kill %1
```

**Step 4: コミット**

```bash
git add Memo/app.py
git commit -m "refactor: extract create_app() factory for testability"
```

---

### Task 2: テスト用パッケージを requirements.txt に追加する

**Files:**
- Modify: `requirements.txt`

**Step 1: 現在の requirements.txt を確認**

```bash
grep -E "pytest|coverage" requirements.txt
# 期待: 何も出力されない（未追加）
```

**Step 2: パッケージを追加インストールしてバージョンを固定**

```bash
conda run -n flask2_env pip install pytest==8.3.5 pytest-flask==1.3.0 pytest-cov==6.1.0
conda run -n flask2_env pip freeze | grep -E "pytest|coverage" >> requirements.txt
```

**Step 3: requirements.txt にエントリが追加されたか確認**

```bash
grep -E "pytest|coverage" requirements.txt
# 期待:
# coverage==7.x.x
# pytest==8.3.5
# pytest-cov==6.1.0
# pytest-flask==1.3.0
```

**Step 4: コミット**

```bash
git add Memo/requirements.txt
git commit -m "chore: add pytest, pytest-flask, pytest-cov to requirements"
```

---

### Task 3: pytest.ini を作成する

**Files:**
- Create: `pytest.ini`

**Step 1: pytest.ini を作成する**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

**Step 2: pytest がテストを検出できるか確認（まだテストがないので 0 件で OK）**

```bash
conda run -n flask2_env pytest --collect-only
# 期待: "no tests ran" または空のテストスイート
```

**Step 3: コミット**

```bash
git add Memo/pytest.ini
git commit -m "chore: add pytest.ini configuration"
```

---

### Task 4: tests/conftest.py を作成する

**Files:**
- Create: `tests/__init__.py`（空ファイル）
- Create: `tests/conftest.py`

**Step 1: tests ディレクトリと conftest.py を作成する**

```python
# tests/conftest.py
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
        # テーブルをクリア（外部キー制約を考慮した順序）
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
        # セッションから切り離してリフレッシュ
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
```

**Step 2: `tests/__init__.py` を作成する（空ファイル）**

```bash
touch tests/__init__.py
```

**Step 3: conftest だけで pytest が通るか確認**

```bash
conda run -n flask2_env pytest --collect-only
# 期待: "no tests ran"（エラーなし）
```

**Step 4: コミット**

```bash
git add Memo/tests/
git commit -m "test: add conftest.py with test fixtures"
```

---

### Task 5: tests/test_models.py を作成する（単体テスト）

**Files:**
- Create: `tests/test_models.py`

**Step 1: テストを書く**

```python
# tests/test_models.py
import pytest
from sqlalchemy.exc import IntegrityError
from models import db, User, Memo, Category


class TestUserModel:
    def test_password_is_hashed(self, app):
        """パスワードが平文でなくハッシュ化されて保存される。"""
        with app.app_context():
            user = User(username='hashtest', email='hash@example.com')
            user.set_password('MyPassword1!')
            assert user.password != 'MyPassword1!'
            assert user.password.startswith('scrypt:') or user.password.startswith('pbkdf2:')

    def test_check_password_correct(self, app):
        """正しいパスワードで check_password が True を返す。"""
        with app.app_context():
            user = User(username='chktest', email='chk@example.com')
            user.set_password('MyPassword1!')
            assert user.check_password('MyPassword1!') is True

    def test_check_password_wrong(self, app):
        """誤ったパスワードで check_password が False を返す。"""
        with app.app_context():
            user = User(username='wrongtest', email='wrong@example.com')
            user.set_password('MyPassword1!')
            assert user.check_password('WrongPassword') is False

    def test_email_unique_constraint(self, app):
        """同じメールアドレスで2件目のユーザー作成は IntegrityError になる。"""
        with app.app_context():
            u1 = User(username='u1', email='dup@example.com')
            u1.set_password('Pass1!')
            db.session.add(u1)
            db.session.commit()

            u2 = User(username='u2', email='dup@example.com')
            u2.set_password('Pass1!')
            db.session.add(u2)
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_is_oauth_user_false_for_normal(self, app):
        """通常ユーザーは is_oauth_user が False。"""
        with app.app_context():
            user = User(username='normal', email='normal@example.com')
            user.set_password('Pass1!')
            assert user.is_oauth_user is False


class TestMemoModel:
    def test_create_memo(self, app, test_user):
        """Memo をDBに保存できる。"""
        with app.app_context():
            user = db.session.get(User, test_user.id)
            memo = Memo(title='テストタイトル', content='テスト本文', user_id=user.id)
            db.session.add(memo)
            db.session.commit()
            saved = db.session.get(Memo, memo.id)
            assert saved.title == 'テストタイトル'


class TestCategoryModel:
    def test_category_name_unique(self, app):
        """同名カテゴリーの2件目は IntegrityError になる。"""
        with app.app_context():
            c1 = Category(name='UniqueTest', color='#111111')
            db.session.add(c1)
            db.session.commit()

            c2 = Category(name='UniqueTest', color='#222222')
            db.session.add(c2)
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()
```

**Step 2: テストを実行して結果を確認**

```bash
conda run -n flask2_env pytest tests/test_models.py -v
# 期待: 全テスト PASSED
```

**Step 3: 失敗したテストがある場合はコードを修正する**

（エラーメッセージを見てフィクスチャや DB 設定を確認）

**Step 4: コミット**

```bash
git add Memo/tests/test_models.py
git commit -m "test: add unit tests for User, Memo, Category models"
```

---

### Task 6: tests/test_public.py を作成する（公開ページ結合テスト）

**Files:**
- Create: `tests/test_public.py`

**Step 1: テストを書く**

```python
# tests/test_public.py
from models import db, Memo, User


class TestPublicPages:
    def test_top_page_returns_200(self, client):
        """トップページ '/' が 200 を返す。"""
        res = client.get('/')
        assert res.status_code == 200

    def test_top_page_with_search_returns_200(self, client):
        """検索クエリ付きトップページが 200 を返す。"""
        res = client.get('/?q=test')
        assert res.status_code == 200

    def test_top_page_with_category_returns_200(self, client, test_category):
        """カテゴリー絞り込みが 200 を返す。"""
        res = client.get(f'/?category_id={test_category.id}')
        assert res.status_code == 200

    def test_detail_page_returns_200(self, app, client, test_user):
        """詳細ページが 200 を返す。"""
        with app.app_context():
            user = db.session.get(User, test_user.id)
            memo = Memo(title='公開テスト', content='本文', user_id=user.id)
            db.session.add(memo)
            db.session.commit()
            memo_id = memo.id

        res = client.get(f'/detail/{memo_id}')
        assert res.status_code == 200

    def test_nonexistent_page_returns_404(self, client):
        """存在しないパスが 404 を返す。"""
        res = client.get('/nonexistent-path-xyz')
        assert res.status_code == 404
```

**Step 2: テストを実行**

```bash
conda run -n flask2_env pytest tests/test_public.py -v
# 期待: 全テスト PASSED
```

**Step 3: コミット**

```bash
git add Memo/tests/test_public.py
git commit -m "test: add integration tests for public pages"
```

---

### Task 7: tests/test_auth.py を作成する（認証結合テスト）

**Files:**
- Create: `tests/test_auth.py`

**Step 1: テストを書く**

```python
# tests/test_auth.py


class TestLogin:
    def test_login_success_redirects(self, client, test_user):
        """正しい認証情報でログインすると 302 リダイレクトになる。"""
        res = client.post('/auth/', data={
            'email': 'test@example.com',
            'password': 'Password1!',
        })
        assert res.status_code == 302

    def test_login_wrong_password_returns_200(self, client, test_user):
        """誤ったパスワードでは 200 を返しエラーが表示される。"""
        res = client.post('/auth/', data={
            'email': 'test@example.com',
            'password': 'WrongPassword!',
        })
        assert res.status_code == 200
        assert 'メールアドレスまたはパスワードが正しくありません'.encode() in res.data

    def test_login_unknown_email_returns_200(self, client):
        """存在しないメールアドレスでも 200 を返す（セキュリティ：原因を限定表示しない）。"""
        res = client.post('/auth/', data={
            'email': 'nobody@example.com',
            'password': 'Password1!',
        })
        assert res.status_code == 200

    def test_logout_redirects(self, auth_client):
        """ログアウトすると 302 リダイレクトになる。"""
        res = auth_client.get('/auth/logout')
        assert res.status_code == 302


class TestAccessControl:
    def test_memo_index_requires_login(self, client):
        """未ログインで /memo/ にアクセスすると /auth/login へリダイレクトされる。"""
        res = client.get('/memo/')
        assert res.status_code == 302
        assert '/auth/' in res.headers['Location']

    def test_memo_create_requires_login(self, client):
        """未ログインで /memo/create にアクセスするとリダイレクトされる。"""
        res = client.get('/memo/create')
        assert res.status_code == 302
        assert '/auth/' in res.headers['Location']

    def test_logged_in_can_access_memo_index(self, auth_client):
        """ログイン済みで /memo/ にアクセスすると 200 を返す。"""
        res = auth_client.get('/memo/')
        assert res.status_code == 200
```

**Step 2: テストを実行**

```bash
conda run -n flask2_env pytest tests/test_auth.py -v
# 期待: 全テスト PASSED
```

**Step 3: コミット**

```bash
git add Memo/tests/test_auth.py
git commit -m "test: add integration tests for authentication and access control"
```

---

### Task 8: tests/test_memo.py を作成する（投稿 CRUD 結合テスト）

**Files:**
- Create: `tests/test_memo.py`

**Step 1: テストを書く**

```python
# tests/test_memo.py
from models import db, Memo, User


class TestMemoCRUD:
    def test_create_memo_saves_to_db(self, app, auth_client, test_user):
        """投稿作成フォームの POST で DB に1件追加される。"""
        with app.app_context():
            before = Memo.query.count()

        res = auth_client.post('/memo/create', data={
            'title': 'テスト投稿タイトル',
            'content': 'テスト投稿の本文です。',
        }, follow_redirects=False)

        # 作成成功後は /memo/ にリダイレクト
        assert res.status_code == 302

        with app.app_context():
            after = Memo.query.count()
            assert after == before + 1

    def test_update_own_memo(self, app, auth_client, test_user):
        """自分の投稿を編集すると 302 リダイレクトになる。"""
        with app.app_context():
            user = db.session.get(User, test_user.id)
            memo = Memo(title='編集前タイトル', content='編集前本文', user_id=user.id)
            db.session.add(memo)
            db.session.commit()
            memo_id = memo.id

        res = auth_client.post(f'/memo/update/{memo_id}', data={
            'title': '編集後タイトル',
            'content': '編集後本文',
        }, follow_redirects=False)
        assert res.status_code == 302

        with app.app_context():
            updated = db.session.get(Memo, memo_id)
            assert updated.title == '編集後タイトル'

    def test_update_other_memo_returns_403(self, app, client, test_user, other_user):
        """他人の投稿を編集しようとすると 403 を返す。"""
        # other_user の投稿を作成
        with app.app_context():
            other = db.session.get(User, other_user.id)
            memo = Memo(title='他人の投稿', content='他人の本文', user_id=other.id)
            db.session.add(memo)
            db.session.commit()
            memo_id = memo.id

        # test_user でログイン
        client.post('/auth/', data={
            'email': 'test@example.com',
            'password': 'Password1!',
        })

        # 他人の投稿を編集しようとする
        res = client.post(f'/memo/update/{memo_id}', data={
            'title': '不正編集',
            'content': '不正本文',
        })
        assert res.status_code == 403

    def test_delete_memo_removes_from_db(self, app, auth_client, test_user):
        """投稿削除後に DB の件数が1減る。"""
        with app.app_context():
            user = db.session.get(User, test_user.id)
            memo = Memo(title='削除対象', content='削除対象本文', user_id=user.id)
            db.session.add(memo)
            db.session.commit()
            memo_id = memo.id
            before = Memo.query.count()

        auth_client.post(f'/memo/delete/{memo_id}')

        with app.app_context():
            after = Memo.query.count()
            assert after == before - 1
```

**Step 2: テストを実行**

```bash
conda run -n flask2_env pytest tests/test_memo.py -v
# 期待: 全テスト PASSED
# ※ 403 テストが失敗する場合は memo/views.py の update ルートに abort(403) がない可能性があるため確認
```

**Step 3: 403 テスト失敗時の対処**

`memo/views.py` の `update` ルートに認可チェックがない場合は追加：

```python
# memo/views.py の update ルート内、memo を取得した直後に追加
memo = Memo.query.get_or_404(memo_id)
if memo.user_id != current_user.id:
    abort(403)
```

**Step 4: 全テストをまとめて実行してカバレッジを確認**

```bash
conda run -n flask2_env pytest --cov=. --cov-report=term-missing
# 期待: 全テスト PASSED
```

**Step 5: コミット**

```bash
git add Memo/tests/test_memo.py
git commit -m "test: add integration tests for memo CRUD and authorization"
```

---

### Task 9: GitHub Actions の test.yml を書き換える

**Files:**
- Modify: `.github/workflows/test.yml`

**Step 1: 現在の test.yml を確認**

```bash
cat .github/workflows/test.yml
# 現状: echo "GitHub Actions is working" のみ
```

**Step 2: test.yml を書き換える**

`.github/workflows/test.yml` を以下に書き換える：

```yaml
name: CI Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r Memo/requirements.txt

      - name: Run tests with coverage
        working-directory: Memo
        env:
          SECRET_KEY: test-secret-key-for-ci
          DATABASE_URL: sqlite:///:memory:
          GOOGLE_CLIENT_ID: dummy
          GOOGLE_CLIENT_SECRET: dummy
          STRIPE_SECRET_KEY: ""
          STRIPE_WEBHOOK_SECRET: ""
          MAIL_USERNAME: ""
          MAIL_PASSWORD: ""
          GOOGLE_API_KEY: ""
        run: pytest --cov=. --cov-report=term-missing --cov-fail-under=30
```

**Note:** `--cov-fail-under=30` は最低 30% カバレッジ未満でテストを失敗にする。最初は低めに設定し、テストを追加するたびに引き上げる。

**Step 3: コミットして GitHub Actions を確認**

```bash
git add .github/workflows/test.yml
git commit -m "ci: replace placeholder with real pytest + coverage workflow"
git push origin main
```

**Step 4: GitHub Actions のログを確認**

```bash
gh run list --limit 3
gh run view <run-id>
# 期待: test ジョブが SUCCESS
```

---

### Task 10: GitHub Branch Protection Rules を設定する（オプション）

**目的:** テスト失敗時に main への直接 Push をブロックする。

**Step 1: GitHub リポジトリ設定で Branch Protection を有効化**

1. GitHub リポジトリ → Settings → Branches
2. "Add branch protection rule" → Branch name pattern: `main`
3. "Require status checks to pass before merging" を ON
4. "Status checks that are required" に `test` を追加
5. "Do not allow bypassing the above settings" を ON
6. Save changes

この設定は GUI のみ（CLI / YAML では設定できない）。

---

## 動作確認チェックリスト

- [ ] `pytest` をローカルで実行して全テスト PASSED
- [ ] `pytest --cov` でカバレッジレポートが表示される
- [ ] GitHub Actions で Push 後に `test` ジョブが SUCCESS になる
- [ ] test.yml に `--cov-fail-under=30` が設定されている
- [ ] （オプション）Branch Protection で main が守られている

## テストが失敗したときのデバッグ方法

```bash
# 詳細出力付きで1ファイルのみ実行
conda run -n flask2_env pytest tests/test_auth.py -v --tb=long

# 特定テストのみ実行
conda run -n flask2_env pytest tests/test_auth.py::TestLogin::test_login_success_redirects -v

# print 出力を表示
conda run -n flask2_env pytest -s tests/test_models.py
```
