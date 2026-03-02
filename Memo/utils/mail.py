import resend
from flask import current_app


def send_mail(to: str, subject: str, html: str = None, text: str = None) -> bool:
    """Resend API でメールを送信する。

    RESEND_API_KEY または RESEND_FROM_EMAIL が未設定の場合は送信をスキップし、
    警告ログを出力して False を返す。
    """
    api_key = current_app.config.get('RESEND_API_KEY', '')
    from_email = current_app.config.get('RESEND_FROM_EMAIL', '')

    if not api_key or not from_email:
        current_app.logger.warning(
            'RESEND_API_KEY または RESEND_FROM_EMAIL が未設定のためメール送信をスキップ'
        )
        return False

    resend.api_key = api_key
    params: resend.Emails.SendParams = {
        'from': from_email,
        'to': [to],
        'subject': subject,
    }
    if html:
        params['html'] = html
    if text:
        params['text'] = text

    resend.Emails.send(params)
    return True


def send_test_email(to: str) -> tuple:
    """ResendのSPF疎通確認用テスト送信。デバッグルートから呼び出す。"""
    try:
        success = send_mail(
            to=to,
            subject="RenderからのResendテスト",
            html="<strong>問題無く稼働している!</strong>",
        )
        return success, "送信成功" if success else "設定未完了（キー/Fromアドレス未設定）"
    except Exception as e:
        return False, str(e)
