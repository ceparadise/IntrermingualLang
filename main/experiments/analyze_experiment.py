from subprocess import Popen, PIPE

import many_stop_words

from LDA import LDA
from VSM import VSM
from common import *
import xml.etree.ElementTree as ET
from gensim import corpora
import re


class CM1_Experiment:
    """
    This experiment investigate the intermingual language factors which affect the link accuracy.
    STEPS:
    1. Run VSM on all English dataset
    2. Output the weights of the words
    3. Assign the pos tag to the words
    4. Replace the high weights words with Chinese then rerun the experiment

    DATA SET:
    CM1 low level to high level requirement links

    """

    def __init__(self):
        self.answer = dict()
        self.file2links = dict()
        self.sourceArtifact = dict()
        self.targetArtifact = dict()
        self.output_dir = os.path.join("../../output", "cm1_analyze")
        self.model = None
        self.readData()

    def startStanforNLP(self):
        stanforNLP_server_cmd = " java -mx4g -cp * edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload tokenize,ssplit,pos,lemma,parse,depparse  -status_port 9000 -port 9000 -timeout 15000 -serverProperties StanfordCoreNLP-chinese.properties"
        self.start_server = Popen(stanforNLP_server_cmd.split(), cwd="G:\lib\stanford-corenlp-full-2016-10-31",
                                  stderr=PIPE, stdout=PIPE, shell=True)

        while (True):
            line = str(self.start_server.stderr.readline())
            print(line)
            success_mark = 'StanfordCoreNLPServer listening at'
            except_mark = 'Address already in use'
            if success_mark in line:
                print("server started...")
                break
            elif except_mark in line:
                print("server already started or port occupied...")
                break
        self.start_server.stderr.close()
        self.start_server.stdout.close()

    def replace_word_in_targetArtifact(self, replace_list):
        replaced_artifact_tokens = []
        for word, replacement in replace_list:
            for artif in self.targetArtifact:
                content = self.targetArtifact[artif]
                stop_words = many_stop_words.get_stop_words("en")
                for token in content.split():
                    token = token.lower()
                    if token not in stop_words and len(token) >= 2:
                        if token == word:
                            replaced_artifact_tokens.append(replacement)
                        else:
                            replaced_artifact_tokens.append(token)
        return " ".join(replaced_artifact_tokens)

    def run_model(self, model):
        self.model = model
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)
        self.model = model

        self.gen_links = sorted(self.get_links(self.model), key=lambda k: k[2], reverse=True)
        self.gold_links = []
        for s_artif in self.answer:
            for t_artif in self.answer[s_artif]:
                self.gold_links.append((s_artif, t_artif))

    def __read_artifact(self, path):
        res = dict()
        tree = ET.parse(path)
        root = tree.getroot()
        for artifact in root.iter('artifact'):
            id = artifact.find("id").text
            content = artifact.find("content").text
            res[id] = content
        return res

    def get_docs(self):
        docs = []
        for a in self.sourceArtifact:
            docs.append(self.sourceArtifact[a])
        for a in self.targetArtifact:
            docs.append(self.targetArtifact[a])
        return docs

    def readData(self):
        source_path = os.path.join(DATA_DIR, "cm1", "CM1-sourceArtifacts.xml")
        target_path = os.path.join(DATA_DIR, "cm1", "CM1-targetArtifacts.xml")
        answer_path = os.path.join(DATA_DIR, "cm1", "CM1-answerSet.xml")

        self.sourceArtifact = self.__read_artifact(source_path)
        self.targetArtifact = self.__read_artifact(target_path)

        tree = ET.parse(answer_path)
        root = tree.getroot()
        for artifact in root.iter('link'):
            source_id = artifact.find("source_artifact_id").text
            target_id = artifact.find("target_artifact_id").text
            if source_id not in self.answer:
                self.answer[source_id] = set()
            self.answer[source_id].add(target_id)

    def get_links(self, trace_model):
        links = []
        total = len(self.sourceArtifact) * len(self.targetArtifact)
        cnt = 0
        for s_id in self.sourceArtifact:
            for t_id in self.targetArtifact:
                if cnt % 1000 == 0:
                    print(str(cnt) + "/" + str(total))
                cnt += 1
                s_content = self.sourceArtifact[s_id]
                t_content = self.targetArtifact[t_id]
                score = trace_model.get_doc_similarity(s_content, t_content)
                links.append((s_id, t_id, score))
        return links

    def write_list(self, t_list, file_path):
        with open(file_path, 'w', encoding='utf8') as fout:
            for item in t_list:
                fout.write(str(item) + "\n")

    def __eval(self, gen_links, gold_links, total_num):
        gen_links = set(gen_links)
        gold_links = set(gold_links)
        tp = len(gen_links & gold_links)
        fp = len(gen_links - gold_links)
        fn = len(gold_links - gen_links)
        tn = total_num - len(gen_links | gold_links)
        if tp == 0:
            precision = 0
            recall = 0
        else:
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
        if recall + precision == 0:
            f1 = 0
        else:
            f1 = 2 * (recall * precision) / (recall + precision)
        return precision, recall, f1

    def eval(self):
        total_num = len(self.gen_links)  # Total possible combination
        for threshold in range(0, 100, 5):
            threshold = threshold / 100.0
            gen_links_above_thre = [(x[0], x[1]) for x in self.gen_links if (float)(x[2]) >= threshold]
            print("threshod=" + str(threshold) + ":" +
                  str(self.__eval(gen_links_above_thre, self.gold_links, total_num)))

    def word_distribution(self, word):
        """
        Get all artifacts that contains the given word and the count of that word
        :param word:
        :return:
        """
        cnt = 0
        s_art_with_wd = []
        t_art_with_wd = []
        for s_artif in self.sourceArtifact:
            content = self.sourceArtifact[s_artif]
            tokens = self.model.get_tokens(content)
            if word in tokens:
                cnt = 0
                for tk in tokens:
                    if word == tk:
                        cnt += 1
                s_art_with_wd.append((s_artif, cnt))

        for t_artif in self.targetArtifact:
            content = self.targetArtifact[t_artif]
            tokens = self.model.get_tokens(content)
            if word in tokens:
                cnt = 0
                for tk in tokens:
                    if word == tk:
                        cnt += 1
                t_art_with_wd.append((t_artif, cnt))
        return s_art_with_wd, t_art_with_wd


class CM1_Experiment2(CM1_Experiment):
    def __init__(self, word_threshold=10):
        super().__init__()
        self.selected_replace_words = dict()
        self.stop_words = many_stop_words.get_stop_words("en")
        self.replaced_target_artifacts = None
        self.impacted_artifacts = None
        self.word_threshold = word_threshold

    def get_replaced_docs(self):
        docs = []
        for a in self.sourceArtifact:
            docs.append(self.sourceArtifact[a])
        for a in self.replaced_target_artifacts:
            docs.append(self.replaced_target_artifacts[a])
        return docs

    def select_words_each_doc_threshold(self):
        """
        Print the words and their distribution (doc_id and times)
        :return:
        """

        def add_to_word_pool(artifacts):
            for artif in artifacts:
                content = artifacts[artif]
                content = content.lower()
                bow = self.__get_bag_of_words_for_str(content)
                for wd in bow:
                    if bow[wd] > self.word_threshold and wd not in self.stop_words:
                        if wd not in self.selected_replace_words:
                            self.selected_replace_words[wd] = 0
                        self.selected_replace_words[wd] += bow[wd]
                        self.impacted_artifacts.add(artif)

        add_to_word_pool(self.sourceArtifact)
        add_to_word_pool(self.targetArtifact)
        with open(os.path.join(self.output_dir, "cm1_exp_selected_words.txt"), 'w', encoding='utf8') as fout:
            for wd in self.selected_replace_words:
                fout.write(wd + "," + str(self.selected_replace_words[wd]) + "\n")

    def select_word_all_doc_threshold(self):
        contents = []
        contents.extend(self.sourceArtifact.items())
        contents.extend(self.targetArtifact.items())
        contents = [x[1] for x in contents]
        for content in contents:
            content = content.lower()
            cl_content = re.sub("[^a-z]", " ", content)
            tokens = cl_content.split()
            for tk in tokens:
                if len(tk) > 2 and tk not in self.stop_words:
                    self.selected_replace_words[tk] = self.selected_replace_words.get(tk, 0) + 1
        with open(os.path.join(self.output_dir, "cm1_exp_selected_words.txt"), 'w', encoding='utf8') as fout:
            ordered_words = sorted(self.selected_replace_words.items(), key=lambda k: k[1], reverse=True)
            for wd in ordered_words:
                fout.write(str(wd[0]) + "," + str(wd[1]) + "\n")

    def read_replace_list(self):
        file_path = os.path.join(DATA_DIR, "cm1", 'word_replace_list', "high_frequency.txt")
        replace_words = dict()
        with open(file_path, encoding='utf8') as fin:
            for line in fin:
                parts = line.split(",")
                if len(parts) == 3:
                    en_word = parts[0].strip()
                    cnt = parts[1]
                    fo_word = parts[2].strip()
                    if int(cnt) >= self.word_threshold:
                        replace_words[en_word] = fo_word
        print("Word Threshold = {}, {} word are selected to replace".format(self.word_threshold, len(replace_words)))
        return replace_words

    def replace_words_in_target_artifacts(self):
        self.replaced_target_artifacts = dict()
        self.impacted_artifacts = set()
        replace_words = self.read_replace_list()
        for t_artif in self.targetArtifact:
            content = self.targetArtifact[t_artif]
            content = content.lower()
            cl_content = re.sub("[^a-z]", " ", content)
            tokens = cl_content.split()
            replaced_tokens = []
            for token in tokens:
                if token in replace_words:
                    replaced_tokens.append(replace_words[token])
                    self.impacted_artifacts.add(t_artif)
                else:
                    replaced_tokens.append(token)
            self.replaced_target_artifacts[t_artif] = " ".join(replaced_tokens)

    def get_impacted_links(self):
        self.impacted_links = []
        self.gold_links = []
        print("{} target artifacts out of {} artifacts are impacted ...".format(len(self.targetArtifact),
                                                                                len(self.impacted_artifacts)))
        for s_artif in self.answer:
            for t_artif in self.answer[s_artif]:
                self.gold_links.append((s_artif, t_artif))
                if s_artif in self.impacted_artifacts or t_artif in self.impacted_artifacts:
                    self.impacted_links.append((s_artif, t_artif))
        print(str(len(self.impacted_links)) + "links are impacted by the replacedment, total links num=" + str(
            len(self.gold_links)))

    def run_origin_model(self, model):
        self.model = model
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)
        self.model = model
        self.gen_links = sorted(self.get_links(self.model, self.sourceArtifact, self.targetArtifact),
                                key=lambda k: k[2], reverse=True)

    def run_replaced_model(self, model):
        self.model = model
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)
        self.model = model
        tmp_target_artif = dict()
        for i_artif in self.impacted_artifacts:
            tmp_target_artif[i_artif] = self.replaced_target_artifacts[i_artif]
        self.gen_impacted_link = sorted(self.get_links(self.model, self.sourceArtifact, tmp_target_artif),
                                        key=lambda k: k[2], reverse=True)

    def __get_bow_for_corpus(self, str_list):
        """
        Get a global bow
        :param str_list:
        :return:
        """
        pass

    def __get_bag_of_words_for_str(self, text_str):
        """
        Convert a string into bag-of-words
        :return:
        """
        tokens = text_str.split()
        bow = dict()
        for tk in tokens:
            if tk not in bow:
                bow[tk] = 0
            bow[tk] += 1
        return bow

    def eval_and_compare(self):
        """
        1. Collect the links related with the impacted docs
        2. Generate the links which have no replacement
        3. Replace the words then run the same algorithm
        4. Evalute the 2 resutls
        :return:
        """

        print("=======Without Replacement========")
        map1 = MAP_cal(self.gen_links, self.gold_links)
        print("map=" + str(map1.run()))
        self.eval(self.gen_links, self.gold_links)

        print("=======With Replacement========")
        map2 = MAP_cal(self.gen_impacted_link, self.impacted_links)
        print("map=" + str(map2.run()))
        self.eval(self.gen_impacted_link, self.impacted_links)

    def __eval(self, gen_links, gold_links, total_num):
        gen_links = set(gen_links)
        gold_links = set(gold_links)
        tp = len(gen_links & gold_links)
        fp = len(gen_links - gold_links)
        fn = len(gold_links - gen_links)
        tn = total_num - len(gen_links | gold_links)
        if tp == 0:
            precision = 0
            recall = 0
        else:
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
        if recall + precision == 0:
            f1 = 0
        else:
            f1 = 2 * (recall * precision) / (recall + precision)
        return precision, recall, f1

    def eval(self, gen_links, gold_links):
        total_num = len(gen_links)  # Total possible combination
        for threshold in range(0, 100, 5):
            threshold = threshold / 100.0
            gen_links_above_thre = [(x[0], x[1]) for x in gen_links if (float)(x[2]) >= threshold]
            print("threshod=" + str(threshold) + ":" +
                  str(self.__eval(gen_links_above_thre, gold_links, total_num)))

    def get_links(self, trace_model, source_artifact, target_artifact):
        links = []
        total = len(source_artifact) * len(target_artifact)
        cnt = 0
        for s_id in self.sourceArtifact:
            for t_id in target_artifact:
                # if cnt % 1000 == 0:
                #     print(str(cnt) + "/" + str(total))
                cnt += 1
                s_content = source_artifact[s_id]
                t_content = target_artifact[t_id]
                score = trace_model.get_doc_similarity(s_content, t_content)
                links.append((s_id, t_id, score))
        return links


class Maven_Experiment(CM1_Experiment2):
    def __init__(self, word_threshold = 10):
        super(Maven_Experiment, self).__init__(word_threshold)
        self.answer = dict()
        self.sourceArtifact = dict()
        self.targetArtifact = dict()
        self.output_dir = os.path.join("../../output", "maven_analyze")
        self.model = None
        self.readData()

    def read_replace_list(self):
        file_path = os.path.join(DATA_DIR, "maven", 'word_replace_list', "high_frequency.txt")
        replace_words = dict()
        with open(file_path, encoding='utf8') as fin:
            for line in fin:
                parts = line.split(",")
                if len(parts) == 3:
                    en_word = parts[0].strip()
                    cnt = parts[1]
                    fo_word = parts[2].strip()
                    if int(cnt) >= self.word_threshold:
                        replace_words[en_word] = fo_word
        print("Word Threshold = {}, {} word are selected to replace".format(self.word_threshold, len(replace_words)))
        return replace_words

    def readData(self):
        source_path = os.path.join(DATA_DIR, "maven", "improvement.csv")
        target_path = os.path.join(DATA_DIR, "maven", "commits.csv")
        answer_path = os.path.join(DATA_DIR, "maven", "improvementCommitLinks.csv")

        with open(source_path) as fin:
            cnt = 0
            for line in fin:
                cnt += 1
                if cnt == 1:
                    continue
                parts = line.split(",")
                id = parts[0]
                content = parts[3]
                self.sourceArtifact[id] = content
        with open(target_path) as fin:
            cnt = 0
            for line in fin:
                cnt += 1
                if cnt == 1:
                    continue
                parts = line.split(",")
                id = parts[0]
                content = parts[2]
                self.targetArtifact[id] = content

        with open(answer_path) as fin:
            cnt = 0
            for line in fin:
                cnt += 1
                if cnt == 1:
                    continue
                parts = line.split(",")
                improve_id = parts[0]
                commit_id = parts[1]
                if improve_id not in self.answer:
                    self.answer[improve_id] = set()
                self.answer[improve_id].add(commit_id)


class MAP_cal:
    def __init__(self, rank, gold):
        self.rank_gold_pairs = []
        rank = sorted(rank, key=lambda k: k[2], reverse=True)
        rank = [(x[0], x[1]) for x in rank]
        self.rank_gold_pairs.append((rank, gold))

    def recall(self, rank, gold, num):
        included = 0
        slice = set(rank[:num + 1])
        for gold_link in gold:
            if gold_link in slice:
                included += 1
        return included / len(gold)

    def precision(self, rank, gold, num):
        hit = 0
        for i in range(0, num + 1):
            if rank[i] in gold:
                hit += 1
        return hit / (num + 1)

    def average_precision(self, rank, gold):
        sum = 0
        if len(gold) == 0:
            return 0
        for i in range(len(gold)):
            gold_index = rank.index(gold[i])
            precision = self.precision(rank, gold, gold_index)
            sum += precision
        return sum / len(gold)

    def mean_average_precision(self, rank_gold_pairs):
        sum = 0
        for pair in rank_gold_pairs:
            rank = pair[0]
            gold = pair[1]
            average_precision = self.average_precision(rank, gold)
            sum += average_precision
        return sum / len(rank_gold_pairs)

    def run(self):
        return self.mean_average_precision(self.rank_gold_pairs)


def link_with_artifact(links, artifact_id):
    """
    Collect the links which contains the given artifact
    :param links:
    :param artifact_id:
    :return:
    """
    res = set()
    for link in links:
        if link[0] == artifact_id or link[1] == artifact_id:
            res.add(link)
    return res


def run_cm1_exp(replace_list_name):
    cm1_exp = CM1_Experiment()
    replace_list = []
    try:
        with open(os.path.join(DATA_DIR, "cm1", 'word_replace_list', replace_list_name), encoding='utf8') as fin:
            for line in fin:
                parts = line.split(",")
                replace_list.append((parts[0].strip(), parts[1].strip()))
            cm1_exp.replace_word_in_targetArtifact(replace_list)
    except Exception as e:
        print(e)
        print("skip replacement")

    vsm = VSM(fo_lang_code="en")
    vsm.build_model(cm1_exp.get_docs())
    cm1_exp.run_model(vsm)
    cm1_exp.eval()
    word_weights = vsm.get_word_weights()
    word_weights = sorted(word_weights, key=lambda x: x[1], reverse=True)
    cm1_exp.write_list(word_weights, os.path.join(cm1_exp.output_dir, "word_weight.txt"))
    with open(os.path.join(cm1_exp.output_dir, "word_gold_links.txt"), 'w', encoding='utf8') as link_fout, \
            open(os.path.join(cm1_exp.output_dir, "word_distribution.txt"), 'w', encoding='utf8') as distrib_fout:
        for word_weight in word_weights:
            word = word_weight[0]
            s_art_contain_wd, t_art_contain_wd = cm1_exp.word_distribution(word)
            s_art_cnt = 0
            t_art_cnt = 0
            for item in s_art_contain_wd:
                s_art_cnt += item[1]
            for item in t_art_contain_wd:
                t_art_cnt += item[1]
            distrib_fout.write(word + "|||" + str(s_art_cnt) + "," + str(t_art_cnt) + "|||")
            distrib_fout.write(str(s_art_contain_wd))
            distrib_fout.write(str(t_art_contain_wd) + "\n")

            gold_link_contain_wd = []
            gold_links = set(cm1_exp.gold_links)
            for s_art in s_art_contain_wd:
                art_id = s_art[0]
                gold_link_contain_wd.extend(link_with_artifact(gold_links, art_id))
            for t_art in t_art_contain_wd:
                art_id = t_art[0]
                gold_link_contain_wd.extend(link_with_artifact(gold_links, art_id))

            gen_link_contain_wd = []
            gen_links = set(cm1_exp.gen_links)
            for s_art in s_art_contain_wd:
                art_id = s_art[0]
                gen_link_contain_wd.extend(link_with_artifact(gen_links, art_id))
            for t_art in t_art_contain_wd:
                art_id = t_art[0]
                gen_link_contain_wd.extend(link_with_artifact(gen_links, art_id))
            gen_in_gold = [x for x in gen_link_contain_wd if x in gold_link_contain_wd]

            gen_links = sorted(gen_links, key=lambda k: k[2], reverse=True)
            gen_in_gold = sorted(gen_in_gold, key=lambda k: k[2], reverse=True)
            link_fout.write(word + "|||")
            link_fout.write(str(len(gold_links)) + "|||")
            link_fout.write(str(gold_links) + "\n")
    cm1_exp.write_list(cm1_exp.gen_links, os.path.join(cm1_exp.output_dir, "gen_links.txt"))

    with open(os.path.join(cm1_exp.output_dir, "gen_links.txt"), 'w', encoding='utf8') as link_fout:
        for item in cm1_exp.gen_links:
            if (item[0], item[1]) in gold_links:
                link_fout.write("*")
            link_fout.write(str(item) + "\n")


def run_maven():
    maven_exp = Maven_Experiment()
    maven_exp.replace_words_in_target_artifacts()
    maven_exp.get_impacted_links()

    vsm = VSM(fo_lang_code="en")
    vsm.build_model(maven_exp.get_docs())
    maven_exp.run_origin_model(vsm)

    vsm_replace = VSM(fo_lang_code="en")
    vsm_replace.build_model(maven_exp.get_docs())

    maven_exp.run_replaced_model(vsm_replace)

    maven_exp.eval_and_compare()



def run_cm1_exp2_VSM():
    """
    Based on Jane's suggestion: evaluate the result on the impacted artifacts only
    :return:
    """
    cm1_exp2 = CM1_Experiment2(word_threshold=90)
    # cm1_exp2.select_word_all_doc_threshold()
    cm1_exp2.replace_words_in_target_artifacts()
    cm1_exp2.get_impacted_links()

    vsm = VSM(fo_lang_code="en")
    vsm.build_model(cm1_exp2.get_docs())

    vsm_replace = VSM(fo_lang_code="en")
    vsm_replace.build_model(cm1_exp2.get_docs())

    cm1_exp2.run_origin_model(vsm)
    cm1_exp2.run_replaced_model(vsm_replace)

    cm1_exp2.eval_and_compare()


def run_cm1_exp2_LDA():
    """
    Based on Jane's suggestion: evaluate the result on the impacted artifacts only
    :return:
    """
    cm1_exp2 = CM1_Experiment2(word_threshold=70)
    # cm1_exp2.select_word_all_doc_threshold()
    cm1_exp2.replace_words_in_target_artifacts()
    cm1_exp2.get_impacted_links()

    vsm = LDA(fo_lang_code="en")
    vsm.train(cm1_exp2.get_docs(), num_topics=20)

    vsm_replace = LDA(fo_lang_code="en")
    vsm_replace.train(cm1_exp2.get_docs(), num_topics=20)

    cm1_exp2.run_origin_model(vsm)
    cm1_exp2.run_replaced_model(vsm_replace)

    cm1_exp2.eval_and_compare()


if __name__ == "__main__":
    run_maven()
    # run_cm1_exp("high_occurance.txt")
    # run_cm1_exp2_LDA()
