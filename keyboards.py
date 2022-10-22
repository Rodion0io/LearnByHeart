from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


return_button = KeyboardButton('Завершить сеанс')
back_button = KeyboardButton('Назад')

next_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton("Далее"))

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row(KeyboardButton("Учить новые слова"))

word_packs_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
word_packs_keyboard.row(KeyboardButton("Английский"), KeyboardButton("Французский")).row(KeyboardButton("Немецкий"))


how_many_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
how_many_keyboard.row(KeyboardButton('5'), KeyboardButton('10'), KeyboardButton('15'))
how_many_keyboard.row(KeyboardButton('20'), KeyboardButton('25'), KeyboardButton('30'))

leaning_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton('Не помню'), KeyboardButton('Помню'))
leaning_keyboard.row(KeyboardButton('Хочу проверить себя')).row(return_button)

new_words_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
new_words_keyboard.row(KeyboardButton("Уже знаю"), KeyboardButton("Не знаю"))
new_words_keyboard.row(return_button)
