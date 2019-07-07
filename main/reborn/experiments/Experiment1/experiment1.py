import operator
import os
import argparse
import random
from math import floor

import nltk
import numpy
from gensim import corpora, models

from LDA import LDA
from VSM import VSM
from common import DATA_DIR
from experiments.analyzeTools import Analyzer
from reborn.DataReader import CM1Reader, EzCLinizReader, MavenReader, DronologyReader
from reborn.Datasets import Dataset, MAP_cal
from reborn.Preprocessor import Preprocessor


class Experiment1:
    """
    Verify that replacing words in document will reduce the VSM and LDA performance
    """

    def __init__(self, replace_word_interval, model_type, data_set, replace_list_name, link_threshold_interval=5,
                 average_time=1):
        self.exp_name = data_set
        self.selected_replace_words = dict()

        reader = None
        if data_set == "cm1":
            reader = CM1Reader()
        elif data_set == "ezclinic":
            reader = EzCLinizReader()
        elif data_set == "maven":
            reader = MavenReader()
        elif data_set == "dronology":
            reader = DronologyReader()

        self.dataSet = reader.readData()
        self.replace_word_population_percentage = replace_word_interval
        self.replace_word_inverval = replace_word_interval
        self.link_threshold_interval = link_threshold_interval
        self.model_type = model_type
        self.replace_list_name = replace_list_name
        self.analyzer = Analyzer()
        self.random_state = numpy.random.RandomState(1)
        self.average_time = average_time

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
        cnt = 0
        write_dir = os.path.join("results", self.exp_name, self.model_type, self.replace_list_name)
        if not os.path.isdir(write_dir):
            os.makedirs(write_dir)
        summary = dict()  # ke=(linkset_id, replace_percent) value = scores
        while cnt < self.average_time:
            cnt += 1
            full_replace_list = self.read_replace_list(self.replace_list_name)[:100]
            replace_percentage = 0
            while replace_percentage <= 100:
                # Create a sub set of replace list
                replace_dict = dict()
                rep_word_size = int(len(full_replace_list) * (replace_percentage / 100))
                tmp = random.sample(full_replace_list, rep_word_size)
                #tmp = full_replace_list[:rep_word_size]
                for (en_word, fo_word) in tmp:
                    replace_dict[en_word] = fo_word

                replaced_dataSet = self.dataSet.get_replaced_dataSet(replace_dict)
                replaced_model = self.get_model(self.model_type, "en", replaced_dataSet.get_docs())

                replaced_results = self.run_model(replaced_model, replaced_dataSet)

                for linkset_id in replaced_results:
                    if self.exp_name == "ezclinic" and linkset_id!="ID-CC":
                        continue
                    print("Running linkSet {}".format(linkset_id))
                    res_ky = (linkset_id, replace_percentage)

                    replaced_result = sorted(replaced_results[linkset_id], key=lambda k: k[2], reverse=True)
                    replaced_map = MAP_cal(replaced_result, replaced_dataSet.gold_link_sets[
                        linkset_id].links, do_sort=False).run()
                    threshold = 0
                    replaced_scores = []
                    replaced_best_f1 = 0
                    while threshold <= 100:
                        replaced_result_above_threshold = [x for x in replaced_result if x[2] >= threshold / 100]
                        #replaced_result_above_threshold = replaced_result[0:floor(len(replaced_result) * (threshold / 100))]
                        replaced_eval_score = replaced_dataSet.evaluate_link_set(linkset_id,
                                                                                 replaced_result_above_threshold)
                        if replaced_eval_score[2] > replaced_best_f1:
                            replaced_best_f1 = replaced_eval_score[2]

                        replaced_scores.append(replaced_eval_score)
                        threshold += self.link_threshold_interval
                    file_name = "{}_{}_{}.txt".format(self.model_type, linkset_id,
                                                      replace_percentage)
                    output_file_path = os.path.join(write_dir, file_name)

                    print("Replaced_MAP=", replaced_map)
                    print("Replaced P,C,F")
                    print(replaced_scores)
                    print("best f1 = {}".format(replaced_best_f1))

                    res_score =  replaced_best_f1, replaced_map
                    score_sum = summary.get(res_ky, [0, 0])
                    for i in range(len(score_sum)):
                        score_sum[i] += res_score[i]
                    summary[res_ky] = score_sum

                    with open(output_file_path, 'w', encoding='utf8') as fout:
                        fout.write(replaced_dataSet.gold_link_sets[linkset_id].replacement_info + "\n")
                        self.write_result(fout,  replaced_best_f1, replaced_map)

                replace_percentage += self.replace_word_inverval

        summary_path = os.path.join(write_dir, "summary.txt")
        with open(summary_path, "w", encoding='utf8') as fout:
            for key in summary:
                fout.write(str(key) + ",")
                scores = []
                for score in summary[key]:
                    scores.append(str(score / self.average_time))
                fout.write(",".join(scores) + "\n")

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
                    if len(fo_word) >0:
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

    def write_result(self, writer, replaced_score, replaced_map):
        # writer.write("Impacted MAP= {}\n".format(impacted_map))
        # writer.write("Impacted P,C,F\n")
        # writer.write(str(impacted_score) + "\n")

        writer.write("Replaced MAP= {}\n".format(replaced_map))
        writer.write("Replaced P,C,F\n")
        writer.write(str(replaced_score) + "\n")

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
    parser.add_argument("--exp_time", help="number of time to run this experiment", default=1, type=int)
    args = parser.parse_args()

    exp = Experiment1(args.replace_interval, model_type=args.model, data_set=args.data_set,
                      replace_list_name=args.replace_list, average_time=args.exp_time)
    if args.create_replace_list:
        exp.create_list(args.create_replace_list)
    else:
        exp.run()
