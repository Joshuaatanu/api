import math
import pandas as pd
import numpy as np


def translate_model(english_text):
    data = pd.read_csv('clean_2.csv')

    # use apply function to turn all the words to lower case

    def lower_case_words(word):
        return word.strip().lower()

    def remove_spaces(word):
        return word.strip()

    data['English'] = data['English'].apply(lower_case_words)
    data['Igala'] = data['Igala'].apply(remove_spaces)

    english_to_igala = data.set_index('English')['Igala'].to_dict()
    igala_to_english = {v: k for k, v in english_to_igala.items()}

    def translate(text, dictionary):
        words = text.lower().split()
        print(words)
        translated_words = [dictionary.get(word, word) for word in words]
        return ' '.join(translated_words)

    def translate_english_to_igala(text):
        return translate(text, english_to_igala)

    def translate_igala_to_english(text):
        return translate(text, igala_to_english)

    translated_text = translate_english_to_igala(english_text)

    return translated_text
