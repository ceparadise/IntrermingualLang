import re

import many_stop_words
from nltk.parse.corenlp import CoreNLPParser
from langdetect import detect
from nltk.stem.snowball import SnowballStemmer


class Model:
    def __init__(self, fo_lang_code):
        # set up stanford nlp java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload
        # tokenize,ssplit,pos,lemma,parse,depparse  -status_port 9000 -port 9000 -timeout 15000 -serverProperties StanfordCoreNLP-
        # chinese.properties
        self.parser = CoreNLPParser()
        self.fo_lang_code = fo_lang_code
        self.en_stemmer = self.get_stemmer("en")
        self.fo_stemmer = self.get_stemmer(self.fo_lang_code)

    def get_stemmer(self, lang_code):
        "danish dutch english finnish french german hungarian italian norwegian porter portuguese romanian russian spanish swedish"
        if lang_code == "en":
            return SnowballStemmer("english")
        elif lang_code == "fr":
            return SnowballStemmer("french")
        elif lang_code == "ge":
            return SnowballStemmer("german")
        elif lang_code == 'it':
            return SnowballStemmer("italian")
        else:
            return None

    def get_tokens(self, doc_str):
        doc_str = self.__clean_doc(doc_str)
        tokens = []
        if self.fo_lang_code == "zh":
            zh, en = self.segment(doc_str)
            tokens.extend(zh)
            tokens.extend(en)
        else:
            tokens.extend(doc_str.split())
        # lang_dict = self.split_tokens_by_lang(tokens)
        # clean the tokens by removing stopwords and short tokens
        # en_tokens = self.__clean_tokens(lang_dict["en"], 'en')
        # fo_tokens = self.__clean_tokens(lang_dict[self.fo_lang_code], self.fo_lang_code)
        # Stem the tokens
        # en_tokens = [self.en_stemmer.stem(x) for x in en_tokens]
        # if self.fo_stemmer is not None:
        #     fo_tokens = [self.fo_stemmer.stem(x) for x in fo_tokens]
        # final_tokens = []
        # final_tokens.append(en)
        # tokens = [self.en_stemmer.stem(x) for x in self.__clean_tokens(tokens, "en")]
        tokens = self.__clean_tokens(tokens, "en")
        tokens = self.__clean_tokens(tokens, self.fo_lang_code)
        tokens = [self.en_stemmer.stem(x) for x in tokens]
        return tokens

    def segment(self, doc):
        seg_str = " ".join(self.parser.tokenize(doc))
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

    def __clean_tokens(self, token_list, language):
        cleaned = []
        stop_words = many_stop_words.get_stop_words(language)
        for token in token_list:
            token = token.lower()
            if token not in stop_words and len(token) >= 2:
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

    def __clean_doc(self, doc_str):
        doc_str = re.sub("(\d+|[^\w]+)", " ", doc_str, flags=re.UNICODE)
        doc_str = doc_str.lower()
        return doc_str


if __name__ == "__main__":
    dummy = Model("en")
    print(dummy.split_tokens_by_lang("The latter by the Laboratory of application shall".split()))
    test_clean_doc1 = ",./你好，世界-=+asd8987"
    print(dummy.clean_doc(test_clean_doc1))
