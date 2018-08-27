from gensim import matutils
from googletrans import Translator

from LDA import LDA

from common import translate_sentences


class TR_LDA:
    def __init__(self, fo_lang_code, trans_agent):
        self.lda = LDA(fo_lang_code)
        self.trans_agent = trans_agent

    def train(self, docs, num_topics=5, passes=100):
        # docs = [doc.split() for doc in docs]
        trans_docs = []
        for doc in docs:
            trans_doc = translate_sentences(doc, "en")
            trans_docs.append(trans_doc)
        self.lda.train(trans_docs, num_topics=num_topics, passes=passes)

    def get_doc_similarity(self, doc1, doc2):
        en_doc1 = self.trans_agent.get_translated_doc(doc1)
        en_doc2 = self.trans_agent.get_translated_doc(doc2)
        return self.lda.get_doc_similarity(en_doc1, en_doc2)

    def get_model_name(self):
        return "TR-LDA"
