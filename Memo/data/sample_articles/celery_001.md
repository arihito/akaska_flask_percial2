# Celeryによる非同期タスク処理

## 非同期処理の必要性

メール送信・画像リサイズ・外部API呼び出しなど、時間のかかる処理をリクエストハンドラ内で実行するとレスポンスが遅延します。Celery を使った非同期タスクキューを導入することで、重い処理をバックグラウンドに移し、ユーザーへの応答を即時化できます。

## Celeryのセットアップ

### インストール
```bash
pip install celery redis
```

Celery はブローカー（タスクキュー）に Redis または RabbitMQ を使います。ローカル開発では Redis が手軽です。

### Redisのインストール（Ubuntu）
```bash
sudo apt install redis-server
sudo systemctl start redis
```

### Celeryの初期化（Application Factoryパターン）
```python
# celery_worker.py
from app import create_app
from extensions import celery

app = create_app()
app.app_context().push()
```

```python
# extensions.py
from celery import Celery

celery = Celery()

def init_celery(app):
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        task_serializer='json',
        accept_content=['json'],
    )
    # Flask アプリコンテキストを各タスクに適用
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
```

```python
# config.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

## タスクの定義と実行

```python
# tasks/mail_tasks.py
from extensions import celery
from flask_mail import Message
from extensions import mail

@celery.task(bind=True, max_retries=3)
def send_welcome_email(self, user_id):
    """ユーザー登録後のウェルカムメール送信タスク"""
    try:
        from models import User
        user = User.query.get(user_id)
        msg = Message(
            '登録ありがとうございます',
            sender='noreply@example.com',
            recipients=[user.email]
        )
        msg.body = f'{user.username} さん、ご登録ありがとうございます！'
        mail.send(msg)
    except Exception as exc:
        # 失敗時は60秒後にリトライ（最大3回）
        raise self.retry(exc=exc, countdown=60)
```

### ビューからタスクを呼び出す
```python
@auth_bp.route('/register', methods=['POST'])
def register():
    # ... ユーザー登録処理 ...
    db.session.commit()

    # 非同期でメール送信（.delay() で即座にキューに積む）
    send_welcome_email.delay(user.id)

    flash('登録が完了しました', 'success')
    return redirect(url_for('auth.login'))
```

`.delay()` はタスクをキューに追加して即座にリターンします。実際のメール送信はワーカープロセスがバックグラウンドで処理します。

## Celeryワーカーの起動

```bash
# ワーカープロセスを起動（別ターミナルで）
celery -A celery_worker.celery worker --loglevel=info

# スケジュールタスクが必要な場合は Beat も起動
celery -A celery_worker.celery beat --loglevel=info
```

## 定期実行タスク（Celery Beat）

定期的に実行するバッチ処理は Celery Beat で管理します。

```python
from celery.schedules import crontab

celery.conf.beat_schedule = {
    # 毎日AM2時にデータ集計
    'daily-summary': {
        'task': 'tasks.report_tasks.generate_daily_report',
        'schedule': crontab(hour=2, minute=0),
    },
    # 30分ごとにキャッシュ更新
    'refresh-cache': {
        'task': 'tasks.cache_tasks.refresh_popular_articles',
        'schedule': 30 * 60,  # 秒指定
    },
}
```

## タスクの状態管理

```python
# タスクIDを保存して後から状態確認
result = send_welcome_email.delay(user.id)
task_id = result.id  # DBなどに保存

# 別のリクエストで状態確認
from celery.result import AsyncResult
task = AsyncResult(task_id)
print(task.state)   # PENDING / STARTED / SUCCESS / FAILURE
print(task.result)  # 戻り値または例外
```

## まとめ

Celery を使うことで、Flask アプリから重い処理を切り離してスケーラブルな非同期アーキテクチャを実現できます。メール送信・レポート生成・外部API連携など多くの場面で活用できます。`bind=True` とリトライ機構を組み合わせることで、障害に強いタスク処理が実現します。

## Flowerによるタスク監視

Celery のタスク状況をブラウザで監視できるダッシュボードです。

```bash
pip install flower
celery -A celery_worker.celery flower --port=5555
```

`http://localhost:5555` でダッシュボードが開き、実行中・完了・失敗したタスクの一覧、実行時間、ワーカーの状態をリアルタイムで確認できます。本番環境では Basic 認証をかけてアクセスを制限します。

## タスクの優先度とルーティング

急ぎのタスクと遅延許容のタスクを別キューで処理することで、重要な処理の遅延を防げます。

```python
# 高優先度キューにルーティング
send_welcome_email.apply_async(
    args=[user.id],
    queue='high_priority'
)

# ワーカーをキュー別に起動
# celery -A celery_worker.celery worker -Q high_priority,default
```

キュー分離により、大量のバッチ処理が緊急のメール送信をブロックするといった問題を回避できます。
