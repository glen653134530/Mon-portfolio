import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests

BOT_TOKEN = 'TON_TOKEN_ICI'
ADMIN_ID = '8142847766'
GOOGLE_SHEET_URL = 'https://script.google.com/macros/s/AKfycbxOL8N8XOrKpGaNJWkIO9n_t9Q8rdBBR_CDh4ssgIPmxujXqv46NtyfN4PEquDWG7tTZg/exec'

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("📌 Nos Services"), KeyboardButton("📅 Prendre rendez-vous"))
    markup.row(KeyboardButton("💬 Demander un devis"), KeyboardButton("🧑‍💻 Contacter un humain"))
    bot.send_message(message.chat.id, "Bienvenue chez GT Web Studio ! Que puis-je faire pour vous ?", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text

    if text == "📌 Nos Services":
        services = "- Création de site web\n- Applications mobiles\n- Graphisme\n- Vidéos animées\n- Community management"
        bot.send_message(chat_id, f"🛠️ Voici nos services :\n{services}")

    elif text == "💬 Demander un devis":
        bot.send_message(chat_id, "Quel est votre nom complet ?")
        user_data[chat_id] = {"étape": "nom", "form": "devis"}

    elif text == "📅 Prendre rendez-vous":
        bot.send_message(chat_id, "Entrez votre nom complet pour la prise de rendez-vous :")
        user_data[chat_id] = {"étape": "nom", "form": "rdv"}

    elif text == "🧑‍💻 Contacter un humain":
        bot.send_message(chat_id, "Nous avons informé un agent, il vous répondra bientôt.")
        bot.send_message(ADMIN_ID, f"⚠️ Un utilisateur souhaite parler à un humain :\nNom d'utilisateur : @{message.from_user.username or 'N/A'}\nNom : {message.from_user.first_name}")

    elif chat_id in user_data:
        étape = user_data[chat_id]["étape"]
        form = user_data[chat_id]["form"]

        if étape == "nom":
            user_data[chat_id]["nom"] = text
            bot.send_message(chat_id, "Entrez votre e-mail :")
            user_data[chat_id]["étape"] = "email"

        elif étape == "email":
            user_data[chat_id]["email"] = text
            if form == "devis":
                bot.send_message(chat_id, "Quel est votre projet ?")
                user_data[chat_id]["étape"] = "projet"
            else:
                bot.send_message(chat_id, "Choisissez une date (format JJ/MM/AAAA) :")
                user_data[chat_id]["étape"] = "date"

        elif étape == "projet":
            user_data[chat_id]["projet"] = text
            envoyer_vers_google_sheet(user_data[chat_id], "Demande de devis")
            bot.send_message(chat_id, "✅ Devis envoyé avec succès ! Nous vous contacterons rapidement.")
            bot.send_message(ADMIN_ID, f"🧾 Nouveau devis :\nNom : {user_data[chat_id]['nom']}\nEmail : {user_data[chat_id]['email']}\nProjet : {text}")
            del user_data[chat_id]

        elif étape == "date":
            user_data[chat_id]["date"] = text
            bot.send_message(chat_id, "Heure souhaitée (ex : 14h30) :")
            user_data[chat_id]["étape"] = "heure"

        elif étape == "heure":
            user_data[chat_id]["heure"] = text
            envoyer_vers_google_sheet(user_data[chat_id], "Prise de rendez-vous")
            bot.send_message(chat_id, "📆 Rendez-vous enregistré ! Un agent vous recontactera.")
            bot.send_message(ADMIN_ID, f"📅 RDV :\nNom : {user_data[chat_id]['nom']}\nEmail : {user_data[chat_id]['email']}\nDate : {user_data[chat_id]['date']} à {text}")
            del user_data[chat_id]

def envoyer_vers_google_sheet(données, type_formulaire):
    payload = {
        "Type": type_formulaire,
        "Nom": données.get("nom", ""),
        "Email": données.get("email", ""),
        "Projet": données.get("projet", ""),
        "Date": données.get("date", ""),
        "Heure": données.get("heure", "")
    }
    try:
        requests.post(GOOGLE_SHEET_URL, data=payload)
    except Exception as e:
        print("Erreur d'envoi vers Google Sheets :", e)

bot.infinity_polling()
