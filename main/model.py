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

    def _get_doc_similarity(self, doc1, doc2):
        raise NotImplementedError

    def get_model_name(self):
        raise NotImplementedError

    def get_link_scores_with_processed_artifacts(self, candidates):
        """
        Take the artifacts as a list of tokens. candidates are in format of [(s_id,s_content),(t_id,t_content)]
        :return:
        """
        res = []
        for candidate in candidates:
            source_artifact = candidate[0]
            s_id = source_artifact[0]
            s_content = source_artifact[1]

            target_artifact = candidate[1]
            t_id = target_artifact[0]
            t_content = target_artifact[1]

            score = self._get_doc_similarity(s_content.split(), t_content.split())
            res.append((s_id, t_id, score))
        return res

    def get_link_scores(self, source_artifacts, target_artifacts):
        """
        Create links for raw dataset
        :param source_artifacts:
        :param target_artifacts:
        :return:
        """
        links = []
        self.processed_artifacts = dict()
        for s_id in source_artifacts:
            content = source_artifacts[s_id]
            tokens = self.preprocessor.get_tokens(content, self.fo_lang_code)
            self.processed_artifacts[s_id] = tokens
        for t_id in target_artifacts:
            content = target_artifacts[t_id]
            tokens = self.preprocessor.get_tokens(content, self.fo_lang_code)
            self.processed_artifacts[t_id] = tokens

        for s_id in source_artifacts:
            for t_id in target_artifacts:
                s_tokens = self.processed_artifacts[s_id]
                t_tokens = self.processed_artifacts[t_id]
                score = self._get_doc_similarity(s_tokens, t_tokens)
                links.append((s_id, t_id, score))
        return links

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
