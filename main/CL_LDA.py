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

        self.cn_train_dir = os.path.join(self.input_dir_path, "_".join([self.corpus_name, "cn", "train"]))
        self.cn_test_dir = os.path.join(self.input_dir_path, "_".join([self.corpus_name, "cn", "test"]))
        self.en_train_dir = os.path.join(self.input_dir_path, "_".join([self.corpus_name, "en", "train"]))
        self.en_test_dir = os.path.join(self.input_dir_path, "_".join([self.corpus_name, "en", "test"]))
        self.train_output_dir = os.path.join(self.working_dir, "../../train_output/")

        self.cn_train_dat = os.path.join(self.cn_train_dir, "train.dat")
        self.en_train_dat = os.path.join(self.en_train_dir, "train.dat")
        self.cn_test_dat = os.path.join(self.cn_test_dir, "test.dat")
        self.en_test_dat = os.path.join(self.en_test_dir, "test.dat")
        self.cn_train_vocab = os.path.join(self.cn_train_dir, "voc.dat")
        self.en_train_vocab = os.path.join(self.en_train_dir, "voc.dat")

        self.tfidf = None
        self.dictionary = None
        self.cn_topics = None
        self.en_topics = None

    def get_tfidf_model(self):
        docs = []
        with open(self.cn_train_dat, encoding='utf8') as cn_in, open(self.en_train_dat, encoding='utf8') as en_in:
            cn_docs = cn_in.readlines()
            en_docs = en_in.readlines()
            for doc in cn_docs:
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
            self.en_train_dir, self.cn_train_dir, self.train_output_dir, self.corpus_name, topic_num, iteration_num,
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
        if self.en_topics == None or self.cn_topics == None:
            train_output = os.path.join(self.train_output_dir, self.corpus_name)
            all_subdirs = [os.path.join(train_output, x) for x in os.listdir(train_output)]
            latest_subdir = max(all_subdirs, key=os.path.getmtime)
            files = os.listdir(latest_subdir)
            max_train_num = max([self.__get_trian_number(x) for x in files])
            cn_topics_file = os.path.join(latest_subdir, "exp_beta-{}_cn".format(max_train_num))
            en_topics_file = os.path.join(latest_subdir, "exp_beta-{}_en".format(max_train_num))
            self.cn_topics = self.__parse_topics_file(cn_topics_file)
            self.en_topics = self.__parse_topics_file(en_topics_file)
        return self.cn_topics, self.en_topics

    def test_CL_LSA(self, doc, project_name):
        working_dir = 'G:/Projects/InterLingualTrace/algorithms/Cross-Lingual-Topic-Model-master/src/test'
        input_dir_path = os.path.join(working_dir, "../../input/")
        cn_test = "_".join([project_name, "cn", "test"])
        en_test = "_".join([project_name, "en", "test"])
        cn_input_dir = os.path.join(input_dir_path, cn_test)
        en_input_dir = os.path.join(input_dir_path, en_test)

        corpus_name = project_name
        model_path = os.path.join(working_dir, "../../model/{}/CrossLDA_ge10_lamda0.5".format(corpus_name))
        output_dir = os.path.join(working_dir, "../../test_output")
        test_command = "python -m model_test --test_en_input={} " \
                       "--test_cn_input={} " \
                       "--dict_input=./ch_en_dict.dat  --model_path={} " \
                       "--corpus_name={} --test_iterations=1 --output_directory={}".format(en_input_dir,
                                                                                           cn_input_dir,
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
        cn_topics, en_topics = self.segment(topics_doc)
        shutil.rmtree(res_dir)  # clear the directory every time
        return set(cn_topics), set(en_topics)

    def clean_tokens(self, token_list, lang="en"):
        cleaned = []
        stop_words = many_stop_words.get_stop_words(lang)
        for token in token_list:
            token = token.lower()
            if token not in stop_words:
                cleaned.append(token)
        return cleaned

    def to_CL_LAS_data_files(self, docs):
        """
        Convert a percent dict to CLLSA usaable data
        :return:
        """

        cn_vocab = set()
        en_vocab = set()

        if not os.path.exists(self.cn_train_dir):
            os.mkdir(self.cn_train_dir)
        if not os.path.exists(self.cn_test_dir):
            os.mkdir(self.cn_test_dir)
        if not os.path.exists(self.en_train_dir):
            os.mkdir(self.en_train_dir)
        if not os.path.exists(self.en_test_dir):
            os.mkdir(self.en_test_dir)

        if os.path.exists(self.cn_train_dat) and os.path.exists(self.en_train_dat) and os.path.exists(
                self.cn_test_dat) and os.path.exists(self.en_test_dat) and os.path.exists(
            self.cn_train_vocab) and os.path.exists(
            self.en_train_vocab):
            print("All file ready, skip writing")
            return

        with open(self.cn_train_dat, "w", encoding='utf8') as cn_train, \
                open(self.en_train_dat, "w", encoding='utf8') as en_train, \
                open(self.cn_test_dat, "w", encoding='utf8') as cn_test, \
                open(self.en_test_dat, "w", encoding='utf8') as en_test:

            for doc in docs:
                cn_tokens, en_tokens = self.segment(doc)
                cn_tokens = self.clean_tokens(cn_tokens, "zh")
                en_tokens = self.clean_tokens(en_tokens)
                cn_doc = " ".join(cn_tokens)
                en_doc = " ".join(en_tokens)

                cn_train.write(cn_doc + "\n")
                en_train.write(en_doc + "\n")
                cn_test.write(cn_doc + "\n")
                en_test.write(en_doc + "\n")

                for cn_token in cn_tokens:
                    cn_vocab.add(cn_token)
                for en_token in en_tokens:
                    en_vocab.add(en_token)

        with open(self.cn_train_vocab, 'w', encoding="utf8") as cn_vocab_output, open(self.en_train_vocab, 'w',
                                                                                      encoding='utf8') as en_vocab_output:
            for tk in cn_vocab:
                cn_vocab_output.write(tk + "\n")
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
        doc1_tk = doc1.split()
        doc2_tk = doc2.split()
        self.get_topics()
        d1_cn_topic_distrib = self.get_topic_distrib(doc1_tk, self.cn_topics)
        d2_cn_topic_distrib = self.get_topic_distrib(doc2_tk, self.cn_topics)
        d1_en_topic_distrib = self.get_topic_distrib(doc1_tk, self.en_topics)
        d2_en_topic_distrib = self.get_topic_distrib(doc2_tk, self.en_topics)
        # cn_sim = gensim.matutils.cossim(d1_cn_topic_distrib, d2_cn_topic_distrib)
        # en_sim = gensim.matutils.cossim(d1_en_topic_distrib, d2_en_topic_distrib)
        # #return (cn_sim + en_sim) / 2
        d1_cn_topic_distrib.extend(d1_en_topic_distrib)
        d2_cn_topic_distrib.extend(d2_en_topic_distrib)
        return gensim.matutils.cossim(d1_cn_topic_distrib, d2_cn_topic_distrib)

    def get_model_name(self):
        return "CL_LDA"


if __name__ == "__main__":
    pass
