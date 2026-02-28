from models import db, Memo, User


class TestMemoCRUD:
    def test_create_memo_saves_to_db(self, app, auth_client, test_user):
        """投稿作成フォームの POST で DB に1件追加される。"""
        with app.app_context():
            before = Memo.query.count()

        res = auth_client.post('/memo/create', data={
            'title': 'テスト投稿',
            'content': 'テスト投稿の本文です。',
        }, follow_redirects=False)

        assert res.status_code == 302

        with app.app_context():
            after = Memo.query.count()
            assert after == before + 1

    def test_update_own_memo(self, app, auth_client, test_user):
        """自分の投稿を編集すると 302 リダイレクトになる。"""
        with app.app_context():
            user = db.session.get(User, test_user.id)
            memo = Memo(title='編集前', content='編集前本文', user_id=user.id)
            db.session.add(memo)
            db.session.commit()
            memo_id = memo.id

        res = auth_client.post(f'/memo/update/{memo_id}', data={
            'title': '編集後',
            'content': '編集後本文',
        }, follow_redirects=False)
        assert res.status_code == 302

        with app.app_context():
            updated = db.session.get(Memo, memo_id)
            assert updated.title == '編集後'

    def test_update_other_memo_returns_404(self, app, client, test_user, other_user):
        """他人の投稿を編集しようとすると 404 を返す（filter_by user_id で first_or_404）。"""
        with app.app_context():
            other = db.session.get(User, other_user.id)
            memo = Memo(title='他人の投稿', content='他人の本文', user_id=other.id)
            db.session.add(memo)
            db.session.commit()
            memo_id = memo.id

        client.post('/auth/', data={
            'email': 'test@example.com',
            'password': 'Password1!',
        })

        res = client.post(f'/memo/update/{memo_id}', data={
            'title': '不正編集',
            'content': '不正本文',
        })
        assert res.status_code == 404

    def test_delete_memo_removes_from_db(self, app, auth_client, test_user):
        """投稿削除後に DB の件数が1減る。"""
        with app.app_context():
            user = db.session.get(User, test_user.id)
            memo = Memo(title='削除対象', content='削除対象本文', user_id=user.id)
            db.session.add(memo)
            db.session.commit()
            memo_id = memo.id
            before = Memo.query.count()

        # delete ルートは GET メソッド
        auth_client.get(f'/memo/delete/{memo_id}')

        with app.app_context():
            after = Memo.query.count()
            assert after == before - 1
