from flask import Blueprint, request, abort
import stripe

webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhook')

ENDPOINT_SECRET = 'whsec_xxxxx'

@webhook_bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, ENDPOINT_SECRET
        )
    except Exception:
        abort(400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # ★ ここで注文確定
        # order_id = save_order(session)

        print('注文確定:', session['id'])

    return '', 200
