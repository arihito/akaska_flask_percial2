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
