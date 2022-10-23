import config
import replicas
import keyboards as kb
import asyncio

from aiogram import types, Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from random import choice

from languages import get_word


storage = MemoryStorage()
bot = Bot(token=config.token)
dp = Dispatcher(bot, storage=storage)


class User(StatesGroup):
    how_many_words = State()
    chosen = State()
    to_learn = State()
    learning = State()
    next = State()
    repetition = State()


@dp.message_handler(commands=['help'], state=None)
async def helping(message: types.Message):
    await message.reply(replicas.messages['help'])


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(choice(replicas.messages['greeting']), reply_markup=kb.next_keyboard)


@dp.message_handler()
async def next_message(message: types.Message):
    if message.text == "Далее":
        await User.chosen.set()
        await message.answer("Выберите язык для изучения из предложенных.", reply_markup=kb.word_packs_keyboard)


@dp.message_handler(state=User.chosen)
async def choose(message: types.Message, state: FSMContext):
    if message.text in ("Английский", "Французский", "Немецкий"):
        async with state.proxy() as data:
            data['chosen'] = message.text
            await message.answer("Язык выбран, спасибо.", reply_markup=kb.main_keyboard)
            await User.to_learn.set()
    else:
        await message.answer("Такого языка у нас нет. Попробуйте еще раз (пользуйтесь клавиатурой).",
                             reply_markup=kb.word_packs_keyboard)
        return None


@dp.message_handler(state=User.to_learn)
async def how_many_words(message: types.Message):
    if message.text == "Учить новые слова":
        await User.how_many_words.set()
        await message.reply("Сколько слов вы хотите выучить за этот сеанс?", reply_markup=kb.how_many_keyboard)
    else:
        await message.reply("Не понял вас. Вы можете приступить к изучению новых слов, просто нажмите кнопку.",
                            reply_markup=kb.main_keyboard)


@dp.message_handler(state=User.how_many_words)
async def start_learning(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.reply("Пожалуйста, отправьте натуральное число - количество слов.",
                            reply_markup=kb.how_many_keyboard)
        return
    else:
        async with state.proxy() as data:
            word = get_word(data['chosen'])
            data["per_session"] = int(message.text)
            data["current_number"] = 0
            data["current_word"] = word
            if 'all_the_words' not in data:
                data["all_the_words"] = []
            await message.reply(f"Вы знаете, как переводится '{word[0]}'?", reply_markup=kb.new_words_keyboard)

            await User.learning.set()


@dp.message_handler(state=User.learning)
async def end3(message: types.Message, state: FSMContext):
    if message.text == "Завершить сеанс":
        await message.reply(f"Хорошо, завершаю.", reply_markup=kb.main_keyboard)
        await User.to_learn.set()
        await asyncio.sleep(5)
        await repeat(message, state)

        return None

    if message.text == "Не знаю":
        async with state.proxy() as data:
            word = list(data['current_word'][:-1]) + ['—'] + [data['current_word'][-1]]

            data['all_the_words'].append(word)

            await message.reply(f"Запоминайте: {' '.join(word)}.", reply_markup=kb.new_words_keyboard)

            word = get_word(data['chosen'])
            data['current_word'] = word

            data['current_number'] += 1
            if data['current_number'] == data['per_session']:
                await User.to_learn.set()
                await message.reply("Ваша тренировка завершена, отдохните.", reply_markup=kb.main_keyboard)
                await asyncio.sleep(5)
                await repeat(message, state)

                return None

            await message.reply(f"Вы знаете, как переводится '{word[0]}'?", reply_markup=kb.new_words_keyboard)

    else:
        async with state.proxy() as data:
            word = get_word(data['chosen'])
            data['current_word'] = word

            data['current_number'] += 1
            if data['current_number'] == data['per_session']:
                await User.to_learn.set()
                await message.reply("Ваша тренировка завершена, отдохните.", reply_markup=kb.main_keyboard)
                await asyncio.sleep(5)
                await repeat(message, state)
                return None

            await message.reply(f"Вы знаете, как переводится '{word[0]}'?", reply_markup=kb.new_words_keyboard)
            data['current_word'] = word


CNT = 0


@dp.message_handler(state=User.repetition)
async def repetition_function(message: types.Message, state: FSMContext):
    global CNT

    if message.text == "Завершить сеанс":
        await message.answer("Хорошо, жду вас снова через 24 часа (напомню).", reply_markup=kb.main_keyboard)
        CNT = 0
        async with state.proxy() as data:
            data['all_the_words'] = []
            data['current_word'] = []
            data['current_number'] = 0
            data['per_session'] = 0
        await User.to_learn.set()
        await asyncio.sleep(24 * 60 * 60)

    if message.text == 'Не помню':
        async with state.proxy() as data:
            if CNT < len(data['all_the_words']):
                if 'index' not in data:
                    data['index'] = 0
                word = data['all_the_words'][CNT]
                await message.answer(f"Вспоминайте: {' '.join(word)}.")

                if CNT + 1 < len(data['all_the_words']):
                    CNT += 1
                    word = data['all_the_words'][CNT]
                    await message.answer(f"Вы помните, как переводится '{word[0]}'?")
                else:
                    await repeat(message, state, True)
            else:
                await repeat(message, state, True)

    elif message.text == "Помню":
        async with state.proxy() as data:
            if CNT + 1 < len(data['all_the_words']):
                if 'index' not in data:
                    data['index'] = 0
                CNT += 1
                word = data['all_the_words'][CNT]
                await message.answer(f"Вы помните, как переводится '{word[0]}'?")
            else:
                await repeat(message, state, True)


async def repeat(message, state, finish=False):
    global CNT
    if message.text == "Завершить сеанс":
        await message.answer("Хорошо, жду вас снова через 24 часа (напомню).", reply_markup=kb.main_keyboard)
        CNT = 0
        async with state.proxy() as data:
            data['all_the_words'] = []
            data['current_word'] = []
            data['current_number'] = 0
            data['per_session'] = 0
        await User.to_learn.set()
        await asyncio.sleep(24 * 60 * 60)

    if finish:
        await message.answer("Слова закончились. Вы великолепны! Следующее повторение - через 24 часа, я вам напомню.",
                             reply_markup=kb.main_keyboard)
        CNT = 0
        async with state.proxy() as data:
            data['all_the_words'] = []
            data['current_word'] = []
            data['current_number'] = 0
            data['per_session'] = 0
        await User.to_learn.set()
        await asyncio.sleep(24 * 60 * 60)

    async with state.proxy() as data:
        if len(data['all_the_words']) > CNT:
            word = data['all_the_words'][CNT]
            await message.answer(f"Помните, как переводится '{word[0]}'?", reply_markup=kb.learning_keyboard)
            await User.repetition.set()
        else:
            pass


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
