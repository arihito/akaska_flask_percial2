import secrets
import string
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, abort, current_app
from flask_mail import Message
from models import db, User
import stripe

webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhook')


def generate_token_password(length=16):
    """サブスク期間中に使用するトークンパスワードを生成"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_admin_token_mail(user, raw_password, expires_at):
    """管理者トークンパスワードをメールで送信"""
    from app import mail
    expires_str = expires_at.strftime('%Y年%m月%d日 %H:%M')
    msg = Message(
        subject='【メモアプリ】管理者トークンパスワードのお知らせ',
        recipients=[user.email],
    )
    msg.body = (
        f"{user.username} 様\n\n"
        f"管理者プランの決済が完了しました。\n"
        f"以下のトークンパスワードで管理者ログインしてください。\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"トークンパスワード: {raw_password}\n"
        f"有効期限: {expires_str} (UTC)\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"※ このパスワードはサブスク期間中は同じものを使用します。\n"
        f"※ 期限切れ後は再度決済が必要です。\n"
    )
    mail.send(msg)


@webhook_bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config['STRIPE_WEBHOOK_SECRET']

    print("\n######## Webhook受信 ########")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        print("######## 署名検証失敗 ########\n")
        abort(400)

    print(f"######## イベント種別: {event['type']} ########")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('metadata', {}).get('user_id')
        print(f"######## user_id: {user_id} ########")

        if user_id:
            user = User.query.get(int(user_id))
            if user:
                # 決済フラグと期限を設定
                days = current_app.config['ADMIN_PLAN_DAYS']
                user.is_paid = True
                expires_at = datetime.now(timezone.utc) + timedelta(days=days)
                user.subscription_expires_at = expires_at

                # トークンパスワード生成・保存
                raw_password = generate_token_password()
                user.set_admin_password(raw_password)
                db.session.commit()
                print(f"######## DB更新完了 / PW: {raw_password} ########")

                # メール送信
                try:
                    send_admin_token_mail(user, raw_password, expires_at)
                    print(f"######## メール送信成功 → {user.email} ########\n")
                except Exception as e:
                    print(f"######## メール送信失敗: {e} ########\n")
            else:
                print(f"######## ユーザーが見つかりません ########\n")
        else:
            print("######## metadataにuser_idなし ########\n")

    return '', 200
