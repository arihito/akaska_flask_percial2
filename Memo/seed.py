import os
import random
from datetime import datetime, timedelta, timezone

# seed用にFlaskアプリを1つ生成しconfigを読み込みdb/login_manager/Blueprintを初期化する
from app import app, db
from models import User, Memo, Favorite, Category, FixedPage
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

# 固定ページ初期データ（STATIC_PAGES から移行）
FIXED_PAGES_SEED = [
    # (key, title, order, image, nav_type, summary)
    ('refactor',   '環境構築',                  0,  'refactor.jpg',   'global', 'VSCode設定・conda仮想環境・Flaskデバッガー・bashエイリアスなど、快適な開発環境を整えるための一連の手順を解説します。'),
    ('crud',       'CRUD',                       1,  'crud.jpg',       'global', 'FlaskとSQLAlchemyを使った基本的なCRUD実装。Blueprint設計・フォームバリデーション・一覧・詳細・作成・更新・削除の各処理を解説します。'),
    ('paging',     'ページング',                 2,  'paging.jpg',     'global', 'Flask-SQLAlchemyのpaginateを活用したページネーション実装。URLパラメータによるページ管理と表示件数のカスタマイズ方法を解説します。'),
    ('upload',     'ファイルアップロード',        3,  'upload.jpg',     'global', 'Flaskでの画像ファイルアップロード実装。拡張子・サイズバリデーション・保存先管理・セキュリティ対策を含む実践的な手順を解説します。'),
    ('drop',       'ドラッグ&ドロップ',          4,  'drop.jpg',       'global', 'DropzoneやSortable.jsを使ったドラッグ&ドロップUI実装。ファイルD&Dアップロードとリスト並び替えUIの構築手順を解説します。'),
    ('htmx',       '非同期',                     5,  'htmx.jpg',       'global', 'HTMXを使ったFlaskアプリの非同期UI構築。JavaScriptを最小限に抑えたサーバーサイドレンダリングとAJAX処理の実装方法を解説します。'),
    ('oauth',      'Googleログイン',              6,  'oauth.jpg',      'global', 'AuthlibによるGoogle OAuth2.0の実装手順。コールバック処理・セッション管理・既存ユーザーとの紐付けフローを丁寧に解説します。'),
    ('jwt',        'JWT認証',                    7,  'jwt.jpg',        'global', 'PyJWTを用いたトークンベース認証の実装。アクセストークンの発行・検証・リフレッシュトークンの設計と実践的な運用方法を解説します。'),
    ('twofactor',  '二段階認証',                 8,  'twofactor.jpg',  'global', 'TOTPベースの二段階認証実装。QRコード生成・認証アプリ（Google Authenticator等）との連携・バックアップコードの設計を解説します。'),
    ('stripe',     'カード決済',                 9,  'stripe.jpg',     'global', 'Stripe Checkoutを使ったカード決済フロー実装。セッション作成・Webhook連携・決済後の自動処理まで一連の実装手順を解説します。'),
    ('i18n',       '多言語設定',                10,  'i18n.jpg',       'global', 'Flask-Babelを使った多言語対応（i18n）実装。翻訳ファイル管理・言語切り替えUIの構築・日本語ローカライズ設定を解説します。'),
    ('deploy',     'デプロイ',                  11,  'deploy.jpg',     'global', 'GunicornとNginxを使ったFlaskアプリの本番デプロイ手順。環境変数管理・SSL設定・GitHub Actionsによる自動化を解説します。'),
    ('help',       'ヘルプ',                    12,  'help.jpg',       'footer', 'アプリの基本的な使い方ガイド。投稿・検索・お気に入り・ユーザー設定など各機能の操作方法をわかりやすく解説します。'),
    ('terms',      '利用規約',                  13,  'terms.jpg',      'footer', '本サービスの利用規約。サービスの目的・禁止事項・アカウント管理・免責事項など利用にあたっての規定を記載しています。'),
    ('policy',     'プライバシーポリシー',       14,  'policy.jpg',     'footer', '個人情報の収集・利用・管理方針。Googleログイン時のデータ取り扱いを含む個人情報保護方針を記載しています。'),
    ('legal',      '特定商取引法に基づく表記',   15,  'legal.jpg',      'footer', '特定商取引法に基づく事業者情報。販売者名・連絡先・サービス提供条件など法定記載事項を掲載しています。'),
    ('disclaimer', '免責事項',                  16,  'disclaimer.jpg', 'footer', '本サービスの情報に関する免責事項。掲載情報の正確性・損害責任の範囲・外部リンクに関する免責を記載しています。'),
    ('copyright',  '著作権・引用について',       17,  'copyright.jpg',  'footer', '本サイトのコンテンツの著作権に関する方針。記事の引用ルール・転載条件・著作物の適切な取り扱い方法を記載しています。'),
]


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

        print("固定ページシード...")
        if FixedPage.query.count() == 0:
            for key, title, order, image, nav_type, summary in FIXED_PAGES_SEED:
                db.session.add(FixedPage(key=key, title=title, order=order, image=image, visible=True, nav_type=nav_type, summary=summary))
            db.session.commit()
            print(f"固定ページ {len(FIXED_PAGES_SEED)} 件を登録しました")
        else:
            print("固定ページはすでに登録済みです（スキップ）")

        print("管理者ユーザー作成...")
        admin_user = User(
            username="管理者",
            email=os.getenv('MAIL_USERNAME', 'admin@example.com'),
            is_admin=True,
            is_paid=True,
            admin_points=24,
            subscription_expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
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
