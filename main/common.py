import os
from time import sleep

import math
from googletrans import Translator

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data')
CLEANED_DATA = os.path.join(DATA_DIR, "cleaned_data")
ALG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'algorithms')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'output')
GIT_PROJECTS = os.path.join(DATA_DIR, "..", "main", "reborn", "github_project_crawl", "git_projects")


def translate_sentences(en_sentence, lang_code):
    translator = Translator()
    sleep(1)
    trans_sentence = translator.translate(en_sentence, dest=lang_code).text
    sleep(1)
    return trans_sentence


def translate_long_sentence(sentence, partition_size=14000):
    translator = Translator()
    trans_content = []
    for par in range(math.ceil(len(sentence) / partition_size)):
        part = sentence[par * partition_size: (par + 1) * partition_size]
        try:
            sleep(1)
            trans_part = translator.translate(part).text
        except Exception as e:
            print("Exception when translating sentence {}".format(part))
            trans_part = part
        trans_content.append(trans_part)
    return " ".join(trans_content)


def translate_tokens(tk_sentence, translator):
    trans_content = []
    tokens = tk_sentence.split()
    for token in tokens:
        try:
            sleep(1)
            trans_part = translator.translate(token).text
        except Exception as e:
            print("Exception when translating sentence {}".format(token))
            trans_part = token
    trans_content.append(trans_part)
    return " ".join(trans_content)
