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
    await message.reply(choice(replicas.messages['greeting']), reply_markup=kb.next_keyboard)


@dp.message_handler()
async def start_bot(message:types.Message):
    if message.text == "Далее":
        await languages.chosen.set()
        await message.answer("Выберите язык для изучения из предложенных.", reply_markup=kb.word_packs_keyboard)

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
        await message.reply("Сколько слов вы хотите выучить за этот сеанс?", reply_markup=kb.how_many_keyboard)
    else:
        await message.reply("Не понял вас. Вы можете приступить к изучению новых слов, просто нажмите кнопку.", reply_markup=kb.main_keyboard)

@dp.message_handler(state=languages.how_many_words)
async def end1(message:types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.reply("Пожалуйста, отправьте натуральное число - количество слов.", reply_markup=kb.how_many_keyboard)
        return
    else:
        async with state.proxy() as data:
            word = get_word(data['chosen'])
            data["per_session"] = int(message.text)
            data["current_number"] = 0
            data["current_word"] = word
            data.setdefault("all_the_words", []).append(word)
            await message.reply(f"Вы знаете, как переводится '{word[0]}'?", reply_markup=kb.new_words_keyboard)

            await languages.learning.set()


@dp.message_handler(state=languages.learning)
async def end3(message:types.Message, state: FSMContext):
    if message.text == "Завершить сеанс":
        await message.reply(f"Хорошо, завершаю.", reply_markup=kb.main_keyboard)
        await languages.to_learn.set()
        return None

    if message.text == "Не знаю":
        async with state.proxy() as data:
            word = list(data['current_word'][:-1]) + ['—'] + [data['current_word'][-1]]
            print(word)
            await message.reply(f"Запоминайте: {' '.join(word)}.", reply_markup=kb.new_words_keyboard)

            word = get_word(data['chosen'])
            data['current_word'] = word
            data['all_the_words'].append(word)

            data['current_number'] += 1
            if data['current_number'] == data['per_session']:
                await languages.to_learn.set()
                await message.reply("Ваша тренировка завершена, отдохните.", reply_markup=kb.main_keyboard)
                return None


            await message.reply(f"Вы знаете, как переводится '{word[0]}'?", reply_markup=kb.new_words_keyboard)


    else:
        async with state.proxy() as data:
            word = get_word(data['chosen'])

            data['current_word'] = word
            data['all_the_words'].append(word)

            data['current_number'] += 1
            if data['current_number'] == data['per_session']:
                await languages.to_learn.set()
                await message.reply("Ваша тренировка завершена, отдохните.", reply_markup=kb.main_keyboard)
                return None

            await message.reply(f"Вы знаете, как переводится '{word[0]}'?", reply_markup=kb.new_words_keyboard)
            data['current_word'] = word
            data['all_the_words'].append(word)



if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)