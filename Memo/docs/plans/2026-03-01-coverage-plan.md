# テストカバレッジ改善 実装プラン

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** factories/seed/admin/docs/utils-AI を除外し、コアモジュールのカバレッジを 90% 以上に引き上げる

**Architecture:** `.coveragerc` に除外設定を追加し、`pytest.ini` の `--cov-fail-under` を 90 に変更。既存 conftest.py の fixture を再利用しつつ、8 ファイルにテストを追加・新規作成する。

**Tech Stack:** pytest, pytest-cov, Flask test client, werkzeug.datastructures.FileStorage, unittest.mock

---

### Task 1: `.coveragerc` 作成と `pytest.ini` 更新

**Files:**
- Create: `.coveragerc`
- Modify: `pytest.ini`

**Step 1: `.coveragerc` を新規作成**

`Memo/.coveragerc` を以下の内容で作成する：

```ini
[run]
omit =
    factories/*
    seed.py
    admin/*
    docs/*
    utils/ai_*.py

[report]
fail_under = 90
```

**Step 2: `pytest.ini` の `--cov-fail-under` を変更**

```
変更前: addopts = -v --tb=short --cov=. --cov-fail-under=40
変更後: addopts = -v --tb=short --cov=. --cov-fail-under=90
```

**Step 3: 現在のカバレッジを確認（除外後の数値を把握）**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
conda run -n flask2_env pytest tests/ --co -q 2>&1 | tail -5
conda run -n flask2_env pytest tests/ -v --tb=no -q 2>&1 | tail -20
```

期待: テスト 26 件が収集される。カバレッジは 70% 台になる（除外後）。

**Step 4: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/.coveragerc Memo/pytest.ini
git commit -m "chore: add .coveragerc and update fail-under to 90"
```

---

### Task 2: `tests/conftest.py` に `fixed_page` fixture を追加

**Files:**
- Modify: `tests/conftest.py`

**Step 1: conftest.py に `fixed_page` fixture を追加**

`tests/conftest.py` の末尾に追記する：

```python
@pytest.fixture
def fixed_page(app):
    """テスト用固定ページを作成して返す。"""
    from models import FixedPage
    with app.app_context():
        page = FixedPage(key='policy', title='プライバシーポリシー', visible=True)
        _db.session.add(page)
        _db.session.commit()
        _db.session.refresh(page)
        return page
```

**Step 2: 構文確認**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
conda run -n flask2_env python -c "from tests.conftest import *; print('OK')"
```

期待: `OK`

---

### Task 3: `tests/test_fixed.py` を新規作成

**Files:**
- Create: `tests/test_fixed.py`

**Step 1: ファイルを作成**

```python
class TestFixedPages:
    def test_existing_fixed_page_returns_200(self, client, fixed_page):
        """存在する固定ページキーで 200 を返す。"""
        res = client.get('/fixed/policy')
        assert res.status_code == 200

    def test_nonexistent_fixed_page_returns_404(self, client):
        """DB に存在しないキーで 404 を返す。"""
        res = client.get('/fixed/nonexistent_key_xyz')
        assert res.status_code == 404
```

**Step 2: テスト実行**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
conda run -n flask2_env pytest tests/test_fixed.py -v --no-cov
```

期待:
```
tests/test_fixed.py::TestFixedPages::test_existing_fixed_page_returns_200 PASSED
tests/test_fixed.py::TestFixedPages::test_nonexistent_fixed_page_returns_404 PASSED
```

**Step 3: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/tests/conftest.py Memo/tests/test_fixed.py
git commit -m "test: add fixed_page fixture and test_fixed.py"
```

---

### Task 4: `tests/test_favorite.py` を新規作成

**Files:**
- Create: `tests/test_favorite.py`

**Step 1: ファイルを作成**

```python
import json
from models import db, User, Memo, Favorite


class TestFavorite:
    def _create_memo(self, app, user_id):
        """テスト用メモを作成して ID を返すヘルパー。"""
        with app.app_context():
            user = db.session.get(User, user_id)
            memo = Memo(title='いいねテスト', content='本文', user_id=user.id)
            db.session.add(memo)
            db.session.commit()
            return memo.id

    def test_add_favorite_returns_json(self, app, auth_client, test_user):
        """AJAX ヘッダー付きでいいね追加すると JSON が返る。"""
        memo_id = self._create_memo(app, test_user.id)
        res = auth_client.post(
            f'/favorite/add/{memo_id}',
            headers={'X-Requested-With': 'XMLHttpRequest'},
        )
        assert res.status_code == 200
        data = json.loads(res.data)
        assert data['liked'] is True
        assert data['like_count'] == 1

    def test_remove_favorite_returns_json(self, app, auth_client, test_user):
        """AJAX ヘッダー付きでいいね削除すると JSON が返る。"""
        memo_id = self._create_memo(app, test_user.id)
        # まず追加
        auth_client.post(
            f'/favorite/add/{memo_id}',
            headers={'X-Requested-With': 'XMLHttpRequest'},
        )
        # 削除
        res = auth_client.post(
            f'/favorite/remove/{memo_id}',
            headers={'X-Requested-With': 'XMLHttpRequest'},
        )
        assert res.status_code == 200
        data = json.loads(res.data)
        assert data['liked'] is False
        assert data['like_count'] == 0

    def test_add_favorite_without_ajax_redirects(self, app, auth_client, test_user):
        """AJAX ヘッダーなしでいいね追加するとリダイレクトされる。"""
        memo_id = self._create_memo(app, test_user.id)
        res = auth_client.post(f'/favorite/add/{memo_id}')
        assert res.status_code == 302

    def test_remove_favorite_without_ajax_redirects(self, app, auth_client, test_user):
        """AJAX ヘッダーなしでいいね削除するとリダイレクトされる。"""
        memo_id = self._create_memo(app, test_user.id)
        res = auth_client.post(f'/favorite/remove/{memo_id}')
        assert res.status_code == 302

    def test_add_favorite_requires_login(self, app, client, test_user):
        """未ログインでいいね追加するとリダイレクトされる。"""
        memo_id = self._create_memo(app, test_user.id)
        res = client.post(f'/favorite/add/{memo_id}')
        assert res.status_code == 302
```

**Step 2: テスト実行**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
conda run -n flask2_env pytest tests/test_favorite.py -v --no-cov
```

期待: 5件すべて PASSED

**Step 3: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/tests/test_favorite.py
git commit -m "test: add test_favorite.py for add/remove favorite routes"
```

---

### Task 5: `tests/test_auth.py` を拡充

**Files:**
- Modify: `tests/test_auth.py`

**Step 1: 以下のクラス・テストを末尾に追加**

```python
class TestRegister:
    def test_register_success_redirects(self, client):
        """正しい入力でユーザー登録すると /auth/ にリダイレクトされる。"""
        res = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Password1!',
            'confirm_password': 'Password1!',
            'gender': '男性',
            'age_range': '20〜30',
            'address': '東京都',
            'occupation': '学生',
        }, follow_redirects=False)
        assert res.status_code == 302

    def test_register_duplicate_email_returns_200(self, client, test_user):
        """登録済みメールで新規登録すると 200 でエラーが表示される。"""
        res = client.post('/auth/register', data={
            'username': 'anotheruser',
            'email': 'test@example.com',   # test_user と同じメール
            'password': 'Password1!',
            'confirm_password': 'Password1!',
            'gender': '男性',
            'age_range': '20〜30',
            'address': '東京都',
            'occupation': '学生',
        })
        assert res.status_code == 200


class TestLoginEdgeCases:
    def test_authenticated_user_redirected_from_login(self, auth_client):
        """ログイン済みユーザーがログインページにアクセスするとマイページに飛ぶ。"""
        res = auth_client.get('/auth/')
        assert res.status_code == 302

    def test_banned_user_cannot_login(self, app, client):
        """一時停止ユーザーはログインできない。"""
        from models import db, User
        with app.app_context():
            user = User(username='banneduser', email='banned@example.com')
            user.set_password('Password1!')
            user.is_banned = True
            db.session.add(user)
            db.session.commit()

        res = client.post('/auth/', data={
            'email': 'banned@example.com',
            'password': 'Password1!',
        })
        assert res.status_code == 200
        assert 'ユーザーアカウントが無効化されました'.encode() in res.data

    def test_oauth_user_cannot_login_with_password(self, app, client):
        """OAuth専用ユーザーは通常ログインできない。"""
        from models import db, User
        with app.app_context():
            user = User(
                username='oauthuser',
                email='oauth@example.com',
                oauth_provider='google',
                oauth_sub='google-sub-123',
            )
            db.session.add(user)
            db.session.commit()

        res = client.post('/auth/', data={
            'email': 'oauth@example.com',
            'password': 'anypassword',
        })
        assert res.status_code == 200
        assert 'Googleログイン専用'.encode() in res.data


class TestDeleteUser:
    def test_delete_own_account(self, app, auth_client, test_user):
        """ログイン済みで POST /auth/delete すると 302 になる。"""
        res = auth_client.post('/auth/delete', follow_redirects=False)
        assert res.status_code == 302

        from models import db, User
        with app.app_context():
            user = db.session.get(User, test_user.id)
            assert user is None


class TestEditUser:
    def test_edit_get_returns_200(self, auth_client):
        """GET /auth/edit が 200 を返す。"""
        res = auth_client.get('/auth/edit')
        assert res.status_code == 200

    def test_edit_post_updates_username(self, app, auth_client, test_user):
        """POST /auth/edit でユーザー名を更新できる。"""
        res = auth_client.post('/auth/edit', data={
            'username': 'updatedname',
            'change_password': False,
        }, follow_redirects=False)
        assert res.status_code == 302

        from models import db, User
        with app.app_context():
            user = db.session.get(User, test_user.id)
            assert user.username == 'updatedname'


class TestCheckUseridAPI:
    def test_short_value_returns_length_error(self, client):
        """2文字以下の値に length_error が返る。"""
        import json
        res = client.get('/auth/api/check_userid?value=ab')
        data = json.loads(res.data)
        assert data.get('length_error') is True

    def test_invalid_char_returns_invalid_char(self, client):
        """使用不可文字に invalid_char が返る。"""
        import json
        res = client.get('/auth/api/check_userid?value=inv@lid!')
        data = json.loads(res.data)
        assert data.get('invalid_char') is True

    def test_available_username_returns_available_true(self, client):
        """存在しないユーザー名は available=True になる。"""
        import json
        res = client.get('/auth/api/check_userid?value=newuniqueuser')
        data = json.loads(res.data)
        assert data.get('available') is True

    def test_existing_username_returns_available_false(self, client, test_user):
        """既存ユーザー名は available=False になる。"""
        import json
        res = client.get(f'/auth/api/check_userid?value={test_user.username}')
        data = json.loads(res.data)
        assert data.get('available') is False
```

**Step 2: テスト実行**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
conda run -n flask2_env pytest tests/test_auth.py -v --no-cov
```

期待: 追加したすべてのテストが PASSED

**Step 3: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/tests/test_auth.py
git commit -m "test: expand test_auth with register, banned, oauth, delete, edit, check_userid"
```

---

### Task 6: `tests/test_memo.py` を拡充

**Files:**
- Modify: `tests/test_memo.py`

**Step 1: 以下のテストを末尾に追加**

```python
class TestMemoIndex:
    def test_index_with_search_query(self, app, auth_client, test_user):
        """検索クエリ付きでマイページ一覧が 200 を返す。"""
        with app.app_context():
            user = db.session.get(User, test_user.id)
            memo = Memo(title='検索タイトル', content='検索本文', user_id=user.id)
            db.session.add(memo)
            db.session.commit()

        res = auth_client.get('/memo/?q=検索')
        assert res.status_code == 200

    def test_index_with_category_filter(self, app, auth_client, test_user, test_category):
        """カテゴリーフィルター付きで 200 を返す。"""
        res = auth_client.get(f'/memo/?category_id={test_category.id}')
        assert res.status_code == 200

    def test_index_sort_by_likes_asc(self, auth_client):
        """いいね昇順ソートで 200 を返す。"""
        res = auth_client.get('/memo/?likes=asc')
        assert res.status_code == 200

    def test_index_sort_by_likes_desc(self, auth_client):
        """いいね降順ソートで 200 を返す。"""
        res = auth_client.get('/memo/?likes=desc')
        assert res.status_code == 200


class TestMemoCreate:
    def test_create_get_returns_200(self, auth_client):
        """GET /memo/create が 200 を返す。"""
        res = auth_client.get('/memo/create')
        assert res.status_code == 200

    def test_create_get_with_init_params(self, auth_client):
        """クエリパラメーター付き GET /memo/create が 200 を返す。"""
        res = auth_client.get('/memo/create?title=テスト&body=本文')
        assert res.status_code == 200

    def test_create_with_too_many_categories_returns_400(self, app, auth_client, test_user):
        """カテゴリーを4つ以上選択すると 400 を返す。"""
        from models import Category
        with app.app_context():
            cats = [Category(name=f'Cat{i}', color=f'#00000{i}') for i in range(4)]
            for c in cats:
                db.session.add(c)
            db.session.commit()
            cat_ids = [str(c.id) for c in cats]

        res = auth_client.post('/memo/create', data={
            'title': 'タイトル',
            'content': '本文',
            'categories': cat_ids,
        })
        assert res.status_code == 400


class TestMemoUpdate:
    def test_update_get_returns_200(self, app, auth_client, test_user):
        """GET /memo/update/<id> が 200 を返す。"""
        with app.app_context():
            user = db.session.get(User, test_user.id)
            memo = Memo(title='更新前タイトル', content='更新前本文', user_id=user.id)
            db.session.add(memo)
            db.session.commit()
            memo_id = memo.id

        res = auth_client.get(f'/memo/update/{memo_id}')
        assert res.status_code == 200

    def test_update_with_too_many_categories_returns_400(self, app, auth_client, test_user):
        """更新時にカテゴリーを4つ以上選択すると 400 を返す。"""
        from models import Category
        with app.app_context():
            user = db.session.get(User, test_user.id)
            memo = Memo(title='カテゴリー超過テスト', content='本文', user_id=user.id)
            db.session.add(memo)
            cats = [Category(name=f'UCat{i}', color=f'#11000{i}') for i in range(4)]
            for c in cats:
                db.session.add(c)
            db.session.commit()
            memo_id = memo.id
            cat_ids = [str(c.id) for c in cats]

        res = auth_client.post(f'/memo/update/{memo_id}', data={
            'title': '更新タイトル',
            'content': '更新本文',
            'categories': cat_ids,
        })
        assert res.status_code == 400
```

**Step 2: テスト実行**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
conda run -n flask2_env pytest tests/test_memo.py -v --no-cov
```

期待: 追加したすべてのテストが PASSED

**Step 3: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/tests/test_memo.py
git commit -m "test: expand test_memo with index filters, create/update edge cases"
```

---

### Task 7: `tests/test_public.py` を拡充

**Files:**
- Modify: `tests/test_public.py`

**Step 1: 以下のテストを末尾に追加**

```python
class TestPublicLoggedIn:
    def test_top_page_logged_in_shows_favorites(self, app, auth_client, test_user):
        """ログイン済みでトップページにアクセスすると 200 を返す（favorite_memo_ids が設定される）。"""
        with app.app_context():
            user = db.session.get(User, test_user.id)
            memo = Memo(title='公開記事', content='本文', user_id=user.id)
            db.session.add(memo)
            db.session.commit()

        res = auth_client.get('/')
        assert res.status_code == 200

    def test_top_page_with_memos_shows_random(self, app, client, test_user):
        """メモが存在するときランダムピックが機能し 200 を返す。"""
        with app.app_context():
            user = db.session.get(User, test_user.id)
            for i in range(3):
                memo = Memo(title=f'記事{i}', content=f'本文{i}', user_id=user.id)
                db.session.add(memo)
            db.session.commit()

        res = client.get('/')
        assert res.status_code == 200

    def test_top_page_recommendation_for_logged_in_with_category(
        self, app, auth_client, test_user, other_user, test_category
    ):
        """ログイン済みかつカテゴリー一致メモがある場合にレコメンドが機能し 200 を返す。"""
        from models import Category
        with app.app_context():
            my_user = db.session.get(User, test_user.id)
            other = db.session.get(User, other_user.id)
            cat = db.session.get(Category, test_category.id)

            # 自分のメモにカテゴリーを付与
            my_memo = Memo(title='自分の記事', content='本文', user_id=my_user.id)
            my_memo.categories = [cat]
            db.session.add(my_memo)

            # 他人のメモに同じカテゴリーを付与
            other_memo = Memo(title='他人の記事', content='本文', user_id=other.id)
            other_memo.categories = [cat]
            db.session.add(other_memo)
            db.session.commit()

        res = auth_client.get('/')
        assert res.status_code == 200
```

**Step 2: テスト実行**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
conda run -n flask2_env pytest tests/test_public.py -v --no-cov
```

期待: 追加したすべてのテストが PASSED

**Step 3: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/tests/test_public.py
git commit -m "test: expand test_public with logged-in and recommendation tests"
```

---

### Task 8: `tests/test_forms.py` を新規作成

**Files:**
- Create: `tests/test_forms.py`

**Step 1: ファイルを作成**

forms.py のバリデーション関数を HTTP 経由で検証するテスト。

```python
class TestPasswordStrength:
    def test_register_with_weak_password_returns_200(self, client):
        """記号なし弱パスワードでの登録は 200 でエラーを返す。"""
        res = client.post('/auth/register', data={
            'username': 'weakpwuser',
            'email': 'weak@example.com',
            'password': 'password123',       # 記号なし → 強度不足
            'confirm_password': 'password123',
            'gender': '男性',
            'age_range': '20〜30',
            'address': '東京都',
            'occupation': '学生',
        })
        assert res.status_code == 200

    def test_register_with_duplicate_username_returns_200(self, client, test_user):
        """既存ユーザー名での登録は 200 でエラーを返す。"""
        res = client.post('/auth/register', data={
            'username': test_user.username,  # 既存ユーザー名
            'email': 'another@example.com',
            'password': 'Password1!',
            'confirm_password': 'Password1!',
            'gender': '男性',
            'age_range': '20〜30',
            'address': '東京都',
            'occupation': '学生',
        })
        assert res.status_code == 200


class TestMemoFormValidation:
    def test_create_memo_with_duplicate_title_returns_200(self, app, auth_client, test_user):
        """同名タイトルで2回投稿すると 200 でエラーが表示される。"""
        from models import db, User, Memo
        with app.app_context():
            user = db.session.get(User, test_user.id)
            memo = Memo(title='重複タイトル', content='本文', user_id=user.id)
            db.session.add(memo)
            db.session.commit()

        res = auth_client.post('/memo/create', data={
            'title': '重複タイトル',
            'content': '新しい本文',
        })
        assert res.status_code == 200


class TestEditUserFormValidation:
    def test_edit_with_change_password_but_empty_password_returns_200(self, auth_client):
        """パスワード変更チェックONで空パスワードを送ると 200 でエラーが表示される。"""
        res = auth_client.post('/auth/edit', data={
            'username': 'testuser',
            'change_password': 'y',   # True として扱われる
            'password': '',            # 空
            'confirm_password': '',
        })
        assert res.status_code == 200

    def test_edit_with_weak_password_returns_200(self, auth_client):
        """パスワード変更チェックONで弱パスワードを送ると 200 でエラーが表示される。"""
        res = auth_client.post('/auth/edit', data={
            'username': 'testuser',
            'change_password': 'y',
            'password': 'weakpassword',    # 記号なし
            'confirm_password': 'weakpassword',
        })
        assert res.status_code == 200
```

**Step 2: テスト実行**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
conda run -n flask2_env pytest tests/test_forms.py -v --no-cov
```

期待: すべて PASSED

**Step 3: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/tests/test_forms.py
git commit -m "test: add test_forms.py for password strength and form validation"
```

---

### Task 9: `tests/test_upload.py` を新規作成

**Files:**
- Create: `tests/test_upload.py`

**Step 1: ファイルを作成**

```python
from io import BytesIO
from unittest.mock import patch
from werkzeug.datastructures import FileStorage
from utils.upload import save_upload


class TestSaveUpload:
    def test_none_file_returns_none(self, app):
        """None を渡すと None が返る。"""
        with app.app_context():
            result = save_upload(None, 'memo')
        assert result is None

    def test_empty_filename_returns_none(self, app):
        """filename が空の FileStorage を渡すと None が返る。"""
        with app.app_context():
            f = FileStorage(filename='')
            result = save_upload(f, 'memo')
        assert result is None

    def test_valid_file_returns_filename_with_extension(self, app):
        """有効なファイルを渡すと拡張子付きファイル名が返る。"""
        with app.app_context():
            data = BytesIO(b'fake image data')
            f = FileStorage(stream=data, filename='photo.jpg', content_type='image/jpeg')
            with patch('utils.upload.os.makedirs'), patch.object(f, 'save'):
                result = save_upload(f, 'memo')
        assert result is not None
        assert result.endswith('.jpg')

    def test_returned_filename_is_unique(self, app):
        """2回呼び出すとそれぞれ異なるファイル名が返る（UUID使用）。"""
        with app.app_context():
            data1 = BytesIO(b'img1')
            data2 = BytesIO(b'img2')
            f1 = FileStorage(stream=data1, filename='a.png', content_type='image/png')
            f2 = FileStorage(stream=data2, filename='b.png', content_type='image/png')
            with patch('utils.upload.os.makedirs'):
                with patch.object(f1, 'save'), patch.object(f2, 'save'):
                    name1 = save_upload(f1, 'user')
                    name2 = save_upload(f2, 'user')
        assert name1 != name2
```

**Step 2: テスト実行**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
conda run -n flask2_env pytest tests/test_upload.py -v --no-cov
```

期待: 4件すべて PASSED

**Step 3: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/tests/test_upload.py
git commit -m "test: add test_upload.py for save_upload edge cases"
```

---

### Task 10: `tests/test_logger.py` を拡充（SMTP ハンドラーテスト）

**Files:**
- Modify: `tests/test_logger.py`

**Step 1: 以下のテストを末尾に追加**

```python
def test_smtp_handler_added_when_mail_credentials_present():
    """本番設定（debug=False, testing=False）かつメール資格情報ありで SMTPHandler が登録される。"""
    from logging.handlers import SMTPHandler
    config = {
        'TESTING': False,
        'DEBUG': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'prod-test-secret-key',
        'MAIL_SUPPRESS_SEND': True,
        'MAIL_USERNAME': 'admin@example.com',
        'MAIL_PASSWORD': 'smtp_pass',
        'STRIPE_SECRET_KEY': '',
        'GOOGLE_CLIENT_ID': 'dummy',
        'GOOGLE_CLIENT_SECRET': 'dummy',
    }
    app = create_app(config)
    smtp_handlers = [h for h in app.logger.handlers if isinstance(h, SMTPHandler)]
    assert len(smtp_handlers) >= 1, "本番設定で SMTPHandler が登録されていない"
```

**Step 2: テスト実行**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
conda run -n flask2_env pytest tests/test_logger.py -v --no-cov
```

期待: 4件すべて PASSED（既存3件 + 新規1件）

**Step 3: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/tests/test_logger.py
git commit -m "test: add SMTP handler test for production config"
```

---

### Task 11: 全テスト実行・カバレッジ確認・最終コミット

**Step 1: 全テスト実行**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
conda run -n flask2_env pytest tests/ -v --tb=short 2>&1 | tail -40
```

期待:
- すべてのテストが PASSED
- `Required test coverage of 90% reached.` が表示される
- `TOTAL ≥ 90%`

**Step 2: カバレッジ詳細確認**

```bash
conda run -n flask2_env pytest tests/ --cov=. --cov-report=term-missing --tb=no -q 2>&1 | grep -E "(TOTAL|auth|memo|public|favorite|fixed|forms|upload|logger)"
```

期待: 各対象ファイルが 90% 以上

**Step 3: 残りファイルをコミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/README.md Memo/static/docs/operation_flow.md Memo/docs/plans/
git commit -m "docs: update README implementation list and add coverage plan docs"
```

---

## 完了の定義

- [ ] `.coveragerc` が存在し factories/seed/admin/docs/utils-AI が除外されている
- [ ] `pytest.ini` の `--cov-fail-under` が 90 になっている
- [ ] `conda run -n flask2_env pytest tests/ -v` が全テスト PASS
- [ ] カバレッジレポートで **TOTAL ≥ 90%** が表示される
- [ ] 以下のファイルがそれぞれ 90% 以上：
  - `auth/views.py`, `favorite/views.py`, `fixed/views.py`
  - `forms.py`, `memo/views.py`, `public/views.py`
  - `utils/logger.py`, `utils/upload.py`
