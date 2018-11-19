import argparse

from DataReader import CM1Reader, EzCLinizReader, MavenReader, os, DATA_DIR


class Experiment3:
    """
    Create a replacement list, then replace part of the english tokens with Chinese synonyms, apply the
    translation based methods to generate trace links. After getting the links, evaluate the subset of links which have
    impacted source or target artifacts
    """

    def __init__(self, model_type, data_set, replacement_file_relative_path, link_threshold_interval=5):
        self.model_type = model_type
        if data_set == "cm1":
            reader = CM1Reader()
        elif data_set == "ezclinic":
            reader = EzCLinizReader()
        elif data_set == "maven":
            reader = MavenReader()

        self.dataSet = reader.readData()
        self.link_threshold_interval = link_threshold_interval
        self.replace_dict: dict = self.read_replacement_tokens_as_dict(replacement_file_relative_path)

    def read_replacement_tokens_as_dict(self, replacement_file_path):
        file_path = os.path.join(DATA_DIR, 'word_replace_list', "experiment3", replacement_file_path)
        replace_dict = dict()
        with open(file_path, encoding='utf8') as fin:
            tmp = []
            for line in fin:
                parts = line.split(",")
                en_word = parts[0]
                cnt = parts[1]
                zh_words = parts[1:]
                replace_dict[en_word] = zh_words
            return replace_dict

    def run(self):
        impacted_dataSet = self.dataSet.get_impacted_dataSet(self.replace_dict)
        replaced_dataSet = self.dataSet.get_replaced_dataSet(self.replace_dict)
        origin_model = self.get_model(self.model_type, "en", self.dataSet.get_docs())


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Experiment 2 - replacement")
    parser.add_argument("--replacement_list")
    parser.add_argument("--replacement_percent")
    parser.add_argument("--model", help="Model used for experiment")
    parser.add_argument("-t", action="store_true", help="use translated dataset")
    parser.add_argument("-d", help="dataset name")
