import random
from datetime import datetime, timedelta
# seed用にFlaskアプリを1つ生成しconfigを読み込みdb/login_manager/Blueprintを初期化する
from app import app, db
from models import User, Memo, Favorite
from datetime import datetime, timedelta
# from factory import UserFactory, MemoFactory, FavoriteFactory 
import pytz

app.app_context().push()

TZ = pytz.timezone("Asia/Tokyo")

# ------------------------------
# Factory群
# ------------------------------

USER_NAMES = [
    "田中太郎",
    "鈴木花子",
    "佐藤健",
    "山田愛",
    "伊藤亮"
]

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
    "Flaskで管理画面を構築する"
]

MEMO_CONTENT_FACTORY = [
    "中規模以上のFlaskアプリではBlueprintによる分割設計が必須です。本記事ではディレクトリ構成、循環import回避、register_blueprintの正しい書き方を具体例つきで解説します。",
    "Flask-Loginを使ったログイン・ログアウト・ログイン必須制御の実装方法を、Userモデル設計から@login_requiredの使い方まで段階的に説明します。",
    "Flask-SQLAlchemyのdb.session管理はバグの温床になりがちです。commitとrollbackのタイミング、例外発生時の安全な処理方法を整理します。",
    "Flask-WTFを用いたフォームバリデーションの基本を解説します。必須入力、文字数制限、カスタムバリデータの作り方まで網羅します。",
    "HTMXを使うことでJavaScriptを書かずに非同期通信が可能です。Flaskと組み合わせた部分更新UIの最小実装例を紹介します。",
    "Flask-Migrateを用いたマイグレーション管理の手順を解説します。既存データを保持したまま安全にスキーマ変更する方法を説明します。",
    "Flaskアプリにおける設定管理のベストプラクティスを紹介します。Configクラス、環境変数、開発・本番環境の切り替え方法を整理します。",
    "Flaskで画像やPDFをアップロードする方法を解説します。secure_filenameの使い方、保存先ディレクトリ設計、セキュリティ対策も含めます。",
    "Blueprint分割時に発生しやすい循環import問題の原因と解決方法を、app factory構成を前提に詳しく解説します。",
    "FlaskでJSON APIを構築する方法を紹介します。POST/GETの実装、エラーレスポンス設計、ステータスコードの扱い方を整理します。",
    "Jinja2テンプレートの継承、マクロ、共通レイアウト設計の基本を解説します。保守性を高めるテンプレート構成を紹介します。",
    "Flaskで大量データを扱う際に必要なページネーションの実装方法を解説します。LIMIT/OFFSETとクエリ最適化も扱います。",
    "Flaskアプリでの例外処理とエラーハンドリング設計について、errorhandlerの使い方とユーザ向け表示の分離方法を説明します。",
    "Flask-WTFを用いたCSRF対策の仕組みを解説します。トークン生成の流れと検証エラー時の挙動も紹介します。",
    "ユーザーごとにお気に入り登録できる機能をFlaskで実装します。中間テーブル設計とユニーク制約の付け方を解説します。",
    "管理者と一般ユーザーで表示や操作を分ける権限制御の実装方法を、Flask-LoginとUserモデル拡張で説明します。",
    "Flaskで部分一致検索や全文検索を実装する方法を紹介します。LIKE検索とインデックス設計の注意点も解説します。",
    "Gunicorn + Nginx構成によるFlaskアプリのデプロイ手順を解説します。systemd設定やログ管理も含めます。",
    "SECRET_KEYやAPIキーを安全に管理するための環境変数運用方法を、python-dotenvを使って説明します。",
    "Flaskで簡易的な管理画面を構築する方法を解説します。CRUD機能とアクセス制限を組み合わせた実装例を紹介します。"
]

IMAGE_POOL = [f"{i:02}.png" for i in range(1, 16)]

# --- ランダム日付生成関数 ---
def random_date(start, end):
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86399)
    return start + timedelta(days=random_days, seconds=random_seconds)
start_date = datetime(2025, 1, 1)
end_date = datetime.now()

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

        print("ユーザー作成...")
        users = []
        for name in USER_NAMES:
            user = User(username=name)
            user.set_password("pass1234!")
            db.session.add(user)
            users.append(user)
        db.session.commit()

        print("メモ作成...")
        memos = []
        for i in range(20):
            user = random.choice(users)
            memo = Memo(
                title=random.choice(MEMO_TITLE_FACTORY),
                content=random.choice(MEMO_CONTENT_FACTORY),
                user_id=user.id,
                image_filename=random.choice(IMAGE_POOL),
                created_at = random_date(start_date, end_date)
            )
            db.session.add(memo)
            memos.append(memo)
        db.session.commit()

        print("お気に入り作成...")
        for user in users:
            liked_count = random.randint(3, 10)
            liked_memos = random.sample(memos, liked_count)
            for rank, memo in enumerate(liked_memos[:5], start=1):
                fav = Favorite(
                    user_id=user.id,
                    memo_id=memo.id,
                    rank=random.randint(1, 5),
                    created_at=datetime.now(TZ) - timedelta(days=random.randint(0, 30))
                )
                db.session.add(fav)
        db.session.commit()

        print("ダミーデータ投入完了！")
        
        # Factoryを使用したダミーデータ生成
        # users = UserFactory.create_batch(5)
        # db.session.add_all(users)
        # db.session.commit()

        # memos = MemoFactory.create_batch(20)
        # db.session.add_all(memos)
        # db.session.commit()

        # favorites = FavoriteFactory.create_batch(50)
        # db.session.add_all(favorites)
        # db.session.commit()

        # print("Seed completed.")

if __name__ == "__main__":
    seed_data()
