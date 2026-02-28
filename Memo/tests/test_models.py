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
