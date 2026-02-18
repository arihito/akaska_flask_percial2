from flask import Flask, render_template, redirect, url_for
import stripe
from extensions import init_stripe
init_stripe()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.j2')

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'jpy',
                    'product_data': {
                        'name': 'みたらし団子',
                    },
                    'unit_amount': 600,  # 円単位
                },
                'quantity': 1, # 購入数
            }
        ],
        mode='payment',
        # 成功画面とキャンセル画面に遷移。_externalはStripeから戻るためのお作法
        success_url=url_for('success', _external=True),
        cancel_url=url_for('cancel', _external=True),
    )

    return redirect(session.url, code=303)

@app.route('/success')
def success():
		return '決済が成功しました'

@app.route('/cancel')
def cancel():
    return '決済がキャンセルされました'
