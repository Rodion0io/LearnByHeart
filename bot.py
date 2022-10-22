from aiogram import types,Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import config

bot = Bot(token=config.token)
dp = Dispatcher(bot)

@dp.message_handler(commands='start')
async def start_bot(message: types.Message):
    await bot.send_message(message.from_user.id, f'Привет {message.from_user}')


if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)