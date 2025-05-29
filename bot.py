import os
import logging
import telebot
import requests
import openai
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.reply_to(message, """Bienvenue chez GT Web Studio !

Envoyez /devis pour demander un devis
Envoyez /rdv pour prendre un rendez-vous
Envoyez /ask pour une question IA")"""

@bot.message_handler(commands=["devis"])
def demander_devis(message):
    msg = bot.send_message(message.chat.id, "Quel service vous intéresse ?")
    bot.register_next_step_handler(msg, lambda m: fin_devis(message, m.text))

def fin_devis(orig_msg, service):
    data = {"Nom": orig_msg.from_user.first_name, "Service": service}
    requests.post(GOOGLE_SCRIPT_URL, data=data)
    bot.send_message(orig_msg.chat.id, "✅ Demande de devis envoyée !")
    bot.send_message(ADMIN_ID, f"🔔 Nouvelle demande de devis : {data}")

@bot.message_handler(commands=["rdv"])
def prendre_rdv(message):
    msg = bot.send_message(message.chat.id, "Pour quel jour souhaitez-vous un RDV ?")
    bot.register_next_step_handler(msg, lambda m: fin_rdv(message, m.text))

def fin_rdv(orig_msg, jour):
    data = {"Nom": orig_msg.from_user.first_name, "Rendez-vous": jour}
    requests.post(GOOGLE_SCRIPT_URL, data=data)
    bot.send_message(orig_msg.chat.id, "✅ Rendez-vous pris en compte !")
    bot.send_message(ADMIN_ID, f"📅 Nouveau RDV demandé : {data}")

@bot.message_handler(commands=["ask"])
def ask_ai(message):
    msg = bot.send_message(message.chat.id, "Posez votre question à l'IA :")
    bot.register_next_step_handler(msg, lambda m: ai_response(message, m.text))

def ai_response(orig_msg, question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        answer = response["choices"][0]["message"]["content"]
        bot.send_message(orig_msg.chat.id, answer)
    except Exception as e:
        bot.send_message(orig_msg.chat.id, "Erreur IA.")
        bot.send_message(ADMIN_ID, f"Erreur IA: {e}")

bot.polling()
