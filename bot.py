

import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Initialisation de la connexion Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("GT_WEB_Studio_Formulaire").worksheet("Devis")

# États pour ConversationHandler
SERVICE, BUDGET, DESCRIPTION, EMAIL = range(4)

# ID de l'administrateur pour les notifications
ADMIN_ID = 8142847766

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📋 Nos Services", "📦 Demander un devis"],
                ["📅 Prendre rendez-vous", "✉️ Contacter un humain"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Bienvenue sur le bot GT Web Studio 👋", reply_markup=reply_markup)

async def demander_devis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Quel service souhaitez-vous ?")
    return SERVICE

async def recevoir_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["service"] = update.message.text
    await update.message.reply_text("Quel est votre budget ?")
    return BUDGET

async def recevoir_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["budget"] = update.message.text
    await update.message.reply_text("Décrivez votre besoin en quelques lignes.")
    return DESCRIPTION

async def recevoir_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["message"] = update.message.text
    await update.message.reply_text("Merci ! Enfin, indiquez votre adresse email.")
    return EMAIL

async def recevoir_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    data = [now, context.user_data["email"], context.user_data["service"],
            context.user_data["budget"], context.user_data["message"]]
    sheet.append_row(data)

    await update.message.reply_text("✅ Votre demande de devis a été envoyée avec succès !")

    # Notification admin
  notif = f"📩 NOUVEAU DEVIS\nNom : {name}\nEmail : {email}\nService : {service}\nBudget : {budget}\nMessage : {message}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=notif)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Opération annulée.")
    return ConversationHandler.END

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token("8055069091:AAGhJNc7IlnGSf563DXAKobROUmGgnmFg_o").build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(📦 Demander un devis)$"), demander_devis)],
        states={
            SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recevoir_service)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, recevoir_budget)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, recevoir_description)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, recevoir_email)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    app.run_polling()
