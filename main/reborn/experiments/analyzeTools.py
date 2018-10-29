from Datasets import Dataset
from Preprocessor import Preprocessor


class Analyzer:
    def __init__(self):
        self.preprocessor = Preprocessor()

    def get_replaced_words(self, linkset_id, not_impact_dataset: Dataset, impacted_dataset: Dataset, gold_link):
        replace_info = {}
        gold_source_artif = gold_link[0]
        not_impacted_link_set = not_impact_dataset.gold_link_sets[linkset_id]
        impacted_link_set = impacted_dataset.gold_link_sets[linkset_id]

        not_impacted_source_artifs = not_impacted_link_set.artiPair.source_artif
        impacted_source_artifs = impacted_link_set.artiPair.source_artif

        origin_source_gold_tokens = set(self.preprocessor.get_tokens(not_impacted_source_artifs[gold_source_artif]))
        impacted_source_gold_tokens = set(self.preprocessor.get_tokens(impacted_source_artifs[gold_source_artif]))
        zh_replacement = [x for x in impacted_source_gold_tokens if x not in origin_source_gold_tokens]
        en_replacement = [x for x in origin_source_gold_tokens if x not in impacted_source_gold_tokens]
        replace_info = {}
        replace_info["link"] = gold_link
        replace_info["zh"] = zh_replacement
        replace_info["en"] = en_replacement
        return replace_info

    def get_changed_ranks(self, link_set_id, origin_result, impacted_result, origin_dataset: Dataset,
                          impacted_dataset: Dataset):
        """
        Find out the links whose score/rank is raised after foreign word replacement
        :param origin_result:
        :param impacted_result:
        :param gold:
        :return:
        """
        replace_infomations = []
        origin_result_link_set = origin_result
        impacted_result_link_set = impacted_result
        impacted_gold_links = impacted_dataset.gold_link_sets[link_set_id].links

        origin_res_dict = {}
        impacted_res_dict = {}
        for link in origin_result_link_set:
            link_body = (link[0], link[1])
            origin_res_dict[link_body] = link[2]
        for link in impacted_result_link_set:
            link_body = (link[0], link[1])
            impacted_res_dict[link_body] = link[2]

        for gold_link in impacted_gold_links:
            origin_score = origin_res_dict[gold_link]
            impacted_score = impacted_res_dict[gold_link]
            origin_rank = None
            impacted_rank = None
            if impacted_score > origin_score:
                replace_info = self.get_replaced_words(link_set_id, origin_dataset, impacted_dataset, gold_link)
                replace_info["origin_score"] = origin_score
                replace_info["impacted_score"] = impacted_score
                replace_infomations.append(replace_info)
        return replace_infomations
