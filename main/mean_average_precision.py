class MAP_cal:
    def __init__(self, res_gold_file_pairs):
        self.rank_gold_pairs = []
        for file_pair in res_gold_file_pairs:
            res_file = file_pair[0]
            gold_file = file_pair[1]

            rank = []
            gold = []
            with open(res_file, encoding='utf8') as fin:
                rank_dict = dict()
                for line in fin:
                    parts = line.split(",")
                    link = (parts[0], parts[1])
                    score = (parts[2])
                    rank_dict[link] = score
                rank = sorted(rank_dict.items(), key=lambda item: item[1], reverse=True)
                rank = [x[0] for x in rank]

            with open(gold_file, encoding='utf8') as fin:
                for line in fin:
                    parts = line.split(",")
                    link = (parts[0].strip("\"\'\n"), parts[1].strip("\n\"\'"))
                    gold.append(link)

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

if __name__ == "__main__":
    file_pairs = []
    uc_cc_vsm  = "G:/Projects/InterLingualTrace/output/0_EasyClinic_50.0%/zh/UC_CC_VSM.links"
    uc_cc_tr_vsm = "G:/Projects/InterLingualTrace/output/0_EasyClinic_50.0%/zh/UC_CC_TR-VSM.links"
    gold = "G:/Projects/InterLingualTrace/output/map_cal/UC_CC.csv"


    file_pairs.append((uc_cc_vsm,gold))
    map = MAP_cal(file_pairs)
    print(map.run())

    file_pairs = []
    file_pairs.append((uc_cc_tr_vsm,gold))
    map = MAP_cal(file_pairs)
    print(map.run())
    # map = MAP_cal("", "")
    # rank = [str(i) for i in range(10)]
    # gold = ['1','4','6']
    # for i in range(10):
    #     print(map.recall(rank, gold, i), map.precision(rank, gold, i))
    # print(map.average_precision(rank,gold))
