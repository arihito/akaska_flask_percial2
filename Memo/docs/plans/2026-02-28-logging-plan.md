# ロギング・エラー通知メール 実装プラン

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** アプリの全エラーをファイル・コンソールに記録し、500系エラー時に管理者へメール通知する

**Architecture:** `utils/logger.py` に `init_logger(app)` を定義し、`RotatingFileHandler`（ファイル）・`StreamHandler`（コンソール）・`SMTPHandler`（本番メール）の3ハンドラーをアプリロガーに登録する。`app.py` の `create_app()` から1行呼ぶだけで有効になる。

**Tech Stack:** Python標準 `logging` モジュール、`logging.handlers.RotatingFileHandler`、`logging.handlers.SMTPHandler`、Flask（既存）

---

### Task 1: `.gitignore` に `logs/` を追加

**Files:**
- Modify: `.gitignore`

**Step 1: .gitignore に logs/ を追記**

`.gitignore` の末尾に以下を追加する：

```
# ログファイル
logs/
```

**Step 2: 確認**

```bash
cat .gitignore
```

期待出力: `logs/` が末尾にある

**Step 3: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/.gitignore
git commit -m "chore: add logs/ to .gitignore"
```

---

### Task 2: `utils/logger.py` を新規作成

**Files:**
- Create: `utils/logger.py`

**Step 1: ファイルを作成**

`utils/logger.py` を以下の内容で作成する：

```python
import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler


def init_logger(app):
    """アプリケーションロガーを初期化する。
    - RotatingFileHandler: logs/app.log（10MB × 最大5世代）
    - StreamHandler: コンソール（DEBUGモード時のみ）
    - SMTPHandler: 管理者メール（本番かつERROR以上のみ）
    """
    log_level = logging.DEBUG if app.debug else logging.INFO
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s'
    )

    # logs/ ディレクトリがなければ作成
    log_dir = os.path.join(app.root_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # ファイルハンドラー（常時有効）
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8',
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.WARNING)

    # コンソールハンドラー（DEBUGモード時のみ）
    if app.debug:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(stream_handler)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)

    # SMTPハンドラー（本番環境かつテストでない場合のみ）
    if not app.debug and not app.testing:
        mail_host = (app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        admin_email = app.config['MAIL_USERNAME']

        mail_handler = SMTPHandler(
            mailhost=mail_host,
            fromaddr=app.config['MAIL_DEFAULT_SENDER'],
            toaddrs=[admin_email],
            subject='[Flask tech blog] サーバーエラーが発生しました',
            credentials=credentials,
            secure=(),  # TLS使用
        )
        mail_handler.setFormatter(formatter)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
```

**Step 2: 構文確認**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
conda run -n flask2_env python -c "from utils.logger import init_logger; print('OK')"
```

期待出力: `OK`

**Step 3: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/utils/logger.py
git commit -m "feat: add utils/logger.py with RotatingFile/Console/SMTP handlers"
```

---

### Task 3: `app.py` に `init_logger` 呼び出しと500エラーハンドラーを追加

**Files:**
- Modify: `app.py`

**Step 1: `app.py` を修正**

`app.py` の先頭インポート部分に以下を追加：

```python
from utils.logger import init_logger
```

`create_app()` 内の `Migrate(app, db)` の直後に以下を追記：

```python
init_logger(app)
```

`register_error_handler` の直後（または `app.register_error_handler(NotFound, show_404_page)` の下）に追加：

```python
from werkzeug.exceptions import InternalServerError

@app.errorhandler(InternalServerError)
def show_500_page(error):
    app.logger.error(
        'Internal Server Error: %s', str(error), exc_info=True
    )
    return '500 Internal Server Error', 500
```

※ 上記は `create_app()` 関数の内側に記述すること。

**Step 2: アプリ起動確認（開発モード）**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
FLASK_DEBUG=1 conda run -n flask2_env python app.py
```

期待: エラーなく起動する。`logs/app.log` が作成される（空でも可）。

**Step 3: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/app.py
git commit -m "feat: register init_logger and 500 error handler in create_app"
```

---

### Task 4: テストを追加・実行

**Files:**
- Create: `tests/test_logger.py`

**Step 1: テストファイルを作成**

`tests/test_logger.py` を以下の内容で作成する：

```python
import logging
import os
import pytest
from app import create_app


def test_log_file_created_on_startup(tmp_path):
    """アプリ起動時に logs/app.log が作成されること。"""
    config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'MAIL_SUPPRESS_SEND': True,
        'STRIPE_SECRET_KEY': '',
        'GOOGLE_CLIENT_ID': 'dummy',
        'GOOGLE_CLIENT_SECRET': 'dummy',
    }
    app = create_app(config)
    # RotatingFileHandler が登録されていることを確認
    file_handlers = [
        h for h in app.logger.handlers
        if hasattr(h, 'baseFilename')
    ]
    assert len(file_handlers) >= 1, "RotatingFileHandler が登録されていない"


def test_smtp_handler_not_added_in_testing(tmp_path):
    """TESTING=True のとき SMTPHandler が登録されないこと。"""
    config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'MAIL_SUPPRESS_SEND': True,
        'STRIPE_SECRET_KEY': '',
        'GOOGLE_CLIENT_ID': 'dummy',
        'GOOGLE_CLIENT_SECRET': 'dummy',
    }
    app = create_app(config)
    from logging.handlers import SMTPHandler
    smtp_handlers = [h for h in app.logger.handlers if isinstance(h, SMTPHandler)]
    assert len(smtp_handlers) == 0, "テスト環境でSMTPHandlerが登録されてしまっている"


def test_500_error_returns_500_status(client):
    """存在しないルートへのアクセスで404が返ること（500ハンドラーの確認は手動）。"""
    response = client.get('/nonexistent-url-xyz')
    assert response.status_code == 404
```

**Step 2: テストを実行**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
conda run -n flask2_env pytest tests/test_logger.py -v
```

期待出力:
```
tests/test_logger.py::test_log_file_created_on_startup PASSED
tests/test_logger.py::test_smtp_handler_not_added_in_testing PASSED
tests/test_logger.py::test_500_error_returns_500_status PASSED
```

**Step 3: 既存テストの回帰確認**

```bash
conda run -n flask2_env pytest tests/ -v --tb=short
```

期待: 全テストがPASSすること

**Step 4: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/tests/test_logger.py
git commit -m "test: add logger initialization tests"
```

---

### Task 5: 手動動作確認（開発環境）

**Step 1: アプリを起動**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo
FLASK_DEBUG=1 conda run -n flask2_env python app.py
```

**Step 2: ログファイルの存在確認**

別ターミナルで:

```bash
ls C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo/logs/
```

期待: `app.log` が存在する

**Step 3: 手動で ERROR ログを書き込んでファイル記録を確認**

Flaskシェルで:

```bash
conda run -n flask2_env flask shell
```

```python
from flask import current_app
current_app.logger.error("テスト用ERRORログ")
```

**Step 4: ログファイルの内容確認**

```bash
cat C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo/logs/app.log
```

期待: `ERROR [app:N] テスト用ERRORログ` が記録されている

---

## 完了の定義

- [ ] `logs/` が `.gitignore` に追加されている
- [ ] `utils/logger.py` が存在し、`init_logger(app)` が定義されている
- [ ] `app.py` から `init_logger(app)` が呼ばれている
- [ ] 500エラーハンドラーが `app.py` に登録されている
- [ ] `tests/test_logger.py` の全テストがPASSしている
- [ ] `logs/app.log` がアプリ起動時に自動生成される
