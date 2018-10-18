class Dataset:
    """
    One dataset contains multiple artifact pairs that have links between them.
    """

    def __init__(self, link_sets):
        self.gold_link_sets = dict()
        for link_set in link_sets:
            self.gold_link_sets[link_set.get_pair_id()] = link_set

    def evaluate_link_set(self, gold_link_set_id, eva_link_set):
        gold_link_set = self.gold_link_sets[gold_link_set_id]
        gen_links = set(gold_link_set.links)
        gold_links = set(eva_link_set.links)
        tp = len(gen_links & gold_links)
        fp = len(gen_links - gold_links)
        fn = len(gold_links - gen_links)
        total_num = gold_link_set.artiType.get_source_size() * gold_link_set.artiType.get_target_size()
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

        map = MAP_cal(gold_links, gen_links)
        return precision, recall, f1, map.run()


class ArtifactPair:
    """
    Each artifactPair contains 2 type of artifacts in the dataset that can have links in between.
    It only holds the artifact contents
    """

    def __init__(self, source_artif, source_name, target_artif, target_name):
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
    Then links between 2 types of artifacts
    """

    def __init__(self, artiPair: ArtifactPair, links):
        self.artiPair = artiPair
        self.links = links

    def get_pair_id(self):
        return self.artiPair.get_pair_id()

    def get_impacted_artifacts(self, replace_list):
        impacted = set()
        replace_list = set(replace_list)
        for artif in self.artiPair.source_artif:
            content = self.artiPair.source_artif[artif]
            tokens = set(content.split())
            if len(tokens & replace_list)>0:
                impacted.add(artif)
        return impacted

    def get_impacted_links(self, replace_wd_list):
        impacted_artifacts = self.get_impacted_artifacts(replace_wd_list)
        impacted_links = []
        print("{} target artifacts out of {} artifacts are impacted ...".format(len(self.artiPair.target_artif),
                                                                                len(impacted_artifacts)))

        for link in self.links:
            if link[0] in impacted_artifacts or link[1] in impacted_artifacts:
                impacted_links.append(link)
        print(str(len(impacted_links)) + "links are impacted by the replacedment, total links num=" + str(
            len(self.links)))


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
