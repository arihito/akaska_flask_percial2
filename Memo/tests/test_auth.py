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
        """存在しないメールアドレスでも 200 を返す（セキュリティ）。"""
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
        """未ログインで /memo/ にアクセスすると /auth/ へリダイレクトされる。"""
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
