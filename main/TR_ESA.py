from ESA import ESA
from common import translate_sentences
import os


class TR_ESA:
    def __init__(self, fo_lang_code, trans_agent):
        """

        :param fo_lang_code:
        :param trans_cache_path: cache file which store the translation result
        """
        self.esa = ESA(fo_lang_code)
        self.trans_docs = dict()
        self.trans_agent = trans_agent

    def build(self, en_wiki, rebuild_en=False):
        self.esa.build(en_wiki, rebuild_en=rebuild_en)

    def get_doc_similarity(self, doc1, doc2):
        en_doc1 = self.trans_agent.get_translated_doc(doc1)
        en_doc2 = self.trans_agent.get_translated_doc(doc2)
        return self.esa.get_doc_similarity(en_doc1, en_doc2)

    def get_model_name(self):
        return "TR-ESA"
