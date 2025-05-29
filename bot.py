
import logging
import openai
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import os

API_TOKEN = os.getenv("BOT_TOKEN")  # Utilisé par Render pour injecter le token de manière sécurisée

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Menu principal
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("📋 Nos Services"),
    KeyboardButton("📩 Demander un devis"),
)
main_menu.add(
    KeyboardButton("📅 Prendre rendez-vous"),
    KeyboardButton("💬 Contacter un humain"),
    KeyboardButton("🧠 Poser une question à l’IA"),
)

# Accueil
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Bienvenue chez GT Web Studio ! Que souhaitez-vous faire ?", reply_markup=main_menu)

# Nos Services
@dp.message_handler(lambda message: message.text == "📋 Nos Services")
async def services(message: types.Message):
    await message.reply("💻 Création de site web
📱 App mobile
🎨 Graphisme & logo
📲 Gestion réseaux sociaux
📷 Vidéo/Montage")

# IA HuggingFace
@dp.message_handler(lambda message: message.text == "🧠 Poser une question à l’IA")
async def ask_ai(message: types.Message):
    await message.reply("Posez-moi votre question :")
    @dp.message_handler()
    async def answer_ai(msg: types.Message):
        prompt = msg.text
        response = requests.post("https://api-inference.huggingface.co/models/google/flan-t5-small",
                                 headers={"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"},
                                 json={"inputs": prompt})
        result = response.json()
        answer = result[0]["generated_text"] if isinstance(result, list) else "Une erreur est survenue."
        await bot.send_message(chat_id=msg.chat.id, text=answer)

# Placeholder pour autres options
@dp.message_handler(lambda message: message.text in ["📩 Demander un devis", "📅 Prendre rendez-vous", "💬 Contacter un humain"])
async def form_placeholder(message: types.Message):
    await message.reply("Cette fonctionnalité est en cours d'intégration. Revenez bientôt !")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    
