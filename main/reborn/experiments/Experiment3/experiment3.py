import argparse

from DataReader import CM1Reader, EzCLinizReader, MavenReader, os, DATA_DIR
from Datasets import MAP_cal, Dataset
from LDA import LDA
from TR_VSM import TR_VSM
from VSM import VSM


class Experiment3:
    """
    Create a replacement list, then replace part of the english tokens with Chinese synonyms, apply the
    translation based methods to generate trace links. After getting the links, evaluate the subset of links which have
    impacted source or target artifacts
    """

    def __init__(self, model_type, data_set, replacement_file_relative_path, replacement_percent=0.5,
                 link_threshold_interval=5):
        self.model_type = model_type
        reader = None
        if data_set == "cm1":
            reader = CM1Reader()
        elif data_set == "ezclinic":
            reader = EzCLinizReader()
        elif data_set == "maven":
            reader = MavenReader()

        self.dataSet = reader.readData()
        self.link_threshold_interval = link_threshold_interval
        self.replace_dict: dict = self.read_replacement_tokens_as_dict(replacement_file_relative_path)
        self.result_dir = "./results"
        self.replacement_percent = replacement_percent

    def read_replacement_tokens_as_dict(self, replacement_file_path):
        file_path = os.path.join(DATA_DIR, 'word_replace_list', replacement_file_path)
        replace_dict = dict()
        with open(file_path, encoding='utf8') as fin:
            for line in fin:
                parts = line.strip("\n\t\r").split(",")
                en_word = parts[0]
                cnt = parts[1]
                zh_words = parts[2:]
                replace_dict[en_word] = zh_words
            return replace_dict

    def run_model(self, model, dataset: Dataset):
        results = dict()
        for link_set_id in dataset.gold_link_sets:
            link_set = dataset.gold_link_sets[link_set_id]
            source_aritf = link_set.artiPair.source_artif
            target_artif = link_set.artiPair.target_artif
            gen_links = self.get_links(model, source_aritf, target_artif)
            results[link_set_id] = gen_links
        return results

    def get_links(self, trace_model, source_artifact, target_artifact):
        return trace_model.get_link_scores(source_artifact, target_artifact)

    def get_model(self, model_type, fo_lang_code, docs):
        model = None
        if model_type == "vsm":
            model = VSM(fo_lang_code=fo_lang_code)
            model.build_model(docs)
        elif model_type == "lda":
            model = LDA(fo_lang_code=fo_lang_code)
            model.build_model(docs, num_topics=60, passes=100)
        elif model_type == "tr-vsm":
            model = TR_VSM(fo_lang_code=fo_lang_code)
            model.build_model(docs)
        return model

    def write_result(self, writer, prf, map_score):
        writer.write("MAP={}\n".format(map_score))
        writer.write(" P,R,F\n")
        writer.write(str(prf) + "\n")

    def run(self):
        impacted_dataSet = self.dataSet.get_impacted_dataSet(self.replace_dict, self.replacement_percent,
                                                             self.replacement_percent)
        impacted_model = self.get_model(self.model_type,
                                        "en", impacted_dataSet.get_docs())
        impacted_results = self.run_model(impacted_model, impacted_dataSet)

        for linkset_id in impacted_results:
            print("Processing link set {}".format(linkset_id))
            impacted_result = sorted(impacted_results[linkset_id], key=lambda k: k[2], reverse=True)
            impacted_map = MAP_cal(impacted_results, impacted_dataSet.gold_link_sets[
                linkset_id].links, do_sort=False).run()
            threshold = 0
            scores = []
            while threshold <= 100:
                filter_links_above_threshold = [x for x in impacted_result if x[2] >= threshold / 100]
                eval_score = impacted_dataSet.evaluate_link_set(linkset_id, filter_links_above_threshold)
                scores.append(eval_score)
                threshold += self.link_threshold_interval

            write_dir = os.path.join(self.result_dir, self.model_type)
            file_name = "{}_{}.txt".format(self.model_type, linkset_id)
            link_score_file = "{}_{}_link_score.txt".format(self.model_type, linkset_id)
            if not os.path.isdir(write_dir):
                os.makedirs(write_dir)
            output_file_path = os.path.join(write_dir, file_name)
            link_score_path = os.path.join(write_dir, link_score_file)

            print("origin MAP=", map)
            print("Origin P,C,F")
            print(scores)

            with open(output_file_path, 'w', encoding='utf8') as fout:
                self.write_result(fout, scores, map)
            with open(link_score_path, 'w', encoding='utf8') as fout:
                for link in impacted_result:
                    fout.write("{}\n".format(str(link)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Experiment 3 - replacement")
    parser.add_argument("--replacement_list",
                        help="the relative path of replacement file, the root is data/word_replace_list")
    parser.add_argument("--model", help="Model used for experiment")
    parser.add_argument("-d", help="dataset name")
    args = parser.parse_args()
    exp3 = Experiment3(model_type=args.model, data_set=args.d, replacement_file_relative_path=args.replacement_list)
    exp3.run()
