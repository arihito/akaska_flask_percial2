# Flaskアプリのロギング設計

## ロギングの重要性

本番環境でのバグ調査や不正アクセスの検知にはログが不可欠です。Flask は Python 標準の `logging` モジュールを使用しており、適切に設定することで、エラーレベルに応じた記録・ファイルへの保存・管理者へのメール通知まで実現できます。

## ロギングの基本設定

### Flaskのデフォルトロガー

Flask は `app.logger` というロガーを内蔵しています。

```python
from flask import Flask

app = Flask(__name__)

@app.route('/test')
def test():
    app.logger.debug('デバッグ情報')
    app.logger.info('通常の情報')
    app.logger.warning('警告')
    app.logger.error('エラー発生')
    app.logger.critical('致命的エラー')
    return 'ok'
```

### ログレベルの設定
```python
import logging

app.logger.setLevel(logging.INFO)  # INFO以上を記録
```

## ファイルへのログ出力

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    if not app.debug:
        # ローテーティングファイルハンドラ
        # 10MB で新ファイルに、最大5ファイル保持
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        file_handler.setFormatter(formatter)

        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('アプリケーション起動')
```

`RotatingFileHandler` を使うことで、ログファイルが肥大化するのを防ぎます。古いログは自動的に `.1`, `.2` などのサフィックスが付いてローテートされます。

## エラー時のメール通知

致命的なエラーが発生した際に管理者へメールを送信します。

```python
from logging.handlers import SMTPHandler

def setup_mail_handler(app):
    if not app.debug:
        mail_handler = SMTPHandler(
            mailhost=('smtp.gmail.com', 587),
            fromaddr='noreply@example.com',
            toaddrs=['admin@example.com'],
            subject='[Flask] アプリケーションエラー',
            credentials=('gmail_user', 'gmail_pass'),
            secure=()
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
```

`setLevel(logging.ERROR)` とすることで、ERROR 以上（ERROR・CRITICAL）が発生した場合のみメールが送信されます。

## リクエストログの記録

```python
from flask import request, g
import time

@app.before_request
def log_request_start():
    g.start_time = time.time()

@app.after_request
def log_request_end(response):
    duration = time.time() - g.start_time
    app.logger.info(
        '%s %s %s %.3fs %s',
        request.method,
        request.path,
        response.status_code,
        duration,
        request.remote_addr,
    )
    return response
```

全リクエストの HTTP メソッド・パス・ステータスコード・応答時間・IPアドレスを自動記録します。パフォーマンス問題の特定や不審なアクセスの追跡に活用できます。

## 構造化ログ（JSON形式）

ログ分析ツール（Elasticsearch・Datadog 等）との連携には JSON 形式が便利です。

```python
import json
import logging

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'module': record.module,
            'message': record.getMessage(),
        }
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)
```

## まとめ

適切なロギング設計は、本番環境での問題解決速度を大幅に向上させます。RotatingFileHandler でファイルサイズを制御し、SMTPHandler で致命的エラーを即時通知する構成が実用的です。構造化ログを採用するとログ分析ツールとの連携が容易になり、大規模アプリでの運用効率が上がります。

## Flask-Talisman によるセキュリティヘッダー

ロギングと合わせてセキュリティ強化も本番環境の必須対応です。

```bash
pip install flask-talisman
```

```python
from flask_talisman import Talisman

Talisman(app, content_security_policy={
    'default-src': '\'self\'',
    'script-src': ['\'self\'', 'cdn.jsdelivr.net'],
    'style-src': ['\'self\'', 'cdn.jsdelivr.net'],
})
```

`Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security` などのセキュリティヘッダーを一括設定し、XSS・クリックジャッキングなどの攻撃を軽減します。

## エラーレベルに応じた対応フロー

| レベル | 説明 | 対応 |
|-------|------|------|
| DEBUG | 詳細なデバッグ情報 | 開発環境のみ有効 |
| INFO | 通常の動作記録 | ファイルに記録 |
| WARNING | 警告（処理は継続） | ファイルに記録 |
| ERROR | エラー（機能一部停止） | ファイル＋メール |
| CRITICAL | 致命的エラー（サービス停止リスク） | ファイル＋メール＋監視ツール |

本番では `INFO` 以上を常時記録し、`ERROR` 以上はリアルタイムで通知する設計が一般的です。
