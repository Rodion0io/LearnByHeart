from aiogram import types,Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import config
from random import choice
import replicas
import keyboards as kb

bot = Bot(token=config.token)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_bot(message:types.Message):
    await message.reply(choice(replicas.messages['greeting']),reply_markup=kb.main_keyboard)


@dp.message_handler(commands=['help'])
async def help(message:types.Message):
        await message.reply(replicas.messages['help'])

@dp.message_handler()
async def add_new_words(message:types.Message):
    if message.text == "Разработчики":
        await message.answer(replicas.messages['developers'])





if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)