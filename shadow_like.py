import os
import requests
from flask import Flask, request

# -----------------------------
# Telegram Bot Configuration
# -----------------------------
BOT_TOKEN = "8407881452:AAFm5RKiw54PhIZj7lZ7k-7q7yYSfdN8TLw"
WEBHOOK_URL = f"https://free-fir-auto-like-shadow.onrender.com/{BOT_TOKEN}"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# Like API (single)
LIKE_API = "https://likes.ffgarena.cloud/api/v2/likes?uid={uid}&amount_of_likes=100&auth=trial-7d&region=bd"

# UID Info APIs
UID_APIS = [
    "https://api-check-gpl.vercel.app/check?uid={uid}",
    "https://infoplayerbngx.vercel.app/get?uid={uid}",
    "https://info-ob50-gpl.vercel.app/get?uid={uid}",
    "https://info-me-ob50.vercel.app/get?uid={uid}"
]

app = Flask(__name__)

# -----------------------------
# Safe API Caller
# -----------------------------
def safe_api_call(url: str):
    try:
        res = requests.get(url, timeout=6)
        if res.status_code == 200:
            return res.json()
    except:
        return None
    return None

# -----------------------------
# Send Likes Function
# -----------------------------
def send_likes(uid: str) -> str:
    url = LIKE_API.format(uid=uid)
    result = safe_api_call(url)
    if result:
        response = f"✅ {url.split('/')[2]} → {result}"
        return (
            "🎮 *FREE FIRE AUTO LIKE BOT*\n"
            "───────────────────────\n"
            f"🆔 UID: `{uid}`\n\n" + response +
            "\n\n💳 *Credit:* SHADOW JOKER"
        )
    else:
        return f"⚠ Like API did not respond for UID `{uid}`"

# -----------------------------
# UID Info Function
# -----------------------------
def get_uid_info(uid: str) -> str:
    responses = []
    for api in UID_APIS:
        url = api.format(uid=uid)
        result = safe_api_call(url)
        if result:
            responses.append(f"✅ {api.split('/')[2]} → `{result}`")
    if not responses:
        return f"⚠ No Info API responded for UID `{uid}`"
    return (
        "ℹ️ *FREE FIRE UID INFORMATION*\n"
        "───────────────────────\n"
        f"🆔 UID: `{uid}`\n\n" + "\n".join(responses) +
        "\n\n💳 *Credit:* SHADOW JOKER"
    )

# -----------------------------
# Send Message with buttons or force reply
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

    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text == "/start":
            buttons = [
                [{"text": "🚀 Send UID (Likes)", "callback_data": "send_uid"}],
                [{"text": "ℹ️ UID Information", "callback_data": "uid_info"}]
            ]
            send_message(
                chat_id,
                "🎮 *Welcome to FREE FIRE AUTO LIKE BOT!*\n\n"
                "👉 Choose an option below:\n\n"
                "💳 *Credit:* SHADOW JOKER",
                buttons
            )

        elif "reply_to_message" in message:
            uid = text.strip()
            if uid:
                reply_text = message["reply_to_message"].get("text", "")
                if "Information" in reply_text:
                    result = get_uid_info(uid)
                else:
                    result = send_likes(uid)
                send_message(chat_id, result)
            else:
                send_message(chat_id, "⚠ Invalid UID! Please try again.")

    if "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        data = callback["data"]

        if data == "send_uid":
            send_message(chat_id, "✏️ Enter your Free Fire UID for Likes:", force_reply=True)
        elif data == "uid_info":
            send_message(chat_id, "✏️ Enter your Free Fire UID for Information:", force_reply=True)

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
