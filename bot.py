
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import requests

# Configuration du logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# URL de votre script Google Apps Script
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxOL8N8XOrKpGaNJWkIO9n_t9Q8rdBBR_CDh4ssgIPmxujXqv46NtyfN4PEquDWG7tTZg/exec"

# Étapes de la conversation
NAME, EMAIL, SERVICE, BUDGET, MESSAGE = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📋 Nos Services", "📦 Demander un devis"],
        ["📅 Prendre rendez-vous", "✉️ Contacter un humain"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Bienvenue chez GT Web Studio. Que souhaitez-vous faire ?", reply_markup=reply_markup)

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Quel est votre nom ?")
    return NAME

async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Quel est votre adresse e-mail ?")
    return EMAIL

async def ask_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    await update.message.reply_text("Quel service vous intéresse ?")
    return SERVICE

async def ask_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["service"] = update.message.text
    await update.message.reply_text("Quel est votre budget ?")
    return BUDGET

async def ask_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["budget"] = update.message.text
    await update.message.reply_text("Ajoutez un message complémentaire :")
    return MESSAGE

async def submit_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["message"] = update.message.text

    data = {
        "Nom": context.user_data["name"],
        "Email": context.user_data["email"],
        "Service": context.user_data["service"],
        "Budget": context.user_data["budget"],
        "Message": context.user_data["message"]
    }

    response = requests.post(GOOGLE_SCRIPT_URL, data=data)

    if response.status_code == 200:
        await update.message.reply_text("✅ Votre demande a été envoyée avec succès. Nous vous répondrons très vite !")
    else:
        await update.message.reply_text("❌ Une erreur s'est produite lors de l'envoi. Veuillez réessayer.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Formulaire annulé.")
    return ConversationHandler.END

if __name__ == "__main__":
    import os
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    form_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📦 Demander un devis$"), ask_name)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_service)],
            SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_budget)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_message)],
            MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, submit_form)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(form_handler)

    app.run_polling()
