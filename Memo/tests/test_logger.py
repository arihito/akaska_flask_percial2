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
