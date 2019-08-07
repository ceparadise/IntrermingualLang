import argparse
import os
import re

from DataReader import Exp3DataReader
from Datasets import MAP_cal, Dataset
from GVSM import GVSM
from LDA import LDA
from LSI import LSI
from Preprocessor import Preprocessor
from VSM import VSM

default_git_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..',
                               'github_project_crawl',
                               "git_projects")


class Experiment3:
    def __init__(self, repo_path, model_type, use_translated_data, term_similarity_type, lang_code,
                 link_threshold_interval=5,
                 output_sub_dir="", print_result=False, github_projects_dir=default_git_dir):
        """

        :param repo_path: the repo path in github
        :param model_type: vsm, gvsm, lda
        :param use_translated_data: whether use translated data or not
        :param term_similarity_type: for gvsm only.
        :param link_threshold_interval: The sample rate for threshold
        :param output_sub_dir: the sub directory for results under Experiment2/result/. Group the experiment by the time running the script
        """
        self.git_projects_dir = github_projects_dir
        self.use_translated_data = use_translated_data
        self.model_type = model_type
        self.repo_path = repo_path
        self.lang_code = lang_code
        self.data_dir = os.path.join(self.git_projects_dir, repo_path)
        self.preprocessor = Preprocessor()
        self.preprocessed_dataset()  # Create clean tokens if not exist
        self.link_threshold_interval = link_threshold_interval
        self.term_similarity_type = term_similarity_type
        self.output_sub_dir = output_sub_dir

    def get_model(self, model_type, fo_lang_code, docs):
        model = None
        if model_type == "vsm":
            model = VSM(fo_lang_code=fo_lang_code)
            model.build_model(docs)
        elif model_type == "lda":
            model = LDA(fo_lang_code=fo_lang_code)
            model.build_model(docs, num_topics=60, passes=100)
        elif model_type == "gvsm":
            model = GVSM(fo_lang_code=fo_lang_code, term_similarity_type=self.term_similarity_type)
            model.build_model(docs)
        elif model_type == "lsi":
            model = LSI(fo_lang_code=fo_lang_code)
            model.build_model(docs, num_topics=60)
        return model

    def preprocessed_dataset(self):
        """
        Preprocess the project data to get english and chinese tokens, write them back to files.
        Skip if the data dir is already there.
        :return:
        """
        output_dir = os.path.join(self.data_dir, "clean_token_data")
        translated_dir = os.path.join(self.data_dir, "en_trans")
        translated_token_dir = os.path.join(translated_dir, "clean_translated_tokens")
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
            print("Processing Issues...")
            with open(os.path.join(self.data_dir, "issue.csv"), encoding='utf8') as fin, \
                    open(os.path.join(output_dir, 'issue.csv'), 'w', encoding='utf8') as fout:
                for i, line in enumerate(fin):
                    if i == 0:
                        fout.write(line)
                        continue
                    parts = line.strip("\n\t\r").split(
                        ",")  # Google translation introduce columa which break csv format
                    id = parts[0]
                    content = " ".join(parts[1:-1])
                    issue_close_time = parts[-1]
                    # Remove a few patterns
                    content = re.sub("\[[^\]]+\]", " ", content)
                    issue_close_time = issue_close_time.strip("\n\t\r")
                    issue_tokens = self.preprocessor.get_tokens(content, self.lang_code)
                    content_tks = " ".join(issue_tokens)
                    fout.write("{},{},{}\n".format(id, content_tks, issue_close_time))
            print("Processing Commit...")
            with open(os.path.join(self.data_dir, "commit.csv", ), encoding='utf8') as fin, \
                    open(os.path.join(output_dir, "commit.csv"), 'w', encoding='utf8') as fout:
                for i, line in enumerate(fin):
                    if i == 0:
                        fout.write(line)
                        continue

                    parts = line.strip("\n\t\r").split(",")
                    id = parts[0]
                    summary = parts[1]
                    content = " ".join(parts[2:-1])
                    commit_time = parts[-1]

                    summary_tokens = self.preprocessor.get_tokens(summary, self.lang_code)
                    content_tks = self.preprocessor.get_tokens(content, self.lang_code)
                    commit_time = commit_time.strip("\n\t\r")
                    fout.write("{},{},{},{}\n".format(id, " ".join(summary_tokens), " ".join(content_tks), commit_time))
        else:
            print("Dir {} alread exist, skip creating".format(output_dir))

        if not os.path.isdir(translated_token_dir) and self.use_translated_data is True:
            os.mkdir(translated_token_dir)
            print("Preprocess Translated Issues...")
            with open(os.path.join(translated_dir, "issue.csv"), encoding='utf8') as fin, \
                    open(os.path.join(translated_token_dir, "issue.csv"), "w", encoding='utf8') as fout:
                for i, line in enumerate(fin):
                    if i == 0:
                        fout.write(line)
                        continue
                    parts = line.strip("\n\t\r").split(
                        ",")  # Google translation introduce columa which break csv format
                    id = parts[0]
                    content = " ".join(parts[1:-1])
                    issue_close_time = parts[-1]
                    # Remove a few patterns
                    content = re.sub("\[[^\]]+\]", " ", content)
                    issue_tokens = self.preprocessor.get_tokens(content, "en")
                    content_tks = " ".join(issue_tokens)
                    fout.write("{},{},{}\n".format(id, content_tks, issue_close_time))

            print("Processing Translated Commit...")
            with open(os.path.join(translated_dir, "commit.csv"), encoding='utf8') as fin, \
                    open(os.path.join(translated_token_dir, "commit.csv"), "w", encoding='utf8') as fout:
                for i, line in enumerate(fin):
                    if i == 0:
                        fout.write(line)
                        continue
                    parts = line.strip("\n\t\r").split(",")
                    id = parts[0]
                    summary = parts[1]
                    content = " ".join(parts[2:-1])
                    commit_time = parts[-1]

                    # Remove a few patterns
                    pass

                    summary_tokens = self.preprocessor.get_tokens(summary, 'en')
                    content_tks = self.preprocessor.get_tokens(content, "en")
                    fout.write("{},{},{},{}\n".format(id, " ".join(summary_tokens), " ".join(content_tks), commit_time))
        else:
            print("Dir {} already exist, skip creating".format(translated_token_dir))

    # def run_model(self, model, dataset: Dataset):
    #     results = dict()
    #     for link_set_id in dataset.gold_link_sets:
    #         link_set: LinkSet = dataset.gold_link_sets[link_set_id]
    #         #gen_links = self.get_links(model, link_set.artiPair)
    #         gen_links = self.get_links()
    #         results[link_set_id] = gen_links
    #     return results

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

    def run(self):
        reader = Exp3DataReader(self.git_projects_dir,self.repo_path)
        dataSet = reader.readData(use_translated_data=self.use_translated_data)
        dataSet, dataset_info = reader.limit_artifacts_in_links(dataSet)
        print(dataSet)
        model = self.get_model(self.model_type, "en", dataSet.get_docs())
        results = self.run_model(model, dataSet)
        for link_set_id in dataSet.gold_link_sets:
            print("Processing link set {}".format(link_set_id))
            result = sorted(results[link_set_id], key=lambda k: k[2], reverse=True)
            map = MAP_cal(result, dataSet.gold_link_sets[link_set_id].links, do_sort=False).run()
            threshold = 0
            scores = []
            while threshold <= 100:
                # batch_size = int(threshold / 100 * len(result))
                # filter_links_above_threshold = result[:batch_size]
                filter_links_above_threshold = [x for x in result if x[2] >= threshold / 100]
                eval_score = dataSet.evaluate_link_set(link_set_id, filter_links_above_threshold)
                scores.append(eval_score)
                threshold += self.link_threshold_interval

            if not self.use_translated_data:
                trans_postfix = "origin"
            else:
                trans_postfix = "trans"
            write_dir = os.path.join("results", self.output_sub_dir, self.repo_path,
                                     "_".join([self.model_type, trans_postfix]))

            file_name = "{}_{}.txt".format(self.model_type, link_set_id)
            link_score_file = "{}_{}_link_score.txt".format(self.model_type, link_set_id)
            if not os.path.isdir(write_dir):
                os.makedirs(write_dir)
            output_file_path = os.path.join(write_dir, file_name)
            link_score_path = os.path.join(write_dir, link_score_file)

            print("origin MAP=", map)
            print("Origin P,C,F")
            print(scores)

            with open(output_file_path, 'w', encoding='utf8') as fout:
                fout.write(dataset_info + "\n")
                self.write_result(fout, scores, map)
            with open(link_score_path, 'w', encoding='utf8') as fout:
                for link in result:
                    fout.write("{}\n".format(str(link)))

    def write_result(self, writer, prf, map_score):
        writer.write("MAP={}\n".format(map_score))
        writer.write(" P,R,F\n")
        writer.write(str(prf) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Experiment 3 - replacement")
    parser.add_argument("--replacement_list",
                        help="the relative path of replacement file, the root is data/word_replace_list")
    parser.add_argument("--model", help="Model used for experiment")
    parser.add_argument("-d", help="dataset name")
    args = parser.parse_args()
    exp3 = Experiment3(model_type=args.model, data_set=args.d, replacement_file_relative_path=args.replacement_list)
    exp3.run()