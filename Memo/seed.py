import os
import random
from datetime import datetime, timedelta

# seed用にFlaskアプリを1つ生成しconfigを読み込みdb/login_manager/Blueprintを初期化する
from app import app, db
from models import User, Memo, Favorite, Category
from factories.user_factory import UserFactory
from factories.body_factory import BodyFactory
import pytz

app.app_context().push()

TZ = pytz.timezone("Asia/Tokyo")

# ------------------------------
# Factory群
# ------------------------------

MEMO_TITLE_FACTORY = [
    "FlaskにおけるBlueprint分割設計の基本",
    "Flask-Loginで認証機能を実装する",
    "Flask-SQLAlchemyのセッション管理",
    "Flaskでのフォームバリデーション入門",
    "FlaskとHTMXによる非同期UI構築",
    "Flask-Migrateで安全にDB更新する",
    "Flaskアプリの設定管理ベストプラクティス",
    "Flaskでのファイルアップロード実装",
    "Flaskにおける循環import対策",
    "FlaskでREST APIを構築する方法",
    "FlaskとJinja2テンプレート設計",
    "Flaskでページネーションを実装する",
    "Flaskにおけるエラーハンドリング設計",
    "FlaskとCSRF対策の実装方法",
    "Flaskでお気に入り機能を作る",
    "Flaskでユーザー権限制御を行う",
    "Flaskで全文検索を実装する",
    "Flaskのデプロイ構成と注意点",
    "Flaskと環境変数による秘密情報管理",
    "Flaskで管理画面を構築する",
    "SQLAlchemyによるDBマイグレーション管理",
    "Flask-WTFでバリデーション付きフォーム作成",
    "環境変数(python-dotenv)の安全な運用",
    "Flask-RESTfulによるAPIサーバー構築",
    "Pytestを用いたFlaskアプリのテスト手法",
    "Application Factoryパターンの導入メリット",
    "Redisを活用したセッション管理の最適化",
    "Flask-Cachingでレスポンスを高速化する",
    "Jinja2テンプレートの継承とコンポーネント化",
    "GunicornとNginxでの本番デプロイ構成",
    "Celeryを使った非同期タスク処理の実装",
    "Flask-Marshmallowでのシリアライズ処理",
    "カスタムエラーハンドリング(404/500)の設計",
    "トークンベース認証(PyJWT)の導入手順",
    "FlaskアプリのDocker化とマルチステージビルド",
    "Loggingモジュールによる実行ログの出力設定",
    "CORS(Flask-CORS)設定の注意点と対策",
    "Swagger(Flasgger)によるAPIドキュメント自動生成",
]

CATEGORY_SEED = [
    ("Python", "#391A63"),
    ("Flask", "#000000"),
    ("SQL", "#52190F"),
    ("CSS", "#111E50"),
    ("API", "#3A340A"),
    ("Auth", "#342647"),
    ("Package", "#0B3F1B"),
]

IMAGE_POOL = [f"{i:02}.jpg" for i in range(1, 22)]


# --- ランダム日付生成関数 ---
def random_date(start, end):
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86399)
    return start + timedelta(days=random_days, seconds=random_seconds)


start_date = datetime(2025, 1, 1)
end_date = datetime.now()
user_start_date = datetime.now() - timedelta(days=365)


# ------------------------------
# Seed処理
# ------------------------------
def seed_data():
    with app.app_context():
        print("データ初期化中...")
        # 削除順は必ず子→親
        Favorite.query.delete()
        Memo.query.delete()
        User.query.delete()
        db.session.commit()

        print("管理者ユーザー作成...")
        admin_user = User(
            username="管理者",
            email=os.getenv('MAIL_USERNAME', 'admin@example.com'),
            is_admin=True,
            is_paid=True,
            created_at=random_date(user_start_date, end_date),
        )
        admin_user.set_password("admin1234%")
        admin_user.set_admin_password("admin1234%")
        db.session.add(admin_user)
        db.session.commit()

        print("サブユーザー作成...")
        subuser = User(
            username="田中太郎",
            email=os.getenv('MAIL_SUBUSER', 'subuser@example.com'),
            created_at=random_date(user_start_date, end_date),
        )
        subuser.set_password("pass1234%")
        db.session.add(subuser)
        db.session.commit()

        print("ユーザー作成...")
        users = UserFactory.create_batch(15)
        for u in users:
            u.created_at = random_date(user_start_date, end_date)
        db.session.commit()
        users = [admin_user, subuser] + users

        print("メモ作成...")
        # BodyFactoryから全記事本文を取得
        all_bodies = BodyFactory.get_all_bodies()
        print(f"読み込んだMarkdown記事数: {len(all_bodies)}件")

        # --- Category 作成 ---
        categories = []
        for name, color in CATEGORY_SEED:
            category = Category.query.filter_by(name=name).first()
            if not category:
                category = Category(name=name, color=color)
                db.session.add(category)
            categories.append(category)

        memos = []
        for idx, user in enumerate(users):
            # 管理者(idx=0)と田中太郎(idx=1)は15件、それ以外は3~6件
            if idx in (0, 1):
                memos_per_user = 15
            else:
                memos_per_user = random.randint(3, 6)

            for i in range(memos_per_user):
                # タイトルはMEMO_TITLE_FACTORYからランダム選択
                title = random.choice(MEMO_TITLE_FACTORY)

                # 本文はBodyFactoryから取得（インデックスでループ）
                body_index = (len(memos) + i) % len(all_bodies)
                body_content = all_bodies[body_index]

                memo = Memo(
                    title=title,
                    content=body_content,  # ← Markdown形式の本文
                    user_id=user.id,
                    image_filename=random.choice(IMAGE_POOL),
                    created_at=random_date(start_date, end_date),
                    view_count=random.randint(0, 1500),  # 0〜1500 で大きくばらけさせる
                )
                db.session.add(memo)
                memos.append(memo)

                # --- Memo にタグ付与 ---
                memos = Memo.query.all()
                for memo in memos:
                    memo.categories.clear()
                    memo.categories.extend(
                        random.sample(categories, k=random.randint(1, 3))
                    )

        print(f"メモ作成完了: {len(memos)}件")

        print("お気に入り作成...")
        for memo in memos:
            like_count = random.randint(0, len(users))  # 0〜全ユーザー数 で大きくばらけさせる
            liked_users = random.sample(users, min(like_count, len(users)))

            for user in liked_users:
                fav = Favorite(
                    user_id=user.id,
                    memo_id=memo.id,
                    rank=random.randint(1, 5),
                    created_at=datetime.now(TZ) - timedelta(days=random.randint(0, 30)),
                )
                db.session.add(fav)

        db.session.commit()

        print("ダミーデータ投入完了！")


if __name__ == "__main__":
    seed_data()
