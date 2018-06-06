import gensim
from gensim import corpora


class LSI:
    def __init__(self):
        pass

if __name__ == "__main__":
    text = "this is a test sentence which i will use for LSI"
    text = [text.split()]
    dictionary = corpora.Dictionary(text)
    corpus = [dictionary.doc2bow(x) for x in text]
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=5, id2word=dictionary, passes=20)
    ldamodel.get_topics()
    print(ldamodel[corpus])
