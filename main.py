from flask import Flask, request, jsonify
import stripe
import traceback
import os

app = Flask(__name__)

STRIPE_KEY = "sk_live_YOUR_SECRET_KEY"
API_AUTH_TOKEN = "skey_2e7dcfc201ee4cb489bca5411c82b321"

stripe.api_key = STRIPE_KEY

@app.route('/')
def home():
    return '✅ Stripe Checker is online!'

@app.route('/check', methods=['POST'])
def check_card():
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {API_AUTH_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    cc = data.get('cc')
    mm = data.get('mm')
    yy = data.get('yy')
    cvv = data.get('cvv')

    if not all([cc, mm, yy, cvv]):
        return jsonify({'status': 'error', 'message': 'Missing card fields'}), 400

    try:
        intent = stripe.PaymentIntent.create(
            amount=1,
            currency='usd',
            confirm=True,
            payment_method_data={
                'type': 'card',
                'card': {
                    'number': cc,
                    'exp_month': mm,
                    'exp_year': yy,
                    'cvc': cvv,
                }
            }
        )
        return jsonify({
            'status': intent.get('status', 'unknown'),
            'message': 'Approved ✅' if intent.get('status') == 'succeeded' else 'Requires Action ⚠️'
        })

    except stripe.error.CardError as e:
        return jsonify({
            'status': 'declined',
            'message': e.user_message,
            'stripe_error': str(e)
        })
    except stripe.error.StripeError as e:
        return jsonify({
            'status': 'error',
            'message': 'Stripe error occurred',
            'stripe_error': str(e)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'trace': traceback.format_exc()
        })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
