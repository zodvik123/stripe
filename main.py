from flask import Flask, request, jsonify
import stripe

app = Flask(__name__)

# ✅ Hardcoded Stripe Secret Key (Use YOUR OWN Key Here)
stripe.api_key = "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"

# ✅ Hardcoded Bot-to-API Auth Token (also used in Telegram bot)
AUTH_TOKEN = "skey_2e7dcfc201ee4cb489bca5411c82b321"


@app.route("/", methods=["GET"])
def home():
    return "✅ Stripe 2025 Checker is live!"


@app.route("/check", methods=["POST"])
def check_card():
    # Auth check
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"status": "error", "message": "Missing or invalid auth header"}), 401

    token = auth_header.split(" ")[1]
    if token != AUTH_TOKEN:
        return jsonify({"status": "error", "message": "Invalid API token"}), 403

    # Parse card info
    data = request.get_json()
    cc = data.get("cc", "").strip()
    mm = data.get("mm", "").strip()
    yy = data.get("yy", "").strip()
    cvv = data.get("cvv", "").strip()

    if not (cc and mm and yy and cvv):
        return jsonify({"status": "error", "message": "Missing card fields"}), 400

    try:
        # Stripe safe call (2025)
        intent = stripe.PaymentIntent.create(
            amount=1,
            currency="usd",
            confirm=True,
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never"
            },
            payment_method_data={
                "type": "card",
                "card": {
                    "number": cc,
                    "exp_month": mm,
                    "exp_year": yy,
                    "cvc": cvv
                }
            }
        )

        return jsonify({
            "status": intent['status'],
            "message": "✅ Approved" if intent['status'] == "succeeded" else intent['status']
        })

    except stripe.error.CardError as e:
        return jsonify({
            "status": "declined",
            "message": "❌ Declined",
            "stripe_error": e.user_message
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Stripe error occurred",
            "stripe_error": str(e)
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
