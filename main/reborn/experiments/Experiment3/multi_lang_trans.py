import re

import common
import os
from shutil import copyfile
import json

from DataReader import GtiProjectReader
from Datasets import ArtifactPair

CHINESE_CHAR_PATTERN = re.compile("[\u4e00-\u9fff]+")


def trans_with_cache(content, lang):
    if content in trans_cache:
        fo_trans_content, en_trans_content = trans_cache[content]
    else:
        fo_trans_content, en_trans_content = translate_zh_intermingual_sentence(content, lang=lang)
        trans_cache[content] = (fo_trans_content, en_trans_content)
    return fo_trans_content, en_trans_content


def save_cache(path, in_dict):
    with open(path, 'w') as fout:
        fout.write(json.dumps(in_dict))


def load_cache(path):
    with open(path, 'r') as fin:
        res = json.loads(fin.read())
        return res


def trans_artifact(in_path, fo_out_path, en_out_path, lang, ids):
    with open(in_path, encoding='utf8') as fin, open(fo_out_path, "w", encoding='utf8') as fo_fout, \
            open(en_out_path, 'w', encoding='utf8') as en_fout:
        for i, line in enumerate(fin):
            if i == 0:
                fo_fout.write(line)
                en_fout.write(line)
                continue
            print(i)
            parts = line.strip("\n\t\r").split(",")
            if len(parts) == 3:
                issue_id, issue_content, issue_close_time = line.strip("\n\t\r").split(",")
                if issue_id not in ids:
                    continue
                fo_trans_content, en_trans_content = translate_zh_intermingual_sentence(issue_content, lang=lang)
                fo_trans_content = fo_trans_content.replace(",", " ")
                en_trans_content = en_trans_content.replace(",", " ")
                fo_fout.write("{},{},{}\n".format(issue_id, fo_trans_content, issue_close_time))
                en_fout.write("{},{},{}\n".format(issue_id, en_trans_content, issue_close_time))
            else:
                commit_id, commit_summary, commit_content, commit_time = line.strip("\n\t\r").split(",")
                if commit_id not in ids:
                    continue
                fo_trans_content, en_trans_content = translate_zh_intermingual_sentence(commit_content, lang=lang)
                fo_trans_summary, en_trans_summary = translate_zh_intermingual_sentence(commit_summary, lang=lang)

                fo_trans_content = fo_trans_content.replace(",", " ")
                en_trans_content = en_trans_content.replace(",", " ")
                fo_trans_summary = fo_trans_summary.replace(",", " ")
                en_trans_summary = en_trans_summary.replace(",", " ")

                fo_fout.write("{},{},{},{}\n".format(commit_id, fo_trans_summary, fo_trans_content, commit_time))
                en_fout.write("{},{},{},{}\n".format(commit_id, en_trans_summary, en_trans_content, commit_time))


def sentence_contains_chinese(sentence: str) -> bool:
    return CHINESE_CHAR_PATTERN.search(sentence) is not None


def translate_zh_intermingual_sentence(sentence: str, lang) -> tuple:
    """
    Find out the Chinese sentences in a long string, translate those parts and return a pure english version sentence
    of the input
    :param sentence:
    :return:
    """
    sentence_segments_by_space = sentence.split()
    fo_translated_sentence = []
    en_translated_sentence = []
    for sentence_segment in sentence_segments_by_space:
        if sentence_contains_chinese(sentence_segment):
            sentence_segment = re.sub("[^\w]+", " ", sentence_segment)
            if sentence_segment in trans_cache:
                fo_trans_segment, en_trans_segment = trans_cache[sentence_segment]
            else:
                fo_trans_segment = common.translate_long_sentence(sentence_segment, lang=lang)
                en_trans_segment = common.translate_long_sentence(fo_trans_segment, lang="en")
                trans_cache[sentence_segment] = (fo_trans_segment, en_trans_segment)
        else:
            fo_trans_segment = sentence_segment
            en_trans_segment = sentence_segment
        fo_translated_sentence.append(fo_trans_segment)
        en_translated_sentence.append(en_trans_segment)
    return " ".join(fo_translated_sentence), " ".join(en_translated_sentence)


if __name__ == "__main__":
    #target_lang_list = ["fr"]
    target_lang_list = common.language_list
    for target_lang in target_lang_list:
        cache_path = "cache/" + target_lang + ".txt"
        trans_cache = dict()
        if os.path.exists(cache_path):
            trans_cache = load_cache(cache_path)
        else:
            print("cache for {} is not found...".format(target_lang))
        for group_name in os.listdir(common.GIT_PROJECTS):
            group_dir_path = os.path.join(common.GIT_PROJECTS, group_name)
            for project_name in os.listdir(group_dir_path):
                print("Translating {} into {}".format(project_name, target_lang))
                # Read only the
                reader = GtiProjectReader(os.path.join(group_name, project_name))
                dataSet = reader.readData(use_translated_data=False)
                dataSet, dataset_info = reader.limit_artifacts_in_links(dataSet)
                artif_pair: ArtifactPair = list(dataSet.gold_link_sets.values())[0].artiPair
                source_artif = artif_pair.source_artif
                target_artif = artif_pair.target_artif

                source_ids = source_artif.keys()
                target_ids = target_artif.keys()

                project_dir_path = os.path.join(group_dir_path, project_name)
                raw_commit_file_path = os.path.join(project_dir_path, "commit.csv")
                raw_issue_file_path = os.path.join(project_dir_path, "issue.csv")
                raw_link_file_path = os.path.join(project_dir_path, "links.csv")
                translation_dir = os.path.join("data", target_lang, group_name, project_name)
                if not os.path.isdir(translation_dir):
                    os.makedirs(translation_dir)
                    fo_trans_commit_path = os.path.join(translation_dir, "commit.csv")
                    fo_trans_issue_path = os.path.join(translation_dir, "issue.csv")

                    en_trans_dir = os.path.join(translation_dir, "en_trans")
                    if not os.path.isdir(en_trans_dir):
                        os.mkdir(en_trans_dir)

                    en_trans_commit_path = os.path.join(en_trans_dir, "commit.csv")
                    en_trans_issue_path = os.path.join(en_trans_dir, "issue.csv")

                    trans_artifact(raw_commit_file_path, fo_trans_commit_path, en_trans_commit_path, target_lang,
                                   target_ids)
                    trans_artifact(raw_issue_file_path, fo_trans_issue_path, en_trans_issue_path, target_lang,
                                   source_ids)
                    copyfile(raw_link_file_path, os.path.join(translation_dir, "links.csv"))
        save_cache(cache_path, trans_cache)

    print("finished")
