import gensim
from gensim import corpora, matutils

from model import Model


class LDA(Model):
    def __init__(self, fo_lang_code):
        super().__init__(fo_lang_code)
        self.ldamodel = None

    def train(self, docs, num_topics=5, passes=100):
        # docs = [doc.split() for doc in docs]
        clean_docs = []
        for doc in docs:
            tmp = []
            zh, en = self.segment(doc)
            tmp.extend(zh)
            tmp.extend(en)
            clean_docs.append(tmp)
        dictionary = corpora.Dictionary(clean_docs)
        corpus = [dictionary.doc2bow(x) for x in clean_docs]
        self.ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=num_topics, id2word=dictionary,
                                                        passes=passes)

    def get_topic_distrb(self, doc):
        bow_doc = self.ldamodel.id2word.doc2bow(doc)
        return self.ldamodel.get_document_topics(bow_doc)

    def get_doc_similarity(self, doc1, doc2):
        doc1_tk = self.get_tokens(doc1)
        doc2_tk = self.get_tokens(doc2)
        dis1 = self.get_topic_distrb(doc1_tk)
        dis2 = self.get_topic_distrb(doc2_tk)
        return 1 - matutils.hellinger(dis1, dis2)

    def get_model_name(self):
        return "LDA"


if __name__ == "__main__":
    docs = [
        ['this', 'is', 'a', 'test'],
        ['test', 'assure', 'quality'],
        ['test', 'is', 'important'],

    ]
    lda = LDA()
    new_doc1 = ["software", 'quality', 'rely', 'test']
    new_doc2 = ["quality", "is", "important"]
    new_doc3 = ["i", "have", "a", "pretty", "dog"]
    lda.train(docs)
    dis1 = lda.get_topic_distrb(new_doc1)
    dis2 = lda.get_topic_distrb(new_doc2)
    dis3 = lda.get_topic_distrb(new_doc3)
    print(dis1)
    print(dis2)
    print(dis3)
    print(matutils.hellinger(dis1, dis2))
    print(matutils.hellinger(dis1, dis3))