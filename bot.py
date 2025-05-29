import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_ID = 8142847766

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(service, callback_data=str(i))] for i, service in enumerate(services)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Bienvenue chez GT Web Studio !

💼 Voici nos services :", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    index = int(query.data)
    response = f"{services[index]}\n\n{descriptions[index]}"
    await query.edit_message_text(text=response)

async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
