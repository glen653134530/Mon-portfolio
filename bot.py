
import logging
import openai
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Configure ton token ici
BOT_TOKEN = "TON_BOT_TOKEN_ICI"
OPENAI_API_KEY = "TA_CLE_API_OPENAI_ICI"
ADMIN_ID = 8142847766

openai.api_key = OPENAI_API_KEY

# Config log
logging.basicConfig(level=logging.INFO)

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📋 Nos Services", "📦 Demander un devis"],
        ["📅 Prendre rendez-vous", "✉️ Contacter un humain"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Bienvenue chez GT Web Studio !\n\n"
        "Envoyez /devis pour demander un devis\n"
        "Envoyez /rdv pour prendre un rendez-vous\n"
        "Envoyez /ask pour une question IA",
        reply_markup=reply_markup
    )

# Commande IA
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Posez votre question à l'IA :")
    return 1

async def ai_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        await update.message.reply_text(completion.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text(f"Erreur IA:\n{e}")
    return ConversationHandler.END

# Commande /devis
async def devis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envoyez votre demande de devis (Nom, Email, Service, Budget, Message).")
    return ConversationHandler.END

# Commande /rdv
async def rdv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envoyez vos infos de RDV (Nom, Projet, Date, Heure).")
    return ConversationHandler.END

# Commande /contacter
async def contacter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Un humain sera notifié. Nous vous répondrons rapidement.")
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"👤 Un utilisateur demande de l'aide : {update.effective_user.first_name}")
    return ConversationHandler.END

# Lancer le bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("devis", devis))
    app.add_handler(CommandHandler("rdv", rdv))
    app.add_handler(CommandHandler("contacter", contacter))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("ask", ask)],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, ai_response)]},
        fallbacks=[]
    ))

    app.run_polling()

if __name__ == "__main__":
    main()
