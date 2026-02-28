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
