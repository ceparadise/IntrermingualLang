import os
from common import translate_sentences


class Trans_Agent:
    """
    Add the translation layer to normal models. Translation is slow thus the translated sentences/doc are cached to local disk.
    Every model will load the cached file into memory
    """

    def __init__(self, trans_cache_dir_path=""):
        self.trans_cache_dir_path = trans_cache_dir_path
        self.par_en_path = os.path.join(self.trans_cache_dir_path, "par_en.txt")
        self.par_fo_path = os.path.join(self.trans_cache_dir_path, "par_fo.txt")
        self.map_file_path = os.path.join(self.trans_cache_dir_path, "map.txt")

        self.fo_dict = dict()
        self.en_dict = dict()
        self.map_dict = dict()

        print("Loading translation cache to memory ...")
        self.fo_dict = self.__read_par_doc_as_dict(self.par_fo_path)
        self.en_dict = self.__read_par_doc_as_dict(self.par_en_path)
        self.map_dict = self.__read_par_doc_as_dict(self.map_file_path)
        print("Finished loading ...")

    def __read_par_doc_as_dict(self, par_file_path):
        tmp_dict = dict()
        if os.path.isfile(par_file_path):
            with open(par_file_path, encoding='utf8') as fin:
                for line in fin:
                    line = line.strip("\n")
                    parts = line.split("|")
                    key = parts[0]
                    value = parts[1]
                    tmp_dict[key] = value
        return tmp_dict

    def __write_dict_as_par_doc(self, par_doc_path, target_dict):
        dir_path = os.path.dirname(par_doc_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(par_doc_path, 'w', encoding='utf8') as fout:
            for key in target_dict:
                key = key.strip("\n")
                fout.write("{}|{}\n".format(key, target_dict[key]))

    def get_translated_doc(self, doc):
        doc = doc.replace("|", " ")
        doc = doc.replace("\n", " ")
        if doc not in self.fo_dict:
            trans = translate_sentences(doc, "en")
            fo_index = str(len(self.fo_dict))
            en_index = str(len(self.en_dict))
            self.fo_dict[doc] = fo_index
            self.en_dict[en_index] = trans
            self.map_dict[fo_index] = en_index

        find_fo_index = self.fo_dict[doc]
        find_end_index = self.map_dict[find_fo_index]
        return self.en_dict[find_end_index]

    def dump_trans_cache(self):
        print("Dump the translations into local disk...")
        self.__write_dict_as_par_doc(self.par_fo_path, self.fo_dict)
        self.__write_dict_as_par_doc(self.par_en_path, self.en_dict)
        self.__write_dict_as_par_doc(self.map_file_path, self.map_dict)


if __name__ == "__main__":
    test_sent1 = "这是中文的测试.\n ||分两个句子"
    test_sent2 = "2号句子include 一些 english"
    agent = Trans_Agent("../output/trans_cache/test")
    print(agent.get_translated_doc(test_sent1))
    print(agent.get_translated_doc(test_sent2))
    agent.dump_trans_cache()
