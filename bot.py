import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)

TOKEN = "8055069091:AAGhJNc7IlnGSf563DXAKobROUmGgnmFg_o"
ADMIN_ID = 8142847766

# Services et descriptions
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
    "Nous concevons des sites web modernes, professionnels et 100% adaptés à vos besoins.",
    "Nous développons des applications mobiles performantes et intuitives pour Android et iOS.",
    "Confiez-nous vos pages : nous assurons contenu, animation et croissance des abonnés.",
    "Des visuels haut de gamme pour booster votre image (affiches, flyers, réseaux...).",
    "Montage de vidéos de qualité pro pour vos projets, pubs, teasers ou réseaux sociaux.",
    "Lancez votre boutique en ligne avec un design pro, panier, paiement et interface admin.",
    "Optimisez votre visibilité avec un bon positionnement Google (SEO) et des campagnes sponsorisées (SEA).",
    "Assurez la sécurité, les mises à jour et le bon fonctionnement de votre site/app."
]

# États conversationnels
DEVIS_SERVICE, DEVIS_BUDGET, DEVIS_EMAIL, RDV_DATE, RDV_HEURE = range(5)

# Menu clavier
main_keyboard = ReplyKeyboardMarkup([
    ["📋 Voir les services", "📦 Demander un devis"],
    ["📅 Prendre rendez-vous", "💬 Contacter un conseiller"]
], resize_keyboard=True)

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bienvenue chez GT Web Studio 👋\nChoisissez une option :", reply_markup=main_keyboard)

# Callback "voir services"
async def voir_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(service, callback_data=str(i))] for i, service in enumerate(services)]
    await update.message.reply_text("💼 Voici nos services :", reply_markup=InlineKeyboardMarkup(keyboard))

# Gestion des boutons services
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    index = int(query.data)
    await query.edit_message_text(f"{services[index]}\n\n{descriptions[index]}")

# Contacter un conseiller
async def contacter_conseiller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await context.bot.send_message(ADMIN_ID, f"📩 Un utilisateur veut vous contacter : @{user.username or user.id}")
    await update.message.reply_text("✅ Un conseiller va vous répondre rapidement.", reply_markup=main_keyboard)

# ===== DEMANDER UN DEVIS =====
async def demander_devis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Quel service souhaitez-vous ?")
    return DEVIS_SERVICE

async def devis_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["service"] = update.message.text
    await update.message.reply_text("Quel est votre budget estimé ?")
    return DEVIS_BUDGET

async def devis_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["budget"] = update.message.text
    await update.message.reply_text("Merci. Entrez votre email de contact.")
    return DEVIS_EMAIL

async def devis_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    info = f"""📦 NOUVEAU DEVIS :
Email : {context.user_data['email']}
Service : {context.user_data['service']}
Budget : {context.user_data['budget']}"""
    await context.bot.send_message(ADMIN_ID, info)
    await update.message.reply_text("Merci ! Votre demande de devis a été transmise ✅", reply_markup=main_keyboard)
    return ConversationHandler.END

# ===== PRENDRE RENDEZ-VOUS =====
async def prendre_rdv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Quel jour souhaitez-vous ? (ex : 2025-06-20)")
    return RDV_DATE

async def rdv_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["date"] = update.message.text
    await update.message.reply_text("À quelle heure ? (ex : 14h00)")
    return RDV_HEURE

async def rdv_heure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["heure"] = update.message.text
    await context.bot.send_message(ADMIN_ID,
        f"📅 Nouveau RDV demandé : {context.user_data['date']} à {context.user_data['heure']}")
    await update.message.reply_text("Rendez-vous transmis à notre équipe ✅", reply_markup=main_keyboard)
    return ConversationHandler.END

# Annulation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Opération annulée", reply_markup=main_keyboard)
    return ConversationHandler.END

# Lancer le bot
async def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers simples
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^📋 Voir les services$"), voir_services))
    app.add_handler(MessageHandler(filters.Regex("^💬 Contacter un conseiller$"), contacter_conseiller))

    # Boutons inline des services
    app.add_handler(CallbackQueryHandler(button_handler))

    # Conversation pour DEVIS
    devis_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📦 Demander un devis$"), demander_devis)],
        states={
            DEVIS_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, devis_service)],
            DEVIS_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, devis_budget)],
            DEVIS_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, devis_email)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(devis_conv)

    # Conversation pour RDV
    rdv_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📅 Prendre rendez-vous$"), prendre_rdv)],
        states={
            RDV_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, rdv_date)],
            RDV_HEURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, rdv_heure)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(rdv_conv)

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
