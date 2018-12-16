import math
import os, io
from gensim import corpora, models, matutils
from gensim.models import KeyedVectors, Word2Vec
from common import DATA_DIR
from Preprocessor import Preprocessor
from model import Model
from hanziconv import HanziConv

GENESIM_W2V = "gensim_w2v"
CROSSLINGUAL_WORDEMBEDDING = "cross_lingual_word_embedding"


class GVSM(Model):
    def __init__(self, fo_lang_code, term_similarity_type):
        super().__init__(fo_lang_code)
        self.tfidf_model = None
        self.word_vec_root = os.path.join(DATA_DIR, "wordVectors")
        self.wv_file_path = os.path.join(self.word_vec_root, "default.wv")
        self.wv: KeyedVectors = None
        self.cl_wv = None
        self.term_similarity_type = term_similarity_type
        if os.path.isfile(self.wv_file_path) and term_similarity_type == GENESIM_W2V:
            self.wv: KeyedVectors = KeyedVectors.load(self.wv_file_path, mmap='r')
        self.term_similarity_cache = dict()

    def load_vectors(self, fname):
        """
        Return word embedding vectors as map
        :return:
        """
        data = {}
        with open(fname, 'r', encoding='utf-8') as fin:
            n, d = map(int, fin.readline().split())
            print("vector #:{} vector dimension:{}".format(n, d))
            for line in fin:
                tokens = line.rstrip().split()
                term = tokens[0]
                if self.fo_lang_code == 'en' or self.fo_lang_code == "zh":
                    term = HanziConv.toSimplified(term)  # conver to simpified Chinese
                data[term] = [float(x) for x in tokens[1:]]
        return data

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

        if self.wv is None and self.term_similarity_type == GENESIM_W2V:
            print("Building Gensim WordVectors on current dataset...")
            self.wv = Word2Vec(docs_tokens)
            self.wv.wv.save(os.path.join(self.word_vec_root, "default.wv"))

        if self.cl_wv is None and self.term_similarity_type == CROSSLINGUAL_WORDEMBEDDING:
            print("Building bilingual word embedding ...")
            vec_file_path = os.path.join(self.word_vec_root, "wiki.zh.align.vec")
            self.cl_wv = self.load_vectors(vec_file_path)
        print("Finish building GVSM model")

    def __get_term_similarity(self, token1, token2):
        term_similarity = 0
        term_pair = (token1, token2)
        if (token1, token2) in self.term_similarity_cache:
            return self.term_similarity_cache[term_pair]
        else:
            if self.term_similarity_type == GENESIM_W2V:
                if token1 in self.wv.vocab and token2 in self.wv.vocab:
                    term_similarity = self.wv.similarity(token1, token2)
            elif self.term_similarity_type == CROSSLINGUAL_WORDEMBEDDING:
                if token1 in self.cl_wv and token2 in self.cl_wv:
                    vec1 = self.cl_wv[token1]
                    vec2 = self.cl_wv[token2]
                    if len(vec1) == 0 or len(vec2) == 0:
                        print(vec1)
                        print(vec2)
                    term_similarity = self.cosine_similarity(vec1, vec2)
            self.term_similarity_cache[term_pair] = term_similarity
        return term_similarity

    def _get_doc_similarity(self, doc1_tk, doc2_tk):
        def remove_low_weight(x: dict, threshold=0.001):
            return {key: value for key, value in x.items() if x[key] > threshold}

        id2token: dict = self.tfidf_model.id2word  # wd id to tokens as a dictionary

        doc1_vec = self.tfidf_model[self.tfidf_model.id2word.doc2bow(doc1_tk)]
        doc2_vec = self.tfidf_model[self.tfidf_model.id2word.doc2bow(doc2_tk)]

        doc1_dict = dict(doc1_vec)
        doc2_dict = dict(doc2_vec)

        doc1_dict = remove_low_weight(doc1_dict)
        doc2_dict = remove_low_weight(doc2_dict)

        token_ids = set()
        token_ids.update(doc2_dict)
        token_ids.update(doc1_dict)
        token_ids = list(token_ids)
        sim_score = 0
        doc1_square_sum = 0
        doc2_square_sum = 0
        for i in range(len(token_ids)):
            id_i = token_ids[i]
            tk_i = id2token[id_i]
            tfidf_i_doc1 = doc1_dict.get(id_i, 0)
            tfidf_i_doc2 = doc2_dict.get(id_i, 0)
            for j in range(i + 1, len(token_ids)):
                id_j = token_ids[j]
                tk_j = id2token[id_j]
                tfidf_j_doc1 = doc1_dict.get(id_j, 0)
                tfidf_j_doc2 = doc2_dict.get(id_j, 0)
                term_similarity = self.__get_term_similarity(tk_i, tk_j)
                doc1_weight = (tfidf_i_doc1 + tfidf_j_doc1) * term_similarity
                doc2_weight = (tfidf_i_doc2 + tfidf_j_doc2) * term_similarity
                sim_score += doc1_weight * doc2_weight
                doc1_square_sum += doc1_weight ** 2
                doc2_square_sum += doc2_weight ** 2
        score = sim_score / (doc1_square_sum ** 0.5 + doc2_square_sum ** 0.5)
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
