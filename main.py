import threading

from flask import Flask, request

from facebook_functions import send_message_fb
import config
from openai_functions import ask_openai_assistant
from whatsapp_functions import send_message_whatsapp
app = Flask(__name__)

@app.route("/")
def handle_home():
    return "OK", 200

@app.route("/facebook", methods=["GET"])
def handle_facebook_get():
    mode = request.args.get("hub.mode")
    verify_token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and verify_token == config.FB_VERIFY_TOKEN:
        print("WEBHOOK VERIFIED.")
        return challenge, 200
    else:
        return "BAD REQUEST", 403
        
def call_ask_openai_assistant_send_message_to_fb_messenger(query: str, recipient_id: str) -> None:
    reply = ask_openai_assistant(query=query, recipient_id=recipient_id)
    send_message_fb(message=reply, recipient_id=recipient_id)

def call_ask_openai_assistant_send_message_to_whatsapp(query: str, recipient_id: str) -> None:
    reply = ask_openai_assistant(query=query, recipient_id=recipient_id)
    send_message_whatsapp(message=reply, recipient_id=recipient_id)

@app.route("/facebook", methods=["POST"])
def handle_facebook_post():
    try:
        body = request.get_json()
        recipient_id = body["entry"][0]["messaging"][0]["sender"]["id"]
        query = body["entry"][0]["messaging"][0]["message"]["text"]
        threading.Thread(
            target=call_ask_openai_assistant_send_message_to_fb_messenger,
            args=(query, recipient_id)
        ).start()
    except:
        pass
    return "OK", 200

@app.route("/whatsapp", methods=["POST"])
def handle_whatsapp_post():
    try:
        query = request.form.get("Body")
        recipient_id = request.form.get("From")

        threading.Thread(
                target=call_ask_openai_assistant_send_message_to_whatsapp,
                args=(query, recipient_id)
            ).start()
    except:
        pass
    return "OK", 200

