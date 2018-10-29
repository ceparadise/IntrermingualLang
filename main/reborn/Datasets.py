import pickle
import math

from reborn.Preprocessor import Preprocessor


class Dataset:
    """
    One dataset contains multiple artifact pairs that have links between them.
    """

    def __init__(self, gold_link_sets, round_digit_num=4):
        # Index the gold link sets by their id
        self.gold_link_sets = dict()
        for link_set in gold_link_sets:
            self.gold_link_sets[link_set.get_pair_id()] = link_set

        self.round_digit_num = round_digit_num

    def get_impacted_dataSet(self, replace_list):
        impacted_link_sets = []
        for link_set_id in self.gold_link_sets.keys():
            link_set = self.gold_link_sets[link_set_id]
            impacted_link_set = link_set.gen_impacted_linkSet(replace_list)  # difference here
            impacted_link_sets.append(impacted_link_set)
        return Dataset(impacted_link_sets)

    def get_replaced_dataSet(self, replace_list):
        """
        Replace part of the english tokens with the given replace list. The data size is equal to origin dataset
        :param replace_list:
        :return:
        """
        replaced_link_sets = []
        for link_set_id in self.gold_link_sets.keys():
            link_set = self.gold_link_sets[link_set_id]
            replaced_link_set = link_set.gen_replaced_linkSet(replace_list)  # difference here
            replaced_link_sets.append(replaced_link_set)
        return Dataset(replaced_link_sets)

    def evaluate_link_set(self, gold_link_set_id, eval_link_set):
        """
        Evaluate a set of generate links set against one gold link set by giving the link set id
        :param gold_link_set_id:
        :param eval_link_set:
        :return:
        """
        gold_link_set = self.gold_link_sets[gold_link_set_id]

        gen_links_no_score = set([(x[0], x[1]) for x in eval_link_set])
        gold_links = set(gold_link_set.links)
        tp = len(gen_links_no_score & gold_links)
        fp = len(gen_links_no_score - gold_links)
        fn = len(gold_links - gen_links_no_score)
        total_num = len(gold_link_set.artiPair.source_artif) * len(gold_link_set.artiPair.target_artif)
        tn = total_num - len(gen_links_no_score | gold_links)
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
        return round(precision, self.round_digit_num), \
               round(recall, self.round_digit_num), \
               round(f1, self.round_digit_num)

    def get_docs(self):
        docs = []
        for link_set in self.gold_link_sets:
            docs.extend(self.gold_link_sets[link_set].get_docs())
        return docs

    def save(self, path):
        with open(path, 'wb') as fout:
            pickle.dumps(self.gold_link_sets, fout)

    def load(self, path):
        with open(path) as fin:
            self.gold_link_sets = pickle.load(fin)


class ArtifactPair:
    """
    Each artifactPair contains 2 type of artifacts in the dataset that can have links in between.
    It only holds the artifact contents
    """

    def __init__(self, source_artif, source_name, target_artif, target_name):
        """

        :param source_artif: a dictionary key is the artifact id , value is the artifact content
        :param source_name: the type of source artifact
        :param target_artif: like wise
        :param target_name:  like wise
        """
        self.source_name = source_name
        self.target_name = target_name
        self.source_artif = source_artif
        self.target_artif = target_artif

    def get_pair_id(self):
        return self.source_name + "-" + self.target_name

    def get_source_size(self):
        return len(self.source_artif)

    def get_target_size(self):
        return len(self.target_artif)


class LinkSet:
    """
    The links between 2 types of artifacts
    """

    def __init__(self, artiPair: ArtifactPair, links):
        self.artiPair = artiPair
        self.links = links
        self.replacement_info = ""
        self.preprocessor = Preprocessor()

    def get_pair_id(self):
        return self.artiPair.get_pair_id()

    def gen_replaced_linkSet(self, replace_dict):
        replaced_artifacts_dict = dict()
        for arti_id in self.artiPair.source_artif:
            replaced_artifacts_dict[arti_id] = self.replace_tokens(self.artiPair.source_artif[arti_id], replace_dict)
        replaced_arti_pair = ArtifactPair(replaced_artifacts_dict, self.artiPair.source_name,
                                          self.artiPair.target_artif,
                                          self.artiPair.target_name)
        return LinkSet(replaced_arti_pair, self.links)

    def gen_impacted_linkSet(self, replace_dict):
        """
        Generate a dateaset that only contains impacted artifacts and links. This dataset is used for evaluation only.
        The model should run on a dataset which do the replacement but kept all links and artifacts.
        :param replace_dict:
        :return:
        """
        impacted_artifacts_dict = dict()
        for arti_id in self.get_impacted_artifacts(replace_dict):
            impacted_artifacts_dict[arti_id] = self.replace_tokens(self.artiPair.source_artif[arti_id], replace_dict)
        impacted_arti_pair = ArtifactPair(impacted_artifacts_dict, self.artiPair.source_name,
                                          self.artiPair.target_artif,
                                          self.artiPair.target_name)
        impacted_links = self.get_impacted_links(replace_dict)
        return LinkSet(impacted_arti_pair, impacted_links)

    def replace_tokens(self, content, replace_dict):
        tokens = set(self.preprocessor.get_tokens(content))
        replaced_content = []

        for token in tokens:
            if token in replace_dict:
                fo_word = replace_dict[token]
                replaced_content.append(fo_word)
            else:
                replaced_content.append(token)
        return " ".join(replaced_content)

    def get_impacted_artifacts(self, replace_dict):
        impacted = set()
        replace_dict = set(replace_dict.keys())
        for artif in self.artiPair.source_artif:
            content = self.artiPair.source_artif[artif]
            tokens = set(self.preprocessor.get_tokens(content))
            if len(tokens & replace_dict) > 0:
                impacted.add(artif)
        return impacted

    def get_impacted_links(self, replace_wd_list):
        impacted_artifacts = self.get_impacted_artifacts(replace_wd_list)
        impacted_links = []
        impacted_artifact_info = "{} source artifacts out of {} artifacts are impacted ...".format(
            len(impacted_artifacts),
            len(self.artiPair.source_artif))

        for link in self.links:
            if link[0] in impacted_artifacts or link[1] in impacted_artifacts:
                impacted_links.append(link)
        impacted_link_info = str(
            len(impacted_links)) + " links are impacted by the replacement, total links num=" + str(
            len(self.links))
        self.replacement_info = impacted_artifact_info + "\n" + impacted_link_info
        print(self.replacement_info)
        return impacted_links

    def get_docs(self):
        docs = []
        for a in self.artiPair.source_artif:
            docs.append(self.artiPair.source_artif[a])
        for a in self.artiPair.target_artif:
            docs.append(self.artiPair.target_artif[a])
        return docs


class MAP_cal:
    def __init__(self, rank, gold, round_digit_num=4, do_sort=True):
        self.round_digit_num = round_digit_num
        self.rank_gold_pairs = []  # keep data for multiple experiments if necessary in future
        if do_sort:  # for performance consideration in case the the rank is and large and sorted already
            rank = sorted(rank, key=lambda k: k[2], reverse=True)
        rank = [(x[0], x[1], round(x[2], 5)) for x in rank]
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
            link = (rank[i][0], rank[i][1])
            if link in gold:
                hit += 1
        return hit / (num + 1)

    def __get_average_index(self, gold_link, ranks):
        """
        If multiple links share same score with the gold, then the index of the gold link should be averaged
        :return:
        """
        gold_index = 0
        gold_score = 0
        for i, link in enumerate(ranks):
            if (link[0], link[1]) == gold_link:
                gold_index = i
                gold_score = link[2]
                break
        left_index = gold_index
        right_index = gold_index
        while left_index >= 0 and ranks[left_index][2] == gold_score:
            left_index -= 1
        while right_index < len(ranks) and ranks[right_index][2] == gold_score:
            right_index += 1
        return math.floor((left_index + right_index) / 2)

    def average_precision(self, rank, gold):
        sum = 0
        if len(gold) == 0:
            return 0
        for g in gold:
            g_index = self.__get_average_index(g, rank)
            precision = self.precision(rank, gold, g_index)
            sum += precision
        return round(sum / len(gold), self.round_digit_num)

    def mean_average_precision(self, rank_gold_pairs):
        sum = 0
        for pair in rank_gold_pairs:
            rank = pair[0]
            gold = pair[1]
            average_precision = self.average_precision(rank, gold)
            sum += average_precision
        return round(sum / len(rank_gold_pairs), 3)

    def run(self):
        return self.mean_average_precision(self.rank_gold_pairs)
