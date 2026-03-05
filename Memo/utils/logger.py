import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone


class ResendErrorHandler(logging.Handler):
    """ERROR 以上のログを Resend API でメール通知するハンドラー。
    本番環境（non-debug / non-testing）でのみ登録される。
    """

    def emit(self, record):
        try:
            from flask import current_app
            app = current_app._get_current_object()
        except RuntimeError:
            return

        try:
            import resend as _resend
            api_key   = app.config.get('RESEND_API_KEY', '')
            from_addr = app.config.get('RESEND_FROM_EMAIL', '')
            to_addr   = app.config.get('MAIL_USERNAME', '')  # 管理者メールアドレス

            if not (api_key and from_addr and to_addr):
                return

            _resend.api_key = api_key
            body = self.format(record)
            _resend.Emails.send({
                'from': from_addr,
                'to': [to_addr],
                'subject': f'[Flask tech blog] {record.levelname}: サーバーエラー発生',
                'text': body,
                'html': f'<pre style="font-family:monospace;font-size:13px">{body}</pre>',
            })
        except Exception:
            # 通知失敗はサイレントに無視（ロギング自体を止めない）
            pass


class DBLogHandler(logging.Handler):
    """ログをDBの app_logs テーブルに書き込むハンドラー。
    リクエストのスコープセッションを汚染しないよう独立セッションを使用する。
    """

    def emit(self, record):
        # アプリコンテキスト外（起動時など）では無視
        try:
            from flask import current_app
            current_app._get_current_object()
        except RuntimeError:
            return

        try:
            from sqlalchemy.orm import Session
            from models import db, AppLog
            # db.session（スコープセッション）とは独立した新規セッションで書き込む
            with Session(db.engine) as session:
                entry = AppLog(
                    level=record.levelname,
                    module=f'{record.name}:{record.lineno}',
                    message=self.format(record),
                    created_at=datetime.now(timezone.utc),
                )
                session.add(entry)
                session.commit()
        except Exception:
            # DB書き込み失敗時はサイレントに無視（ロギング自体を止めない）
            pass


def init_logger(app):
    """アプリケーションロガーを初期化する。
    - RotatingFileHandler: logs/app.log（10MB × 最大5世代）
    - StreamHandler: コンソール（DEBUGモード時のみ）
    - DBLogHandler: app_logs テーブル（INFO以上）
    - ResendErrorHandler: 管理者メール通知（本番かつERROR以上のみ）
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
    file_handler.setLevel(logging.INFO)

    # コンソールハンドラー（DEBUGモード時のみ）
    if app.debug:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(stream_handler)

    app.logger.addHandler(file_handler)

    # DBハンドラー（INFO以上をDBに書き込み）
    db_handler = DBLogHandler()
    db_handler.setFormatter(formatter)
    db_handler.setLevel(logging.INFO)
    app.logger.addHandler(db_handler)

    app.logger.setLevel(log_level)

    # Resendエラーハンドラー（本番環境かつテストでない場合のみ）
    if not app.debug and not app.testing:
        resend_handler = ResendErrorHandler()
        resend_handler.setFormatter(formatter)
        resend_handler.setLevel(logging.ERROR)
        app.logger.addHandler(resend_handler)
