from flask import Blueprint, request, jsonify, url_for
import stripe

BASE_PRODUCT = {
    'name': 'みたらし団子',
    'price': 600
}

TOPPINGS = {
    'kinako': {'name': 'きなこ', 'price': 0},
    'matcha': {'name': '抹茶', 'price': 50},
    'black': {'name': '黒ごま', 'price': 100},
    'special': {'name': '特製', 'price': 150},
}

checkout_bp = Blueprint('checkout', __name__, url_prefix='/checkout')

@checkout_bp.route('/create', methods=['POST'])
def create():
    data = request.get_json()

    line_items = [
        {
            'price_data': {
                'currency': 'jpy',
                'product_data': {'name': 'みたらし団子'},
                'unit_amount': 600,
            },
            'quantity': 1,
        }
    ]

    for tid, item in data.items():
        topping = TOPPINGS.get(tid)
        if not topping:
            continue

        qty = min(item['qty'], 2)

        line_items.append({
            'price_data': {
                'currency': 'jpy',
                'product_data': {'name': topping['name']},
                'unit_amount': topping['price'],
            },
            'quantity': qty,
        })

    session = stripe.checkout.Session.create(
        mode='payment',
        line_items=line_items,
        success_url=url_for('checkout.success', _external=True),
        cancel_url=url_for('checkout.cancel', _external=True),
    )

    return jsonify({'url': session.url})

@checkout_bp.route('/success')
def success():
    return '決済が完了しました（テスト）'

@checkout_bp.route('/cancel')
def cancel():
    return '決済がキャンセルされました'
