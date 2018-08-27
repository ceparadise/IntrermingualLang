import os
from time import sleep

from googletrans import Translator

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data')
CLEANED_DATA = os.path.join(DATA_DIR, "cleaned_data")
ALG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'algorithms')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'output')


def translate_sentences(en_sentence, lang_code):
    translator = Translator()
    sleep(1)
    trans_sentence = translator.translate(en_sentence, dest=lang_code).text
    sleep(1)
    return trans_sentence
