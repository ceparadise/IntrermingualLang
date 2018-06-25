import re

import many_stop_words
from nltk import StanfordSegmenter
from langdetect import detect


class Model:
    def __init__(self, fo_lang_code):
        self.seg = StanfordSegmenter()
        self.seg.default_config('zh')
        self.fo_lang_code = fo_lang_code

    def get_tokens(self, doc_str):
        tokens = []
        if self.fo_lang_code == "zh":
            print("segmenting Chinese...")
            zh, en = self.segment(doc_str)
            tokens.extend(zh)
            tokens.extend(en)
        else:
            tokens.extend(doc_str.split())
        return tokens

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

    def get_doc_similarity(self, doc1, doc2):
        raise NotImplementedError

    def get_model_name(self):
        raise NotImplementedError

    def split_tokens_by_lang(self, tokens):
        lang_dict = {}
        lang_dict['en'] = []
        lang_dict[self.fo_lang_code] = []
        for token in tokens:
            try:
                detectedLangCode = detect(token)
                if detectedLangCode == self.fo_lang_code:
                    lang_dict[detectedLangCode].append(token)
                else:
                    lang_dict['en'].append(token)
            except Exception:
                pass

        return lang_dict

    def clean_doc(self, doc_str):
        doc_str = re.sub("(\d+|[^\w]+)", " ", doc_str, flags=re.UNICODE)
        return doc_str


if __name__ == "__main__":
    dummy = Model("en")
    print(dummy.split_tokens_by_lang("The latter by the Laboratory of application shall".split()))
    test_clean_doc1 = ",./你好，世界-=+asd8987"
    print(dummy.clean_doc(test_clean_doc1))

