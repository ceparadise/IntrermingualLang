import re

import many_stop_words
from nltk import StanfordSegmenter


class Model:
    def __init__(self):
        self.seg = StanfordSegmenter()
        self.seg.default_config('zh')

    def segment(self, doc):
        seg_str = self.seg.segment(doc)
        ch_token = self.get_zh(seg_str)
        en_token = self.get_en(doc)
        return ch_token, en_token

    def get_zh(self, doc):
        pattern = re.compile("[\u4e00-\u9fff]+")
        res = pattern.findall(doc)
        return res

    def get_en(self, doc):
        pattern = re.compile("[a-zA-Z]+")
        res = pattern.findall(doc)
        return res;

    def clean_tokens(self, token_list, lang="en"):
        cleaned = []
        stop_words = many_stop_words.get_stop_words(lang)
        for token in token_list:
            token = token.lower()
            if token not in stop_words:
                cleaned.append(token)
        return cleaned
