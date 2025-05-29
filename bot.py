import logging
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import openai

# Charger les variables d’environnement
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")

openai.api_key = OPENAI_API_KEY

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [["📋 Nos Services", "📦 Demander un devis"],
               ["📅 Prendre rendez-vous", "✉️ Contacter un humain"]]
    await update.message.reply_text(
        "Bienvenue chez GT Web Studio !\n\n"
        "Envoyez /devis pour demander un devis\n"
        "Envoyez /rdv pour prendre un rendez-vous\n"
        "Envoyez /ask pour une question IA",
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Posez votre question à l'IA :")
    return 1

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"Erreur IA : {e}")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("ask", ask)],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)]},
        fallbacks=[]
    ))
    app.run_polling()

if __name__ == "__main__":
    main()
