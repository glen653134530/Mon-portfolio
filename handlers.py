from aiogram import types
from aiogram.dispatcher import Dispatcher

def register_handlers(dp: Dispatcher):
    @dp.message_handler(commands=["start"])
    async def welcome(msg: types.Message):
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("📋 Nos Services", "📦 Demander un devis")
        kb.add("📅 Prendre rendez-vous", "💬 Contacter un humain")
        kb.add("🧠 Poser une question à l’IA")
        await msg.answer("Bienvenue chez GT Web Studio ! Que souhaitez-vous faire ?", reply_markup=kb)

    @dp.message_handler(lambda msg: msg.text == "📋 Nos Services")
    async def services(msg: types.Message):
        await msg.reply("💻 Création de site web\n📱 App mobile\n🎨 Graphisme & logo\n📲 Gestion réseaux sociaux\n🎥 Vidéo/Montage")

    @dp.message_handler(lambda msg: msg.text == "📦 Demander un devis")
    async def devis(msg: types.Message):
        await msg.reply("Cette fonctionnalité est en cours d'intégration. Revenez bientôt !")

    @dp.message_handler(lambda msg: msg.text == "📅 Prendre rendez-vous")
    async def rdv(msg: types.Message):
        await msg.reply("Merci ! Cette fonctionnalité sera bientôt disponible.")

    @dp.message_handler(lambda msg: msg.text == "💬 Contacter un humain")
    async def contact(msg: types.Message):
        await msg.reply("Un membre de notre équipe va vous contacter très bientôt.")

    @dp.message_handler(lambda msg: msg.text == "🧠 Poser une question à l’IA")
    async def ask_ia(msg: types.Message):
        await msg.reply("Posez-moi votre question :")
