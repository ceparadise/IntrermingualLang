from gensim import corpora, models, matutils

from VSM import VSM
from common import translate_sentences
from model import Model


class TR_VSM(Model):
    def __init__(self, fo_lang_code, trans_agent):
        self.vsm = VSM(fo_lang_code)
        self.trans_agent = trans_agent

    def build_model(self, docs):
        trans_docs = []
        for doc in docs:
            trans_doc = translate_sentences(doc, "en")
            trans_docs.append(trans_doc)
        self.vsm.build_model(docs)

    def get_doc_similarity(self, doc1, doc2):
        en_doc1 = self.trans_agent.get_translated_doc(doc1)
        en_doc2 = self.trans_agent.get_translated_doc(doc2)
        return self.vsm.get_doc_similarity(en_doc1, en_doc2)

    def get_model_name(self):
        return "TR-VSM"
