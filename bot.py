import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import requests

# --- Config ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
SHEET_URL = os.getenv("SHEET_URL")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# --- Google Sheet Setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL)

# --- Menu ---
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("📋 Nos Services"),
    KeyboardButton("📦 Demander un devis"),
    KeyboardButton("📅 Prendre rendez-vous"),
    KeyboardButton("💬 Contacter un humain"),
    KeyboardButton("🧠 Poser une question à l’IA")
)

# --- Commande start ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Bienvenue chez GT Web Studio ! Que souhaitez-vous faire ?", reply_markup=main_menu)

# --- Nos Services ---
@dp.message_handler(lambda message: message.text == "📋 Nos Services")
async def services(message: types.Message):
    await message.reply("💻 Création de site web
📱 App mobile
🎨 Graphisme & logo
📲 Gestion réseaux sociaux
🎬 Vidéo/Montage")

# --- Demander un devis ---
@dp.message_handler(lambda message: message.text == "📦 Demander un devis")
async def ask_for_quote(message: types.Message):
    await message.reply("Veuillez indiquer votre nom :")
    dp.register_message_handler(get_name, state="get_name")

async def get_name(message: types.Message):
    name = message.text
    await message.reply("Votre email :")
    dp.register_message_handler(lambda m: get_email(m, name), state="get_email")

async def get_email(message: types.Message, name):
    email = message.text
    await message.reply("Quel service souhaitez-vous ?")
    dp.register_message_handler(lambda m: get_service(m, name, email), state="get_service")

async def get_service(message: types.Message, name, email):
    service = message.text
    await message.reply("Quel est votre budget ?")
    dp.register_message_handler(lambda m: get_budget(m, name, email, service), state="get_budget")

async def get_budget(message: types.Message, name, email, service):
    budget = message.text
    await message.reply("Décrivez votre projet :")
    dp.register_message_handler(lambda m: save_devis(m, name, email, service, budget), state="save_devis")

async def save_devis(message: types.Message, name, email, service, budget):
    msg = message.text
    sheet.worksheet("Devis").append_row([datetime.now().strftime("%d/%m/%Y %H:%M:%S"), name, email, service, budget, msg])
    await message.reply("✅ Votre demande de devis a été envoyée avec succès !")

# --- Rendez-vous ---
@dp.message_handler(lambda message: message.text == "📅 Prendre rendez-vous")
async def ask_rdv(message: types.Message):
    await message.reply("Entrez la date souhaitée (jj/mm/aaaa) :")
    dp.register_message_handler(get_rdv_date, state="get_rdv_date")

async def get_rdv_date(message: types.Message):
    date = message.text
    await message.reply("Heure souhaitée :")
    dp.register_message_handler(lambda m: get_rdv_time(m, date), state="get_rdv_time")

async def get_rdv_time(message: types.Message, date):
    hour = message.text
    await message.reply("Sujet du rendez-vous :")
    dp.register_message_handler(lambda m: save_rdv(m, date, hour), state="save_rdv")

async def save_rdv(message: types.Message, date, hour):
    sujet = message.text
    sheet.worksheet("Rendez-vous").append_row([datetime.now().strftime("%d/%m/%Y %H:%M:%S"), date, hour, sujet])
    await message.reply("✅ Rendez-vous enregistré avec succès !")

# --- Contacter un humain ---
@dp.message_handler(lambda message: message.text == "💬 Contacter un humain")
async def contact_admin(message: types.Message):
    await message.reply("Expliquez votre besoin :")
    dp.register_message_handler(lambda m: forward_to_admin(m), state="forward_to_admin")

async def forward_to_admin(message: types.Message):
    text = message.text
    sheet.worksheet("Messages").append_row([datetime.now().strftime("%d/%m/%Y %H:%M:%S"), message.from_user.full_name, text])
    await bot.send_message(ADMIN_ID, f"📩 Message reçu de {message.from_user.full_name} :
{text}")
    await message.reply("✅ Un humain vous contactera très bientôt.")

# --- IA HuggingFace ---
@dp.message_handler(lambda message: message.text == "🧠 Poser une question à l’IA")
async def ask_ai(message: types.Message):
    await message.reply("Posez-moi votre question :")
    dp.register_message_handler(answer_ai, state="answer_ai")

async def answer_ai(message: types.Message):
    question = message.text
    response = requests.post("https://api-inference.huggingface.co/models/gpt2", headers={
        "Authorization": f"Bearer {os.getenv('HF_TOKEN')}"
    }, json={"inputs": question})
    answer = response.json()
    text = answer[0]["generated_text"] if isinstance(answer, list) else "❌ Erreur IA."
    sheet.worksheet("Questions IA").append_row([datetime.now().strftime("%d/%m/%Y %H:%M:%S"), question, text])
    await message.reply(text)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
