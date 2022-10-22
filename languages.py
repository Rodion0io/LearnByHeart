import pandas as pd
from random import choice

en = list(pd.read_csv("oxford_3000.csv").values)
fr = list(pd.read_csv("french.csv").values)
de = list(pd.read_csv("german.csv").values)


def get_word(language: str):
    if language == 'Английский':
        return choice(en)[:-1]
    elif language == 'Французский':
        return choice(fr)
    elif language == "Немецкий":
        return choice(de)[-1::-1]
    else:
        return 42

print(get_word("Английский"), get_word("Немецкий"), get_word("Французский"))
