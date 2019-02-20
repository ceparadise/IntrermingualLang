import os
from time import sleep

import math
from google.cloud import translate
import re
from PyDictionary import PyDictionary

dictionary = PyDictionary()

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data')
CLEANED_DATA = os.path.join(DATA_DIR, "cleaned_data")
ALG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'algorithms')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'output')
GIT_PROJECTS = os.path.join(DATA_DIR, "..", "main", "reborn", "github_project_crawl", "git_projects")

CHINESE_CHAR_PATTERN = re.compile("[\u4e00-\u9fff]+")

# franch german turkish swedish Slovak Russian Hungarian italian
# language_list = ["fr", "de", "tr", "sv", "sk", "ru", "hu", "it"]
language_list = ["de", "tr", "sv", "sk", "ru", "hu", "it"]

try:
    translator = translate.Client()
except Exception as e:
    print(e)


def translate_sentences(en_sentence, lang_code):
    sleep(1)
    trans_sentence = translator.translate(en_sentence, target_language=lang_code)["translatedText"]
    sleep(1)
    return trans_sentence


def translate_long_sentence(sentence, lang="en", partition_size=14000):
    """
    Translate a long sentence into English.
    :param sentence:
    :param partition_size:
    :return:
    """
    trans_content = []
    for par in range(math.ceil(len(sentence) / partition_size)):
        part = sentence[par * partition_size: (par + 1) * partition_size]
        try:
            trans_part = translator.translate(part, target_language=lang)["translatedText"]
        except Exception as e:
            sleep(3)
            print("Exception when translating sentence {}, exception is {}".format(part, e))
            trans_part = part
        trans_content.append(trans_part)
    return " ".join(trans_content)


def translate_tokens(tk_sentence, target_language="en"):
    trans_content = []
    tokens = tk_sentence.split()
    for token in tokens:
        try:
            trans_part = str(dictionary.translate(token, target_language))
        except Exception as e:
            print("Exception when translating token {}".format(token))
            trans_part = token
    trans_content.append(trans_part)
    return " ".join(trans_content)


def sentence_contains_chinese(sentence: str) -> bool:
    return CHINESE_CHAR_PATTERN.search(sentence) is not None


def translate_intermingual_sentence(sentence: str, lang="en") -> str:
    """
    Find out the Chinese sentences in a long string, translate those parts and return a pure english version sentence
    of the input
    :param sentence:
    :return:
    """
    sentence_segments_by_space = sentence.split()
    translated_sentence = []
    for sentence_segment in sentence_segments_by_space:
        if sentence_contains_chinese(sentence_segment):
            sentence_segment = re.sub("[^\w]+", " ", sentence_segment)
            trans_segment = translate_long_sentence(sentence_segment, lang=lang)
        else:
            trans_segment = sentence_segment
        translated_sentence.append(trans_segment)
    return " ".join(translated_sentence)
