import re

import many_stop_words
import nltk


class Preprocessor():
    def __init__(self):
        self.parser = nltk.CoreNLPParser()
        self.java_keywords = set([w.strip('*') for w in """
        abstract    continue    for     new     switch
        assert   default     goto*   package     synchronized
        boolean     do  if  private     this
        break   double  implements  protected   throw
        byte    else    import  public  throws
        case    enum****    instanceof  return  transient
        catch   extends     int     short   try
        char    final   interface   static  void
        class   finally     long    strictfp**  volatile
        const*  float   native  super   while
        """.split()])

    def get_stemmer(self, lang_code):
        "danish dutch english finnish french german hungarian italian norwegian porter portuguese romanian russian spanish swedish"
        if lang_code == "en":
            return nltk.SnowballStemmer("english")
        elif lang_code == "fr":
            return nltk.SnowballStemmer("french")
        elif lang_code == "ge":
            return nltk.SnowballStemmer("german")
        elif lang_code == 'it':
            return nltk.SnowballStemmer("italian")
        else:
            return None

    def get_zh(self, doc):
        pattern = re.compile("[\u4e00-\u9fff]+")
        res = pattern.findall(doc)
        return res

    def get_en(self, doc):
        pattern = re.compile("[a-zA-Z]+")
        res = pattern.findall(doc)
        return res

    def __clean_doc(self, doc_str):
        doc_str = re.sub("(\d+|[^\w]+)", " ", doc_str, flags=re.UNICODE)
        return doc_str

    def remove_java_keyword(self, tokens):
        return [x for x in tokens if x not in self.java_keywords]

    def get_tokens(self, doc, language="en"):
        tokens = []
        doc = self.__clean_doc(doc)
        if language == "zh":  # maybe a mixture of en and zh
            seg_str = " ".join(self.parser.tokenize(doc))
            ch_token = self.get_zh(seg_str)
            en_token = self.get_en(doc)
            res = []
            res.extend(ch_token)
            res.extend(en_token)
        else:
            res = nltk.word_tokenize(doc)
        for wd in res:
            tokens.extend(self.split_camal_case(wd))
        tokens = [x.lower() for x in tokens]
        tokens = self.remove_java_keyword(tokens)
        tokens = self.remove_stop_word(tokens, language=language)
        return tokens

    def get_stemmed_tokens(self, doc_str, language="en"):
        en_stemmer = self.get_stemmer("en")
        fo_stemmer = self.get_stemmer(language)

        tokens = self.get_tokens(doc_str, language)
        tokens = [en_stemmer.stem(x) for x in tokens]
        tokens = [fo_stemmer.stem(x) for x in tokens]
        return tokens

    def remove_stop_word(self, token_list, language="en"):
        stop_words = many_stop_words.get_stop_words(language)
        return [x for x in token_list if x not in stop_words]

    def split_camal_case(self, phrase):
        """
        Should not contain whitespace
        :param phrase: phrase in camalcase
        :return:
        """
        matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', phrase)
        return [m.group(0) for m in matches]


if __name__ == "__main__":
    test_str = "this is a sentence contains CamalCase word HTTPRequest"
    test_str2 = "HTTPRequest"
    test_str3 = "this is sentece for 中英文混杂的句子，不知道可不可以合理地split出来"
    pre = Preprocessor()
    print(pre.get_tokens(test_str))
    print(pre.split_camal_case(test_str2))
    print(pre.get_tokens(test_str3, language="zh"))
