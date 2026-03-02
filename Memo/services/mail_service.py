import resend
import os

# Renderの環境変数から取得
resend.api_key = os.environ.get("RESEND_API_KEY")

def send_test_email():
    try:
        params = {
            "from": os.environ.get("RESEND_FROM_EMAIL"), # noreply@send.actlink.co.jp
            "to": "arihit.m@gmail.com",
            "subject": "RenderからのResendテスト",
            "html": "<strong>問題無く稼働している!</strong>",
        }
        email = resend.Emails.send(params)
        print(f"Success: {email}")
    except Exception as e:
        print(f"Error: {e}")
