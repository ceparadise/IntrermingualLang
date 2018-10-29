import operator
import os
import argparse

import nltk
from gensim import corpora, models

from LDA import LDA
from VSM import VSM
from common import DATA_DIR
from model import Model
from reborn.DataReader import CM1Reader, EzCLinizReader, MavenReader
from reborn.Datasets import Dataset, MAP_cal
from reborn.Preprocessor import Preprocessor


class Experiment1:
    """
    Verify that replacing words in document will reduce the VSM and LDA performance
    """

    def __init__(self, replace_word_interval, model_type, data_set, replace_list_name, link_threshold_interval=5):
        self.exp_name = data_set
        self.selected_replace_words = dict()

        reader = None
        if data_set == "cm1":
            reader = CM1Reader()
        elif data_set == "ezclinic":
            reader = EzCLinizReader()
        elif data_set == "maven":
            reader = MavenReader()

        self.dataSet = reader.readData()
        self.replace_word_population_percentage = replace_word_interval
        self.replace_word_inverval = replace_word_interval
        self.link_threshold_interval = link_threshold_interval
        self.model_type = model_type
        self.replace_list_name = replace_list_name

    def get_model(self, model_type, fo_lang_code, docs):
        model = None
        if model_type == "vsm":
            model = VSM(fo_lang_code=fo_lang_code)
            model.build_model(docs)
        elif model_type == "lda":
            model = LDA(fo_lang_code=fo_lang_code)
            model.build_model(docs, num_topics=60, passes=100)
        return model

    def run(self):
        full_replace_list = self.read_replace_list(self.replace_list_name)
        replace_percentage = self.replace_word_population_percentage

        while replace_percentage <= 100:
            # Create a sub set of replace list
            replace_dict = dict()
            rep_word_size = int(len(full_replace_list) * (replace_percentage / 100))
            tmp = full_replace_list[:rep_word_size]
            for (en_word, fo_word) in tmp:
                replace_dict[en_word] = fo_word

            impacted_dataSet = self.dataSet.get_impacted_dataSet(replace_dict)
            replaced_dataSet = self.dataSet.get_replaced_dataSet(replace_dict)

            origin_model = self.get_model(self.model_type, "en", self.dataSet.get_docs())
            origin_results = self.run_model(origin_model, self.dataSet)

            impacted_model = self.get_model(self.model_type,
                                            "en", replaced_dataSet.get_docs())
            # impacted_model is trained with a dataSet that contains foreign language

            # replaced_result contains scores for all links, impacted_results contains scores for impacted links only
            impacted_results = self.run_model(impacted_model, impacted_dataSet)
            replaced_results = self.run_model(impacted_model, replaced_dataSet)

            for linkset_id in impacted_results:
                print("Running linkSet {}".format(linkset_id))
                origin_result = sorted(origin_results[linkset_id], key=lambda k: k[2], reverse=True)
                replaced_result = sorted(replaced_results[linkset_id], key=lambda k: k[2], reverse=True)
                impacted_result = sorted(impacted_results[linkset_id], key=lambda k: k[2], reverse=True)

                # calculate the MAP score for the impacted gold links on origin rank order
                origin_map = MAP_cal(origin_result, impacted_dataSet.gold_link_sets[
                    linkset_id].links, do_sort=False).run()

                # calculate the MAP score for the impacted gold links on the new ranking generated by the impacted_model
                impacted_map = MAP_cal(replaced_result, impacted_dataSet.gold_link_sets[
                    linkset_id].links, do_sort=False).run()

                # filter the origin result to keep only the impacted links. This set is the origin model score on impacted links
                impacted_links = set([(x[0], x[1]) for x in impacted_result])
                filter_origin_result = [x for x in origin_result if (x[0], x[1]) in impacted_links]

                threshold = 0
                origin_scores = []
                impacted_scores = []
                while threshold <= 100:
                    filter_origin_above_threshold = [x for x in filter_origin_result if x[2] >= threshold / 100]
                    impacted_result_above_threshold = [x for x in impacted_result if x[2] >= threshold / 100]
                    origin_eval_score = impacted_dataSet.evaluate_link_set(linkset_id, filter_origin_above_threshold)
                    impacted_eval_score = impacted_dataSet.evaluate_link_set(linkset_id,
                                                                             impacted_result_above_threshold)
                    origin_scores.append(origin_eval_score)
                    impacted_scores.append(impacted_eval_score)
                    threshold += self.link_threshold_interval
                file_name = "{}_{}_{}.txt".format(self.model_type, linkset_id,
                                                  replace_percentage)
                write_dir = os.path.join("results", self.exp_name, self.model_type, self.replace_list_name)
                if not os.path.isdir(write_dir):
                    os.makedirs(write_dir)
                output_file_path = os.path.join(write_dir, file_name)
                with open(output_file_path, 'w') as fout:
                    fout.write(replaced_dataSet.gold_link_sets[linkset_id].replacement_info + "\n")
                    self.write_result(fout, origin_scores, origin_map, impacted_scores, impacted_map)
                print("origin MAP=", origin_map)
                print("Origin P,C,F")
                print(origin_scores)

                print("impacted_MAP=", impacted_map)
                print("impacted P,C,F")
                print(impacted_scores)
            replace_percentage += self.replace_word_inverval

    def read_replace_list(self, replace_list_name):
        file_path = os.path.join(DATA_DIR, 'word_replace_list', replace_list_name)
        with open(file_path, encoding='utf8') as fin:
            tmp = []
            for line in fin:
                parts = line.split(",")
                if len(parts) == 3:
                    en_word = parts[0].strip()
                    cnt = parts[1]
                    fo_word = parts[2].strip()
                    tmp.append((en_word, fo_word))
            return tmp

    def get_links(self, trace_model, source_artifact, target_artifact):
        return trace_model.get_link_scores(source_artifact, target_artifact)

    def run_model(self, model, dataset: Dataset):
        results = dict()
        for link_set_id in dataset.gold_link_sets:
            link_set = dataset.gold_link_sets[link_set_id]
            source_aritf = link_set.artiPair.source_artif
            target_artif = link_set.artiPair.target_artif
            gen_links = self.get_links(model, source_aritf, target_artif)
            results[link_set_id] = gen_links
        return results

    def write_result(self, writer, origin_score, origin_map, impacted_score, impacted_map):
        writer.write("origin MAP= {}\n".format(origin_map))
        writer.write("origin P,C,F\n")
        writer.write(str(origin_score) + "\n")

        writer.write("impacted_MAP= {}\n".format(impacted_map))
        writer.write("impacted P,C,F\n")
        writer.write(str(impacted_score) + "\n")

    def create_list(self, output_file_path):
        preprocessor = Preprocessor()
        words_in_both_side_cnt = dict()
        with open(output_file_path, 'w') as fout:
            for linkSet_id in self.dataSet.gold_link_sets:
                link_set = self.dataSet.gold_link_sets[linkSet_id]
                source_cnt_dict = dict()
                target_cnt_dict = dict()
                # Count the word in both side
                for source_artif in link_set.artiPair.source_artif:
                    doc = link_set.artiPair.source_artif[source_artif]
                    tokens = preprocessor.get_tokens(doc)
                    for tk in tokens:
                        source_cnt_dict[tk] = source_cnt_dict.get(tk, 0) + 1

                for target_artif in link_set.artiPair.target_artif:
                    doc = link_set.artiPair.target_artif[target_artif]
                    tokens = preprocessor.get_tokens(doc)
                    for tk in tokens:
                        target_cnt_dict[tk] = target_cnt_dict.get(tk, 0) + 1

                words_in_both_side = source_cnt_dict.keys() & target_cnt_dict.keys()
                for word_in_both_side in words_in_both_side:
                    source_cnt = source_cnt_dict[word_in_both_side]
                    target_cnt = target_cnt_dict[word_in_both_side]
                    total_cnt = source_cnt + target_cnt
                    words_in_both_side_cnt[word_in_both_side] = words_in_both_side_cnt.get(word_in_both_side,
                                                                                           0) + total_cnt
            sorted_wd_cnt_list = sorted(words_in_both_side_cnt.items(), key=operator.itemgetter(1), reverse=True)
            for wd in sorted_wd_cnt_list:
                fout.write("{},{},\n".format(wd[0], wd[1]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("CM1 Experiment")
    parser.add_argument("-c", "--create_replace_list",
                        help="Create a list of word, this list will be used to replace words in target artifacts after manually adding Chinese translation")
    parser.add_argument("--replace_list", help="replace list name")
    parser.add_argument("--replace_interval", default=10, type=int,
                        help="Increase the usage percentage of replace list that will be used for replacement by this interval ")
    parser.add_argument("--model", help="Model used for experiment")
    parser.add_argument("--data_set", help="The dataset that will be applied")
    args = parser.parse_args()

    exp = Experiment1(args.replace_interval, model_type=args.model, data_set=args.data_set,
                      replace_list_name=args.replace_list)
    if args.create_replace_list:
        exp.create_list(args.create_replace_list)
    else:
        exp.run()
