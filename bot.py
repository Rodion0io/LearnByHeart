from aiogram import types,Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from languages import get_word
from random import choice
import config
import replicas
import keyboards as kb

storage = MemoryStorage()
bot = Bot(token=config.token)
dp = Dispatcher(bot,storage=storage)


class languages(StatesGroup):
    how_many_words = State()
    chosen = State()
    to_learn = State()
    learning = State()
    next = State()


@dp.message_handler(commands=['help'], state=None)
async def help(message:types.Message):
        await message.reply(replicas.messages['help'])


@dp.message_handler(commands=['start'])
async def start_bot(message:types.Message):
    await languages.chosen.set()
    await message.reply(choice(replicas.messages['greeting']), reply_markup=kb.word_packs_keyboard)


@dp.message_handler(state=languages.chosen)
async def f(message:types.Message, state: FSMContext):
    print(555)
    if message.text in ("Английский", "Французский", "Немецкий"):
        async with state.proxy() as data:
            data['chosen'] = message.text
            await message.answer("Язык выбран, спасибо.", reply_markup=kb.main_keyboard)
            await languages.to_learn.set()
    else:
        await message.answer("Такого языка у нас нет. Попробуйте еще раз (пользуйтесь клавиатурой).", reply_markup=kb.word_packs_keyboard)
        return None


@dp.message_handler(state=languages.to_learn)
async def end(message:types.Message, state: FSMContext):
    if message.text == "Учить новые слова":
        await languages.how_many_words.set()
        await message.answer("Сколько слов вы хотите выучить за этот сеанс?", reply_markup=kb.how_many_keyboard)
        async with state.proxy() as data:
            data['cnt_session'] = 0


@dp.message_handler(state=languages.how_many_words)
async def end1(message:types.Message, state: FSMContext):
    if message.text.isdigit():
        async with state.proxy() as data:
            data['current_words_number'] = int(message.text)
        await languages.learning.set()
        await message.answer("Понятно, приступим.", reply_markup=kb.new_words_keyboard)


@dp.message_handler(state=languages.learning)
async def end2(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        word = get_word(data['chosen'])
        await message.answer(f"Вы знаете это слово? {word[0]}")
        data['current_word'] = word
        await languages.next.set()


@dp.message_handler(state=languages.next)
async def end3(message:types.Message, state: FSMContext):
    if message.text == "Не знаю":
        async with state.proxy() as data:
            data.setdefault("learning_words", []).append(data['current_word'])
            await message.answer(f"Запоминайте: {data['current_word']}")
            data['cnt_session'] += 1
            if data['cnt_session'] == data['current_words_number']:
                await message.answer(f"Ваша тренировка завершена, отдохните)", reply_markup=kb.main_keyboard)
                await languages.to_learn.set()
    await languages.learning.set()


if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)