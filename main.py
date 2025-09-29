import os
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import web
import json

# Ваш файл з балансами
BALANCES_FILE = 'balances.json'

# Функція для завантаження балансів
def load_balances():
    if os.path.exists(BALANCES_FILE):
        with open(BALANCES_FILE, 'r') as f:
            return json.load(f)
    return {}

# Функція для збереження балансів
def save_balances(balances):
    with open(BALANCES_FILE, 'w') as f:
        json.dump(balances, f, indent=4)

# Ініціалізація бота
API_TOKEN = os.getenv('API_TOKEN')
if not API_TOKEN:
    raise RuntimeError("API_TOKEN not found in environment variables.")

WEBHOOK_HOST = os.getenv('WEBHOOK_HOST', 'https://your-app-name.deno.dev')
WEBHOOK_PATH = f'/{API_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Команди вашого бота
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привіт! Я ваш бот для відстеження балансу. Ви можете додати мене до групи.")

@dp.message_handler(commands=['add'])
async def add_balance(message: types.Message):
    try:
        _, amount_str = message.text.split(maxsplit=1)
        amount = float(amount_str)
        user_id = str(message.from_user.id)
        balances = load_balances()
        current_balance = balances.get(user_id, 0.0)
        balances[user_id] = current_balance + amount
        save_balances(balances)
        await message.reply(f"Додано {amount}. Ваш новий баланс: {balances[user_id]}")
    except (ValueError, IndexError):
        await message.reply("Будь ласка, вкажіть суму для додавання. Наприклад: /add 100")

@dp.message_handler(commands=['balance'])
async def show_balance(message: types.Message):
    user_id = str(message.from_user.id)
    balances = load_balances()
    balance = balances.get(user_id, 0.0)
    await message.reply(f"Ваш поточний баланс: {balance}")

# Налаштування вебхуків
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()

if __name__ == '__main__':
    app = get_new_configured_app(dp, WEBHOOK_PATH)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host='0.0.0.0', port=os.getenv('PORT', 8080))
