import re
import subprocess, os
from nltk.tokenize.stanford_segmenter import StanfordSegmenter
import many_stop_words
import shutil


class CL_LSA:
    def __init__(self):
        self.seg = StanfordSegmenter()
        self.seg.default_config('zh')

    def segment(self, doc):
        seg_str = self.seg.segment(doc)
        ch_token = self.get_zh(seg_str)
        en_token = self.get_en(doc)
        return ch_token, en_token

    def get_zh(self, doc):
        pattern = re.compile("[\u4e00-\u9fff]+")
        res = pattern.findall(doc)
        return res

    def get_en(self, doc):
        pattern = re.compile("[a-zA-Z]+")
        res = pattern.findall(doc)
        return res;

    def train_CL_LSA(self, doc, project_name):
        working_dir = 'G:/Projects/InterLingualTrace/algorithms/Cross-Lingual-Topic-Model-master/src/train'
        input_dir_path = os.path.join(working_dir, "../../input/")
        self.to_CL_LAS_data_files(doc, input_dir_path, project_name)
        cn_train = "_".join([project_name, "cn", "train"])
        en_train = "_".join([project_name, "en", "train"])
        cn_input_dir = os.path.join(input_dir_path, cn_train)
        en_input_dir = os.path.join(input_dir_path, en_train)
        output_dir = os.path.join(working_dir, "../../train_output/ ")
        corpus_name = project_name
        train_command = "python -m lda.launch_train --en_input_directory={} " \
                        "--ch_input_directory={} --output_directory={} " \
                        "--corpus_name={} --number_of_topics_ge=10 --training_iterations=100 --lamda=0.5 --alpha_alpha=0.5 --alpha_beta=0.01".format(
            en_input_dir, cn_input_dir, output_dir, corpus_name)
        train_process = subprocess.Popen(train_command, cwd=working_dir)
        train_process.wait()
        # return self.test_CL_LSA(doc, project_name)
        # Read topic distributions


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

    def to_CL_LAS_data_files(self, doc, intput_dir_path, project_name):
        """
        Convert a percent dict to CLLSA usaable data
        :return:
        """
        cn_vocab = set()
        en_vocab = set()

        cn_train_dir = os.path.join(intput_dir_path, "_".join([project_name, "cn", "train"]))
        cn_test_dir = os.path.join(intput_dir_path, "_".join([project_name, "cn", "test"]))
        en_train_dir = os.path.join(intput_dir_path, "_".join([project_name, "en", "train"]))
        en_test_dir = os.path.join(intput_dir_path, "_".join([project_name, "en", "test"]))

        if not os.path.exists(cn_train_dir):
            os.mkdir(cn_train_dir)
        if not os.path.exists(cn_test_dir):
            os.mkdir(cn_test_dir)
        if not os.path.exists(en_train_dir):
            os.mkdir(en_train_dir)
        if not os.path.exists(en_test_dir):
            os.mkdir(en_test_dir)

        cn_train_dat = os.path.join(cn_train_dir, "train.dat")
        en_train_dat = os.path.join(en_train_dir, "train.dat")
        cn_test_dat = os.path.join(cn_test_dir, "test.dat")
        en_test_dat = os.path.join(en_test_dir, "test.dat")
        cn_train_vocab = os.path.join(cn_train_dir, "voc.dat")
        en_train_vocab = os.path.join(en_train_dir, "voc.dat")
        with open(cn_train_dat, "w", encoding='utf8') as cn_train, \
                open(en_train_dat, "w", encoding='utf8') as en_train, \
                open(cn_test_dat, "w", encoding='utf8') as cn_test, \
                open(en_test_dat, "w", encoding='utf8') as en_test:
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

        with open(cn_train_vocab, 'w', encoding="utf8") as cn_vocab_output, open(en_train_vocab, 'w',
                                                                                 encoding='utf8') as en_vocab_output:
            for tk in cn_vocab:
                cn_vocab_output.write(tk + "\n")
            for tk in en_vocab:
                en_vocab_output.write(tk + "\n")
