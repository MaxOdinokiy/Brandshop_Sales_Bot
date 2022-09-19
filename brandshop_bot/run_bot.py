from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold, hlink
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import time
import os
import json


load_dotenv()
path_dotenv = Path('.')/'.env'
load_dotenv(dotenv_path=path_dotenv)

API_TOKEN = os.getenv('TOKEN')

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    start_buttons = ['Шмотка', 'Нешмотка']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.reply(
        "Hi!\nI'm Brandshop_sales_Bot!\nDesigned by Max Odinokiy",
        reply_markup=keyboard
    )


@dp.message_handler(Text(equals='Шмотка'))
async def get_item(message: types.Message):

    await message.answer('Please, wait a minute!')
    today_items = datetime.strftime(datetime.now(), '%Y_%m_%d')

    with open(f'brandshop_bot/data/{today_items}_items_data.json', 'r') as file: # noqa
        data = json.load(file)
    for key in data:
        item = data.get(key)
        card = f"{hlink(item.get('name'), item.get('url'))}\n" \
            f"{hbold('Discount: ')} {item.get('discount')} %\n" \
            f"{hbold('Price: ')} {item.get('old_price')} ₽\n" \
            f"{hbold('New price: ')} {item.get('new_price')} ₽ 🔥🔥🔥 \n" \
            f"{hbold('Sizes: ')} {item.get('sizes')}"
        await message.answer(card)
        time.sleep(10)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
