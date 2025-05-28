
from flask import Flask, request
import requests

app = Flask(__name__)
BOT_TOKEN = "8055069091:AAGhJNc7IlnGSf563DXAKobROUmGgnmFg_o"
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

@app.route('/', methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        message = data["message"].get("text", "")

        response = {"chat_id": chat_id, "text": "Bien reçu : " + message}
        requests.post(URL, json=response)
    return {"ok": True}

@app.route('/')
def index():
    return "Bot GT Web Studio est actif !"
