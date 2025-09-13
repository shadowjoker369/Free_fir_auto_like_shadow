import os
import requests
from flask import Flask, request

# -----------------------------
# Telegram Bot Configuration
# -----------------------------
BOT_TOKEN = "8407881452:AAFm5RKiw54PhIZj7lZ7k-7q7yYSfdN8TLw"
WEBHOOK_URL = f"https://free-fir-auto-like-shadow.onrender.com/{BOT_TOKEN}"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# API Endpoints
API_1 = "http://103.149.253.241:2010/like"
API_2 = "https://likes.ffgarena.cloud/api/v2/likes"

app = Flask(__name__)

# -----------------------------
# Send Likes Function
# -----------------------------
def send_likes(uid: str) -> str:
    try:
        # API 1 Call
        params1 = {"key": "conbo", "uid": uid, "region": "bd"}
        res1 = requests.get(API_1, params=params1, timeout=5).json()
        status1 = res1.get("status", "❌ No response")

        # API 2 Call
        params2 = {"uid": uid, "amount_of_likes": 100, "auth": "trial-7d", "region": "bd"}
        res2 = requests.get(API_2, params=params2, timeout=5).json()
        status2 = res2.get("status", "❌ No response")

        return (
            "🎮 *FREE FIRE AUTO LIKE BOT*\n"
            "───────────────────────\n"
            f"🆔 UID: `{uid}`\n\n"
            f"⚡ API-1 Response: {status1}\n"
            f"⚡ API-2 Response: {status2}\n\n"
            "✅ Likes Request Sent Successfully!\n"
            "───────────────────────\n"
            "💳 *Credit:* SHADOW JOKER"
        )
    except Exception as e:
        return f"⚠ Error: {e}"

# -----------------------------
# Send Message with optional buttons or force reply
# -----------------------------
def send_message(chat_id, text, buttons=None, force_reply=False):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    elif force_reply:
        payload["reply_markup"] = {"force_reply": True, "input_field_placeholder": "Enter your UID..."}

    requests.post(API_URL + "sendMessage", json=payload)

# -----------------------------
# Flask Routes
# -----------------------------
@app.route("/")
def home():
    return "🤖 FREE FIRE AUTO LIKE BOT by SHADOW JOKER is Running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    # Normal message
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text == "/start":
            buttons = [[{"text": "🚀 Send UID", "callback_data": "send_uid"}]]
            send_message(
                chat_id,
                "🎮 *Welcome to FREE FIRE AUTO LIKE BOT!*\n\n"
                "👉 Click below to send your UID and get likes instantly.\n\n"
                "💳 *Credit:* SHADOW JOKER",
                buttons
            )

        elif text.startswith("/like"):
            args = text.split(" ")
            if len(args) == 2:
                uid = args[1]
                result = send_likes(uid)
                send_message(chat_id, result)
            else:
                send_message(chat_id, "⚠ Usage: `/like <UID>`")

        elif "reply_to_message" in message:
            uid = message["text"].strip()
            if uid:
                result = send_likes(uid)
                send_message(chat_id, result)
            else:
                send_message(chat_id, "⚠ Invalid UID! Please try again.")

    # Callback button
    if "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        data = callback["data"]

        if data == "send_uid":
            send_message(
                chat_id,
                "✏️ Please enter your Free Fire UID:",
                force_reply=True
            )

    return "ok"

# -----------------------------
# Set Webhook Automatically
# -----------------------------
def set_webhook():
    res = requests.get(API_URL + "setWebhook", params={"url": WEBHOOK_URL})
    print("Webhook setup response:", res.json())

# -----------------------------
if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
