import re
import subprocess, os

from gensim import corpora
from nltk.tokenize.stanford_segmenter import StanfordSegmenter
import many_stop_words
import shutil
import gensim

from common import ALG_DIR
from model import Model


class CL_LDA(Model):
    def __init__(self, corpus_name, fo_lang_code):
        super().__init__(fo_lang_code)
        self.working_dir = os.path.join(ALG_DIR, 'Cross-Lingual-Topic-Model-master/src/train')
        self.input_dir_path = os.path.join(self.working_dir, "../../input/")
        self.corpus_name = corpus_name

        self.fo_train_dir = os.path.join(self.input_dir_path, "_".join([self.corpus_name, fo_lang_code, "train"]))
        self.fo_test_dir = os.path.join(self.input_dir_path, "_".join([self.corpus_name, fo_lang_code, "test"]))
        self.en_train_dir = os.path.join(self.input_dir_path, "_".join([self.corpus_name, "en", "train"]))
        self.en_test_dir = os.path.join(self.input_dir_path, "_".join([self.corpus_name, "en", "test"]))
        self.train_output_dir = os.path.join(self.working_dir, "../../train_output/")

        self.fo_train_dat = os.path.join(self.fo_train_dir, "train.dat")
        self.en_train_dat = os.path.join(self.en_train_dir, "train.dat")
        self.fo_test_dat = os.path.join(self.fo_test_dir, "test.dat")
        self.en_test_dat = os.path.join(self.en_test_dir, "test.dat")
        self.fo_train_vocab = os.path.join(self.fo_train_dir, "voc.dat")
        self.en_train_vocab = os.path.join(self.en_train_dir, "voc.dat")

        self.tfidf = None
        self.dictionary = None
        self.fo_topics = None
        self.en_topics = None

    def get_tfidf_model(self):
        docs = []
        with open(self.fo_train_dat, encoding='utf8') as fo_in, open(self.en_train_dat, encoding='utf8') as en_in:
            fo_docs = fo_in.readlines()
            en_docs = en_in.readlines()
            for doc in fo_docs:
                docs.append([x for x in doc.split()])
            for doc in en_docs:
                docs.append([x for x in doc.split()])
            dictionary = corpora.Dictionary(docs)
            corpus = [dictionary.doc2bow(x) for x in docs]
            self.tfidf = gensim.models.TfidfModel(corpus)
            self.dictionary = dictionary

    def train_CL_LSA(self, topic_num=10, iteration_num=100, lambda_val=0.5, alpha_val=0.5, alph_beta=0.01):
        train_command = "python -m lda.launch_train --en_input_directory={} " \
                        "--ch_input_directory={} --output_directory={} " \
                        "--corpus_name={} --number_of_topics_ge={} --training_iterations={} --lamda={} --alpha_alpha={} --alpha_beta={}".format(
            self.en_train_dir, self.fo_train_dir, self.train_output_dir, self.corpus_name, topic_num, iteration_num,
            lambda_val, alpha_val, alph_beta)
        train_process = subprocess.Popen(train_command, cwd=self.working_dir)
        train_process.wait()
        self.get_topics()

    def __get_trian_number(self, train_output_file_name):
        if '-' not in train_output_file_name:
            return -1
        postfix = train_output_file_name.split('-')[1]
        num, lang = postfix.split('_')
        return int(num)

    def __parse_topics_file(self, topic_file_path):
        topic = dict()
        cnt = -1
        with open(topic_file_path) as fin:
            lines = fin.readlines()
            for line in lines:
                if line.startswith("==="):
                    cnt += 1
                    topic[cnt] = []
                else:
                    parts = [x.strip("\n") for x in line.split("\t") if len(x) > 0]
                    word = parts[0]
                    weight = (float)(parts[1])
                    topic[cnt].append((word, weight))
        return topic

    def get_topics(self):
        if self.en_topics == None or self.fo_topics == None:
            train_output = os.path.join(self.train_output_dir, self.corpus_name)
            all_subdirs = [os.path.join(train_output, x) for x in os.listdir(train_output)]
            latest_subdir = max(all_subdirs, key=os.path.getmtime)
            files = os.listdir(latest_subdir)
            max_train_num = max([self.__get_trian_number(x) for x in files])
            fo_topics_file = os.path.join(latest_subdir, "exp_beta-{}_cn".format(max_train_num))
            en_topics_file = os.path.join(latest_subdir, "exp_beta-{}_en".format(max_train_num))
            self.fo_topics = self.__parse_topics_file(fo_topics_file)
            self.en_topics = self.__parse_topics_file(en_topics_file)
        return self.fo_topics, self.en_topics

    def test_CL_LSA(self, doc, project_name, bi_lang_dict="./ch_en_dict.dat"):
        working_dir = 'G:/Projects/InterLingualTrace/algorithms/Cross-Lingual-Topic-Model-master/src/test'
        input_dir_path = os.path.join(working_dir, "../../input/")
        fo_test = "_".join([project_name, self.fo_lang_code, "test"])
        en_test = "_".join([project_name, "en", "test"])
        fo_input_dir = os.path.join(input_dir_path, fo_test)
        en_input_dir = os.path.join(input_dir_path, en_test)

        corpus_name = project_name
        model_path = os.path.join(working_dir, "../../model/{}/CrossLDA_ge10_lamda0.5".format(corpus_name))
        output_dir = os.path.join(working_dir, "../../test_output")
        test_command = "python -m model_test --test_en_input={} " \
                       "--test_cn_input={} " \
                       "--dict_input={}  --model_path={} " \
                       "--corpus_name={} --test_iterations=1 --output_directory={}".format(en_input_dir,
                                                                                           fo_input_dir,
                                                                                           bi_lang_dict,
                                                                                           model_path, corpus_name,
                                                                                           output_dir)
        test_process = subprocess.Popen(test_command, cwd=working_dir)
        test_process.wait()

        # Read topics and return as a list
        corpus_dir = os.path.join(output_dir, corpus_name)
        res_dirs = os.listdir(corpus_dir)
        if len(res_dirs) != 1:
            raise Exception("Incorrect number of folds in {}".format(corpus_dir))

        res_dir = os.path.join(corpus_dir, res_dirs[0])
        topic_dir = os.path.join(res_dir, "topics")
        topic_file = os.listdir(topic_dir)[0]

        file_path = os.path.join(topic_dir, topic_file)
        with open(file_path) as topic_file:
            topics_doc = topic_file.read()
        fo_topics, en_topics = self.segment(topics_doc)
        shutil.rmtree(res_dir)  # clear the directory every time
        return set(fo_topics), set(en_topics)

    def to_CL_LAS_data_files(self, docs):
        """
        Convert a percent dict to CLLSA usaable data
        :return:
        """

        fo_vocab = set()
        en_vocab = set()

        if not os.path.exists(self.fo_train_dir):
            os.mkdir(self.fo_train_dir)
        if not os.path.exists(self.fo_test_dir):
            os.mkdir(self.fo_test_dir)
        if not os.path.exists(self.en_train_dir):
            os.mkdir(self.en_train_dir)
        if not os.path.exists(self.en_test_dir):
            os.mkdir(self.en_test_dir)

        if os.path.exists(self.fo_train_dat) and os.path.exists(self.en_train_dat) and os.path.exists(
                self.fo_test_dat) and os.path.exists(self.en_test_dat) and os.path.exists(
            self.fo_train_vocab) and os.path.exists(
            self.en_train_vocab):
            print("All file ready, skip writing")
            return

        with open(self.fo_train_dat, "w", encoding='utf8') as fo_train, \
                open(self.en_train_dat, "w", encoding='utf8') as en_train, \
                open(self.fo_test_dat, "w", encoding='utf8') as fo_test, \
                open(self.en_test_dat, "w", encoding='utf8') as en_test:

            for doc in docs:
                fo_tokens, en_tokens = self.segment(doc)
                fo_doc = " ".join(fo_tokens)
                en_doc = " ".join(en_tokens)

                fo_train.write(fo_doc + "\n")
                en_train.write(en_doc + "\n")
                fo_test.write(fo_doc + "\n")
                en_test.write(en_doc + "\n")

                for fo_token in fo_tokens:
                    fo_vocab.add(fo_token)
                for en_token in en_tokens:
                    en_vocab.add(en_token)

        with open(self.fo_train_vocab, 'w', encoding="utf8") as fo_vocab_output, open(self.en_train_vocab, 'w',
                                                                                      encoding='utf8') as en_vocab_output:
            for tk in fo_vocab:
                fo_vocab_output.write(tk + "\n")
            for tk in en_vocab:
                en_vocab_output.write(tk + "\n")

    def get_topic_distrib(self, doc, topics):
        # TODO Try another algorithms to get the topic distribution
        distrib = []
        for topic_id in topics:
            words_weights = topics[topic_id]
            topic_vec = []
            # Replace keyword with id
            for word, weight in words_weights:
                w_id = self.dictionary.token2id[word]
                topic_vec.append((w_id, weight))

            bow = self.dictionary.doc2bow(doc)
            tfidf_vec = self.tfidf[bow]
            sim = gensim.matutils.cossim(tfidf_vec, topic_vec)
            if sim > 0:
                distrib.append((topic_id, sim))
        return distrib

    def get_doc_similarity(self, doc1, doc2):
        doc1_tk = self.get_tokens(doc1)
        doc2_tk = self.get_tokens(doc2)
        self.get_topics()
        d1_fo_topic_distrib = self.get_topic_distrib(doc1_tk, self.fo_topics)
        d2_fo_topic_distrib = self.get_topic_distrib(doc2_tk, self.fo_topics)
        d1_en_topic_distrib = self.get_topic_distrib(doc1_tk, self.en_topics)
        d2_en_topic_distrib = self.get_topic_distrib(doc2_tk, self.en_topics)
        # cn_sim = gensim.matutils.cossim(d1_cn_topic_distrib, d2_cn_topic_distrib)
        # en_sim = gensim.matutils.cossim(d1_en_topic_distrib, d2_en_topic_distrib)
        # #return (cn_sim + en_sim) / 2
        d1_fo_topic_distrib.extend(d1_en_topic_distrib)
        d2_fo_topic_distrib.extend(d2_en_topic_distrib)
        return gensim.matutils.cossim(d1_fo_topic_distrib, d2_fo_topic_distrib)

    def get_model_name(self):
        return "CL_LDA"


if __name__ == "__main__":
    pass
