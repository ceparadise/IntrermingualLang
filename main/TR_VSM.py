from gensim import corpora, models, matutils

from VSM import VSM
from common import translate_sentences, translate_long_sentence
from model import Model


class TR_VSM(Model):
    def __init__(self, fo_lang_code):
        self.vsm = VSM(fo_lang_code)
        self.trans_dict = dict()

    def build_model(self, docs):
        trans_docs = []
        for doc in docs:
            trans_doc = translate_long_sentence(doc)
            trans_docs.append(trans_doc)
            self.trans_dict[doc] = trans_doc
        self.vsm.build_model(trans_docs)

    def get_doc_similarity(self, doc1, doc2):
        en_doc1 = self.trans_dict[doc1]
        en_doc2 = self.trans_dict[doc2]
        return self.vsm._get_doc_similarity(en_doc1, en_doc2)

    def get_model_name(self):
        return "TR-VSM"
