import os
import requests
from flask import Flask, request

BOT_TOKEN = "8407881452:AAFm5RKiw54PhIZj7lZ7k-7q7yYSfdN8TLw"
WEBHOOK_URL = f"https://your-app-name.onrender.com/{BOT_TOKEN}"
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
        # API 1
        params1 = {"key": "conbo", "uid": uid, "region": "bd"}
        res1 = requests.get(API_1, params=params1, timeout=5).json()
        status1 = res1.get("status", "No response")

        # API 2
        params2 = {"uid": uid, "amount_of_likes": 100, "auth": "trial-7d", "region": "bd"}
        res2 = requests.get(API_2, params=params2, timeout=5).json()
        status2 = res2.get("status", "No response")

        return (
            f"🎮 *FREE FIRE LIKE BOT*\n"
            f"💳 Credit: SHADOW JOKER\n\n"
            f"✅ Likes Sent!\n\n"
            f"*API 1 Status:* {status1}\n"
            f"*API 2 Status:* {status2}\n\n"
            f"UID: `{uid}`"
        )
    except Exception as e:
        return f"⚠ Error sending likes: {e}"

# -----------------------------
# Send Message (With optional buttons or force reply)
# -----------------------------
def send_message(chat_id, text, buttons=None, force_reply=False):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    elif force_reply:
        payload["reply_markup"] = {"force_reply": True, "input_field_placeholder": "Enter UID here..."}
    
    requests.post(API_URL + "sendMessage", json=payload)

# -----------------------------
# Flask Routes
# -----------------------------
@app.route("/")
def home():
    return "🤖 FREE FIRE LIKE BOT Running!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    # Message Handling
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        # Start command
        if text == "/start":
            buttons = [[{"text": "Send UID", "callback_data": "send_uid"}]]
            send_message(chat_id,
                "🎮 *FREE FIRE LIKE BOT*\n"
                "💳 Credit: SHADOW JOKER\n\n"
                "👋 Welcome! Click below to send your UID.",
                buttons
            )
        # Direct /like command
        elif text.startswith("/like"):
            args = text.split(" ")
            if len(args) == 2:
                uid = args[1]
                result = send_likes(uid)
                send_message(chat_id, result)
            else:
                send_message(chat_id, "⚠ Usage: `/like <UID>`")

        # If it's a reply to Force Reply
        elif "reply_to_message" in message:
            reply_text = message["text"]
            if reply_text.isdigit() or reply_text:  # Basic UID validation
                uid = reply_text.strip()
                result = send_likes(uid)
                send_message(chat_id, result)
            else:
                send_message(chat_id, "⚠ Invalid UID! Please send a valid UID.")

    # Callback Query Handling
    if "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        data = callback["data"]

        if data == "send_uid":
            # Force reply for UID input
            send_message(chat_id,
                "✏️ Please enter your UID below:",
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