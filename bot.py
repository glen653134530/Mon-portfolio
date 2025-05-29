import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)
import os

# === Configuration ===
TOKEN = os.environ.get("BOT_TOKEN")  # Utilisé sur Render via variables d’environnement
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8142847766"))

# === Données ===
services = [
    "🔹 Création de sites web",
    "🔹 Développement d’applications mobiles",
    "🔹 Gestion de réseaux sociaux",
    "🔹 Conception d’affiches et visuels pro",
    "🔹 Montage vidéo",
    "🔹 Création de boutiques e-commerce",
    "🔹 Référencement SEO/SEA",
    "🔹 Maintenance & sécurité"
]

descriptions = [
    "Sites web modernes, professionnels et 100% adaptés à vos besoins.",
    "Applications mobiles Android/iOS performantes et intuitives.",
    "Animation, contenu et croissance de vos réseaux sociaux.",
    "Affiches, flyers et visuels pro pour booster votre image.",
    "Montage de vidéos professionnelles pour tous vos projets.",
    "Boutiques e-commerce avec panier, paiement, et interface admin.",
    "Positionnement Google (SEO) et campagnes sponsorisées (SEA).",
    "Sécurité, mises à jour et bon fonctionnement de vos sites/apps."
]

# === États de conversation ===
DEVIS_SERVICE, DEVIS_BUDGET, DEVIS_EMAIL, RDV_DATE, RDV_HEURE = range(5)

# === Menus ===
menu_keyboard = ReplyKeyboardMarkup([
    ["📋 Voir les services", "📦 Demander un devis"],
    ["📅 Prendre rendez-vous", "💬 Contacter un conseiller"]
], resize_keyboard=True)

# === Handlers ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bienvenue chez GT Web Studio 👋\nChoisissez une option :", reply_markup=menu_keyboard)

async def voir_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(service, callback_data=str(i))] for i, service in enumerate(services)]
    await update.message.reply_text("💼 Voici nos services :", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    index = int(query.data)
    await query.edit_message_text(f"{services[index]}\n\n{descriptions[index]}")

async def contacter_conseiller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"📩 Un utilisateur veut vous contacter : @{user.username or user.id}")
    await update.message.reply_text("✅ Un conseiller va vous répondre rapidement.", reply_markup=menu_keyboard)

# === Demander un devis ===
async def demander_devis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Quel service souhaitez-vous ?")
    return DEVIS_SERVICE

async def devis_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["service"] = update.message.text
    await update.message.reply_text("Quel est votre budget estimé ?")
    return DEVIS_BUDGET

async def devis_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["budget"] = update.message.text
    await update.message.reply_text("Entrez votre email de contact :")
    return DEVIS_EMAIL

async def devis_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    context.user_data["email"] = email

    msg = f"""📦 NOUVEAU DEVIS
Service : {context.user_data['service']}
Budget : {context.user_data['budget']}
Email : {email}"""

    await context.bot.send_message(ADMIN_ID, msg)
    await update.message.reply_text("Merci ! Votre demande a été transmise ✅", reply_markup=menu_keyboard)
    return ConversationHandler.END

# === Prendre rendez-vous ===
async def prendre_rdv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Quel jour souhaitez-vous ? (ex : 2025-06-25)")
    return RDV_DATE

async def rdv_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["date"] = update.message.text
    await update.message.reply_text("À quelle heure ? (ex : 14h00)")
    return RDV_HEURE

async def rdv_heure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["heure"] = update.message.text
    msg = f"📅 Nouveau RDV demandé : {context.user_data['date']} à {context.user_data['heure']}"
    await context.bot.send_message(ADMIN_ID, msg)
    await update.message.reply_text("Votre rendez-vous a été transmis ✅", reply_markup=menu_keyboard)
    return ConversationHandler.END

# === Annulation ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Opération annulée.", reply_markup=menu_keyboard)
    return ConversationHandler.END

# === Lancement de l’application ===
async def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^📋 Voir les services$"), voir_services))
    app.add_handler(MessageHandler(filters.Regex("^💬 Contacter un conseiller$"), contacter_conseiller))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📦 Demander un devis$"), demander_devis)],
        states={
            DEVIS_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, devis_service)],
            DEVIS_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, devis_budget)],
            DEVIS_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, devis_email)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📅 Prendre rendez-vous$"), prendre_rdv)],
        states={
            RDV_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, rdv_date)],
            RDV_HEURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, rdv_heure)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    await app.run_polling()

# === Point d'entrée ===
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
