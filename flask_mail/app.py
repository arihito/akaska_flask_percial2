import os
from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Memo/.env を読み込む
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'Memo', '.env'))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)


@app.route('/test-mail')
def test_mail():
    msg = Message(
        subject='【テスト】Flask-Mail疎通確認',
        recipients=[os.getenv('MAIL_USERNAME')],
        body=(
            'Flask-Mail による疎通確認メールです。\n'
            'このメールが届いていれば送信成功です。'
        ),
    )
    mail.send(msg)
    return 'メール送信成功！受信ボックスをご確認ください。'


if __name__ == '__main__':
    app.run(debug=True, port=5001)
