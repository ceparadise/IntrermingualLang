from googletrans import Translator
import os
import random
from time import sleep


class translateReplacement:
    def __init__(self, interval, dataset_name="EasyClinicDataset", en_dir_name="2 - docs (English)",
                 fo_dir_names_codes=[("1 - docs (Italian)", "it")], input_dir="raw_data", output_dir="output",
                 translate=False):
        """

        :param interval:
        :param dataset_name: Dataset name which is the root directory.
        :param en_dir_name: English data directory.
        :param fo_dir_names_code: A list of tuple which include (dir_name, language_code)
        :param input_dir:
        :param output_dir:
        """
        self.interval = interval
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.isTranslate = translate
        self.fo_dir_names_codes = fo_dir_names_codes

        self.input_dataset_dir_path = os.path.join(input_dir, dataset_name)
        self.output_dataset_dir_path = os.path.join(output_dir, dataset_name)
        if not os.path.isdir(self.output_dataset_dir_path):
            os.makedirs(self.output_dataset_dir_path)

        self.dataset_name = dataset_name

        self.paths = []
        self.en_dir_path = os.path.join(self.input_dataset_dir_path, en_dir_name)
        self.get_file_paths(self.en_dir_path)
        # Every language directory must have same acrhitecutre as the english directory
        self.paths = [os.path.relpath(x, self.en_dir_path) for x in self.paths]

    def get_file_paths(self, root):
        file_names = os.listdir(root)
        for name in file_names:
            file_path = os.path.join(root, name)
            if os.path.isdir(file_path):
                self.get_file_paths(file_path)
            else:
                self.paths.append(file_path)

    def run(self):
        for dir_name_code in self.fo_dir_names_codes:
            self.process(dir_name_code)

    def process(self, name_code):
        """
        Mix the given language with English
        :return:
        """
        fo_lang_input_dir_root = os.path.join(self.input_dataset_dir_path, name_code[0])
        fo_lang_output_dir_root = os.path.join(self.output_dataset_dir_path, name_code[1])
        if not os.path.isdir(fo_lang_output_dir_root):
            os.makedirs(fo_lang_output_dir_root)

        lang_code = name_code[1]
        for rel_path in self.paths:
            print("Processing {} for language {}".format(rel_path, lang_code))
            fo_file_path = os.path.join(fo_lang_input_dir_root, rel_path)
            en_file_path = os.path.join(self.en_dir_path, rel_path)

            en_sentences = []
            fo_sentences = []

            with open(en_file_path, encoding='utf8',errors="ignore") as fin:
                en_sentences = fin.readlines()
                en_sentences = [sent.strip("\n\t\r ") for sent in en_sentences]

            if self.isTranslate:
                fo_sentences = self.translate_sentences(en_sentences, lang_code)
            else:
                with open(fo_file_path, encoding='utf8', errors="ignore") as fin:
                    fo_sentences = fin.readlines()
                    fo_sentences = [sent.strip("\n\t\r ") for sent in fo_sentences]

            percentange = 0.0
            while percentange <= 1:
                # relative path to the parent dir of the file
                parent_dir_name = os.path.basename(os.path.dirname(rel_path))
                file_name = os.path.basename(rel_path)
                pack_path = os.path.join(fo_lang_output_dir_root, self.gen_package_name(percentange))
                target_dir = os.path.join(pack_path, parent_dir_name)
                if not os.path.isdir(target_dir):
                    os.makedirs(target_dir)
                self.gen_package_with_percentage(target_dir, file_name, percentange, en_sentences, fo_sentences)
                percentange += self.interval

    def gen_package_with_percentage(self, target_dir, filename, percentage, en_sentences, fo_sentences):
        with open(os.path.join(target_dir, filename), 'w', encoding='utf8') as fout:
            mixed_sentences = []
            sent_num = len(en_sentences)
            picked_nums = random.sample([i for i in range(0, sent_num)], int(percentage * sent_num))
            for i in range(0, sent_num):
                if i in picked_nums:
                    mixed_sentences.append(fo_sentences[i] + "\n")
                else:
                    mixed_sentences.append(en_sentences[i] + "\n")
            fout.writelines(mixed_sentences)

    def gen_package_name(self, percentage):
        return "docs-{}%".format(round(percentage * 100, 2))

    def translate_sentences(self, en_sentences, lang_code):
        res = []
        translator = Translator()
        for en_word in en_sentences:
            try:
                # ch_sentence = translator.translate(en_word, dest='zh-cn').text
                ch_sentence = translator.translate(en_word, dest=lang_code).text
                res.append(ch_sentence)
            except Exception as e:
                print("Error with translating {}, sleep 60s to cool down for google translation".format(en_word))
                sleep(60)
        return res


if __name__ == "__main__":
    replacer = translateReplacement(0.1)
    replacer.run()
    print("finished")
