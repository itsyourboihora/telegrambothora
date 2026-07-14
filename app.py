from flask import Flask, request
import requests
import os

# ---- YOUR SETTINGS ----
BOT_TOKEN = "8693301178:AAF2nNn4Igy_Da5UW347uX7LLv95QfokVyc"
OWNER_CHAT_ID = "7766147200"
WELCOME_MESSAGE = "Special VC(with cowgirl pose, doggy pose, loud moan) spanking , tongue showing , playing : 3200k for 12 mins, 2200k for 8 mins
Normal VC: 1700 for 10 mins, 1200k for 6 mins"
# -------------------------

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
app = Flask(__name__)

def send_message(chat_id, text, with_pay_button=False):
    data = {"chat_id": chat_id, "text": text}
    if with_pay_button:
        data["reply_markup"] = (
            '{"inline_keyboard": [[{"text": "\\ud83d\\udcb3 Pay Now", "callback_data": "pay_now"}]]}'
        )
    requests.post(f"{API_URL}/sendMessage", data=data)

def send_qr_code(chat_id):
    with open("qr.jpg", "rb") as photo:
        requests.post(
            f"{API_URL}/sendPhoto",
            data={"chat_id": chat_id, "caption": "Scan this QR code to pay 🙏"},
            files={"photo": photo},
        )

def answer_callback_query(callback_query_id):
    requests.post(f"{API_URL}/answerCallbackQuery", data={"callback_query_id": callback_query_id})

@app.route("/", methods=["GET"])
def home():
    return "Bot is alive!"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()

    # Handle a tap on the "Pay Now" button
    if "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        if callback.get("data") == "pay_now":
            send_qr_code(chat_id)
        answer_callback_query(callback["id"])
        return "ok"

    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        first_name = message["chat"].get("first_name", "Someone")
        username = message["chat"].get("username", "no username")

        if str(chat_id) == OWNER_CHAT_ID:
            # Owner replying: /reply <chat_id> <message>
            if text.startswith("/reply"):
                parts = text.split(" ", 2)
                if len(parts) == 3:
                    target_id, reply_text = parts[1], parts[2]
                    send_message(target_id, reply_text)
        else:
            # Auto-reply to the customer, with a Pay Now button
            send_message(chat_id, WELCOME_MESSAGE, with_pay_button=True)
            # Send a copy to the owner
            copy_text = (
                f"New message from {first_name} (@{username})\n"
                f"Chat ID: {chat_id}\n\n"
                f"\"{text}\"\n\n"
                f"To reply, send: /reply {chat_id} your message here"
            )
            send_message(OWNER_CHAT_ID, copy_text)

    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
