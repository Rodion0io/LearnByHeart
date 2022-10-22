from aiogram import types,Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from random import choice
import config
import replicas
import keyboards as kb

storage = MemoryStorage()
bot = Bot(token=config.token)
dp = Dispatcher(bot,storage=storage)

class languages(StatesGroup):
    how_many_words = State()

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


@dp.message_handler(state=None)
@dp.message_handler(state=language.chosen)
async def f(message:types.Message):
    if message.text == "Учить новые слова":
        await languages.how_many_words.set()
        await message.reply('Сколько слов вы хотите выучить?')

@dp.message_handler(state=languages.how_many_words)
async def end(message:types.Message,state: FSMContext):
    async with state.proxy() as data:
        data['languages'] == message.text

    await state.finish()







if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)