import re

import many_stop_words
from nltk.parse.corenlp import CoreNLPParser
from nltk.stem.snowball import SnowballStemmer
from nltk import word_tokenize
from subprocess import Popen, PIPE

from reborn.Preprocessor import Preprocessor


class Model:
    def __init__(self, fo_lang_code):
        # set up stanford nlp java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload
        # tokenize,ssplit,pos,lemma,parse,depparse  -status_port 9000 -port 9000 -timeout 15000 -serverProperties StanfordCoreNLP-
        # chinese.properties
        self.parser = CoreNLPParser()
        self.fo_lang_code = fo_lang_code
        self.preprocessor = Preprocessor()

    def get_doc_similarity(self, doc1, doc2):
        raise NotImplementedError

    def get_model_name(self):
        raise NotImplementedError

    def split_tokens_by_lang(self, tokens):
        lang_dict = {}
        lang_dict['en'] = []
        lang_dict[self.fo_lang_code] = []
        for token in tokens:
            m = re.match("^[a-zA-Z]+$", token)
            if not m:
                lang_dict[self.fo_lang_code].append(token)
            else:
                lang_dict['en'].append(token)
        return lang_dict

    def startStanforNLP(self):
        stanforNLP_server_cmd = " java -mx4g -cp * edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload tokenize,ssplit,pos,lemma,parse,depparse  -status_port 9000 -port 9000 -timeout 15000 -serverProperties StanfordCoreNLP-chinese.properties"
        self.start_server = Popen(stanforNLP_server_cmd.split(), cwd="G:\lib\stanford-corenlp-full-2016-10-31",
                                  stderr=PIPE, stdout=PIPE, shell=True)

        while (True):
            line = str(self.start_server.stderr.readline())
            print(line)
            success_mark = 'StanfordCoreNLPServer listening at'
            except_mark = 'Address already in use'
            if success_mark in line:
                print("server started...")
                break
            elif except_mark in line:
                print("server already started or port occupied...")
                break
        self.start_server.stderr.close()
        self.start_server.stdout.close()


if __name__ == "__main__":
    pass
