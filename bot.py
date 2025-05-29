import logging
from aiogram import Bot, Dispatcher, executor, types
import requests

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
SHEET_URL = "https://script.google.com/macros/s/AKfycbxOL8N8XOrKpGaNJWkIO9n_t9Q8rdBBR_CDh4ssgIPmxujXqv46NtyfN4PEquDWG7tTZg/exec"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    types.KeyboardButton("📋 Nos Services"),
    types.KeyboardButton("📦 Demander un devis"),
    types.KeyboardButton("📅 Prendre rendez-vous"),
    types.KeyboardButton("💬 Contacter un humain"),
    types.KeyboardButton("🧠 Poser une question à l’IA")
)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Bienvenue chez GT Web Studio ! Que souhaitez-vous faire ?", reply_markup=main_menu)

@dp.message_handler(lambda message: message.text == "📋 Nos Services")
async def services(message: types.Message):
    await message.reply("""📋 *Nos Services*

💻 Création de site web
📱 App mobile
🎨 Graphisme & logo
📲 Gestion réseaux sociaux
🎞️ Vidéo/Montage", parse_mode="Markdown""")

@dp.message_handler(lambda message: message.text == "📦 Demander un devis")
async def demande_devis(message: types.Message):
    await message.reply("🛠 Cette fonctionnalité est en cours d’intégration. Revenez bientôt !")

@dp.message_handler(lambda message: message.text == "📅 Prendre rendez-vous")
async def rendez_vous(message: types.Message):
    await message.reply("📆 Cette fonctionnalité est en cours d’intégration. Revenez bientôt !")

@dp.message_handler(lambda message: message.text == "💬 Contacter un humain")
async def contacter_humain(message: types.Message):
    await message.reply("🙋🏽‍♂️ Un conseiller vous répondra sous peu. Merci de patienter...")

@dp.message_handler(lambda message: message.text == "🧠 Poser une question à l’IA")
async def pose_question(message: types.Message):
    await message.reply("🧠 Posez-moi votre question :")

@dp.message_handler()
async def handle_ai_question(message: types.Message):
    if message.reply_to_message and "Posez-moi votre question" in message.reply_to_message.text:
        question = message.text
        headers = {"Content-Type": "application/json"}
        payload = {"inputs": question}
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            await message.reply(response.json()[0]["generated_text"])
        else:
            await message.reply("Une erreur est survenue. Veuillez réessayer plus tard.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
