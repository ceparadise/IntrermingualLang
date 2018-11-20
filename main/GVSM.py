import math
import os
from gensim import corpora, models, matutils
from gensim.models import KeyedVectors, Word2Vec
from common import DATA_DIR
from Preprocessor import Preprocessor
from model import Model


class GVSM(Model):
    def __init__(self, fo_lang_code):
        super().__init__(fo_lang_code)
        self.tfidf_model = None
        self.word_vec_root = os.path.join(DATA_DIR, "wordVectors")
        self.wv_file_path = os.path.join(self.word_vec_root, "default.wv")
        self.wv: KeyedVectors = None
        if os.path.isfile(self.wv_file_path):
            self.wv: KeyedVectors = KeyedVectors.load(self.wv_file_path, mmap='r')

    def build_model(self, docs):
        print("Building GVSM model...")
        docs_tokens = []
        cnt = 0
        for doc in docs:
            # print(cnt, len(docs))
            cnt += 1
            docs_tokens.append(self.preprocessor.get_tokens(doc, self.fo_lang_code))
        dictionary = corpora.Dictionary(docs_tokens)
        corpus = [dictionary.doc2bow(x) for x in docs_tokens]
        self.tfidf_model = models.TfidfModel(corpus, id2word=dictionary)

        if self.wv is None:
            print("Building WordVectors...")
            self.wv = Word2Vec(docs_tokens)
            self.wv.wv.save(os.path.join(self.word_vec_root, "default.wv"))
        print("Finish building VSM model")

    def _get_doc_similarity(self, doc1_tk, doc2_tk):
        def cal_square_total(weight_vec):
            square_total = 0
            for (id, weight) in weight_vec:
                square_total += weight * weight
            return square_total

        id2token: dict = self.tfidf_model.id2word  # wd id to tokens as a dictionary

        doc1_vec = self.tfidf_model[self.tfidf_model.id2word.doc2bow(doc1_tk)]
        doc2_vec = self.tfidf_model[self.tfidf_model.id2word.doc2bow(doc2_tk)]
        doc1_square_sum = cal_square_total(doc1_vec)
        doc2_square_sum = cal_square_total(doc2_vec)
        sim_score = 0
        for (doc1_token_id, doc1_token_weight) in doc1_vec:
            for (doc2_token_id, doc2_token_weight) in doc2_vec:
                doc1_token = id2token[doc1_token_id]
                doc2_token = id2token[doc2_token_id]
                if doc1_token in self.wv.vocab and doc2_token in self.wv.vocab:
                    term_similarity = self.wv.similarity(doc1_token, doc2_token)
                else:
                    term_similarity = 0
                sim_score += doc1_token_weight * doc2_token_weight * term_similarity
            score = sim_score / (math.sqrt(doc1_square_sum * doc2_square_sum))
        return score

    def get_model_name(self):
        return "GVSM"

    def get_word_weights(self):
        dfs = self.tfidf_model.dfs
        idfs = self.tfidf_model.idfs
        res = []
        for termid in dfs:
            word = self.tfidf_model.id2word[termid]
            idf = idfs.get(termid)
            res.append((word, idf))
        return res


if __name__ == "__main__":
    docs = [
        'this is a test',
        'test assure quality',
        'test is important',
    ]
    vsm = VSM("en")
    vsm.build_model(docs)
    preprocessor = Preprocessor()
    new_doc1 = preprocessor.get_stemmed_tokens("software quality rely on test", "en")
    new_doc2 = preprocessor.get_stemmed_tokens("quality is important", "en")
    new_doc3 = preprocessor.get_stemmed_tokens("i have a pretty dog", "en")
