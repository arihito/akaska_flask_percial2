import random
from datetime import datetime, timedelta
# seed用にFlaskアプリを1つ生成しconfigを読み込みdb/login_manager/Blueprintを初期化する
from app import app, db
from models import User, Memo, Favorite
from datetime import datetime, timedelta
from factories.user_factory import UserFactory
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
    "Swagger(Flasgger)によるAPIドキュメント自動生成"
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
    "Flaskで簡易的な管理画面を構築する方法を解説します。CRUD機能とアクセス制限を組み合わせた実装例を紹介します。",
    "Flask-Migrate(Alembic)を利用して、DBスキーマの変更履歴を管理する方法を紹介。モデル変更からアップグレードまでのコマンド操作を網羅しています。",
    "Flask-WTFなら、CSRF対策を施したセキュアなフォームを簡単に作成可能。バリデーションエラー時のメッセージ表示方法も解説します。",
    "APIキーやパスワードをコードに直接書かず、.envファイルで管理するベストプラクティス。flask-dotenvの自動読み込み機能についても触れます。",
    "Flask-RESTfulを使用して、リソース指向のAPIを構築します。Reqparseによる引数チェックや、マーシャリングによる出力制御を詳しく見ていきます。",
    "ユニットテストから結合テストまで、pytest-flaskを使った効率的なテストコードの書き方を解説。フィクスチャによるDB初期化がポイントです。",
    "app.pyに全てを書くのではなく、create_app関数を使ってFlaskインスタンスを生成する手法。テスト時や複数環境での切り替えに非常に役立ちます。",
    "標準のクッキーベースのセッションではなく、サーバー側のRedisでセッションを保持する方法。Flask-Sessionの導入手順を解説します。",
    "頻繁にアクセスされるDBクエリやページ全体をキャッシュし、パフォーマンスを劇的に向上させるFlask-Cachingの使い方を学びます。",
    "共通のヘッダーやフッターをbase.htmlにまとめ、各ページでextends/includeを活用してDRY（二度手間を防ぐ）な開発を行う手法です。",
    "Flask開発サーバーを卒業し、本番環境で安定して動作させるためのWSGIサーバー(Gunicorn)とリバースプロキシ(Nginx)の設定例です。",
    "メール送信や画像処理など、時間の掛かる処理をバックグラウンドで行うためのCelery + Redis（またはRabbitMQ）の連携方法を解説します。",
    "複雑なモデルオブジェクトをJSONに変換（シリアライズ）し、逆にリクエストデータをバリデーション（デシリアライズ）する効率的な手順です。",
    "ユーザーに不親切なエラー画面を見せないために、errorhandlerデコレータを使用して独自のHTMLやJSONを返す仕組みを構築します。",
    "Flask-Loginを使わない、ステートレスなAPI向けのJWT認証。PyJWTを使ったエンコード・デコードと、デコレータによるアクセス制限を実装します。",
    "Flaskアプリをコンテナ化し、軽量な本番用イメージを作成する方法。docker-composeを使ったDB（PostgreSQL）との連携もカバーします。",
    "標準のloggingライブラリをFlaskに統合し、INFO/ERRORログをファイルやコンソールに適切に出力するための設定方法を整理しました。",
    "フロントエンド（React/Vueなど）と別ドメインで通信する際に発生するCORSエラー。Flask-CORSで安全に許可ドメインを設定する方法です。",
    "APIを作成しながらドキュメントも同時に更新。Flasggerを使って、Swagger UIからブラウザ上でAPIをテスト実行できる環境を整えます。"
]

IMAGE_POOL = [f"{i:02}.jpg" for i in range(1, 13)]

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
        users = UserFactory.create_batch(15)
        db.session.commit()


        print("メモ作成...")
        memos = []
        MEMOS_PER_USER = 12
        for user in users:
          for _ in range(MEMOS_PER_USER):
            memo = Memo(
              title=random.choice(MEMO_TITLE_FACTORY),
              content=random.choice(MEMO_CONTENT_FACTORY),
              user_id=user.id,
              image_filename=random.choice(IMAGE_POOL),
              created_at=random_date(start_date, end_date)
            )
            db.session.add(memo)
            memos.append(memo)
        db.session.commit()

        print("お気に入り作成...")
        for memo in memos:
            like_count = random.randint(5, 15)
            liked_users = random.sample(users, min(like_count, len(users)))

            for user in liked_users:
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
