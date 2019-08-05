from common import *
import xml.etree.ElementTree as ET

from github_project_crawl.github_script import sentence_contains_foreign_lang
from reborn.Datasets import ArtifactPair, LinkSet, Dataset
from datetime import datetime


class CM1Reader:
    def __init__(self):
        pass

    def __read_artifact(self, path):
        res = dict()
        tree = ET.parse(path)
        root = tree.getroot()
        for artifact in root.iter('artifact'):
            id = artifact.find("id").text
            content = artifact.find("content").text
            res[id] = content
        return res

    def readData(self):
        source_path = os.path.join(DATA_DIR, "cm1", "CM1-sourceArtifacts.xml")
        target_path = os.path.join(DATA_DIR, "cm1", "CM1-targetArtifacts.xml")
        answer_path = os.path.join(DATA_DIR, "cm1", "CM1-answerSet.xml")

        sourceArtifact = self.__read_artifact(source_path)
        targetArtifact = self.__read_artifact(target_path)
        links = set()

        tree = ET.parse(answer_path)
        root = tree.getroot()
        for artifact in root.iter('link'):
            source_id = artifact.find("source_artifact_id").text
            target_id = artifact.find("target_artifact_id").text
            links.add((source_id, target_id))
        artif_pair = ArtifactPair(sourceArtifact, "cm1Source", targetArtifact, "cm1Target")
        link_set = LinkSet(artif_pair, links)
        return Dataset([link_set])


class EzCLinizReader:
    def __init__(self):
        pass

    def readData(self):
        data_dir_path = os.path.join(DATA_DIR, "EasyClinicDataset", "2 - docs (English)")
        aritfacts_dirs = os.listdir(data_dir_path)

        arti_name_convert = {"1 - use cases": "UC", "2 - Interaction diagrams": "ID", "3 - test cases": "TC",
                             "4 - class description": "CC"}

        artifact_dict = dict()
        link_sets = []

        for artifact_dir in aritfacts_dirs:
            artif_code = arti_name_convert[artifact_dir]
            artifact_dir = os.path.join(data_dir_path, artifact_dir)
            tmp_dict = dict()
            for artifact_file in os.listdir(artifact_dir):
                file_path = os.path.join(data_dir_path, artifact_dir, artifact_file)
                with open(file_path, encoding='utf8', errors="ignore") as fin:
                    content = fin.read()
                    id = artifact_file.replace(".txt", "")
                    tmp_dict[id] = content
            artifact_dict[artif_code] = tmp_dict

        oracle_dir = os.path.join(data_dir_path, "..", "oracle")
        for link_file in os.listdir(oracle_dir):
            artif_type_codes = link_file.strip(".txt").split("_")
            source_code = artif_type_codes[0]
            target_code = artif_type_codes[1]
            links = []
            with open(os.path.join(oracle_dir, link_file)) as fin:
                for line in fin:
                    parts = line.split(":")
                    from_artif = parts[0]
                    to_artifs = parts[1].split()
                    for to_artif in to_artifs:
                        from_artif_id = from_artif.strip(".txt")
                        to_artif_id = to_artif.strip(".txt")
                        links.append((from_artif_id, to_artif_id))
            artif_pair = ArtifactPair(artifact_dict[source_code], source_code, artifact_dict[target_code], target_code)
            link_set = LinkSet(artif_pair, links)
            link_sets.append(link_set)
        return Dataset(link_sets)


class MavenReader:
    def __init__(self):
        pass

    def read_link(self, path):
        links = []
        raw_links = self.read_csv(path, 0, 1)
        for source_artifact in raw_links.keys():
            target_artifact = raw_links[source_artifact]
            links.append((source_artifact, target_artifact))
        return links

    def read_csv(self, path, id_index, content_index):
        res = dict()
        with open(path) as fin:
            cnt = 0
            for line in fin:
                cnt += 1
                if cnt == 1:
                    continue
                parts = line.split(",")
                id = parts[id_index]
                content = parts[content_index]
                res[id] = content
        return res

    def __read_code(self, data_dir_path):
        id_path = self.read_csv(os.path.join(data_dir_path, "code.csv"), 0, 1)
        artifact_code = dict()
        for id in id_path:
            path = id_path[id].strip("\n")
            path = os.path.join(data_dir_path, path)
            with open(path) as fin:
                content = fin.read()
            artifact_code[id] = content
        return artifact_code

    def readData(self):
        data_dir_path = os.path.join(DATA_DIR, "maven")
        artifact_bug = self.read_csv(os.path.join(data_dir_path, "bug.csv"), 0, 3)
        artifact_commit = self.read_csv(os.path.join(data_dir_path, "commits.csv"), 0, 2)
        artifact_improvement = self.read_csv(os.path.join(data_dir_path, "improvement.csv"), 0, 3)
        artifact_code = self.__read_code(data_dir_path)

        bug_commit_links = self.read_link(os.path.join(data_dir_path, "bugCommitLinks.csv"))
        commit_code_links = self.read_link(os.path.join(data_dir_path, "CommitCodeLinks.csv"))
        improvement_commit_links = self.read_link(os.path.join(data_dir_path, "improvementCommitLinks.csv"))

        bug_commit_pair = ArtifactPair(artifact_bug, "bug", artifact_commit, "commit")
        commit_code_pair = ArtifactPair(artifact_commit, "commit", artifact_code, "code")
        improvement_commit_pair = ArtifactPair(artifact_improvement, "improvement", artifact_commit, "commit")

        bug_commit_set = LinkSet(bug_commit_pair, bug_commit_links)
        commit_code_set = LinkSet(commit_code_pair, commit_code_links)
        improvement_commit_set = LinkSet(improvement_commit_pair, improvement_commit_links)

        link_sets = [bug_commit_set, commit_code_set, improvement_commit_set]
        return Dataset(link_sets)


import json


class DronologyReader:
    def __init__(self):
        pass

    def read_artifacts(self) -> dict:
        pass

    def readData(self):
        file_path = os.path.join(DATA_DIR, "dronology", "dronologydataset.json")
        with open(file_path, encoding='utf8') as fin:
            content = fin.read();
        jsonObj = json.loads(content);
        re_dict = dict()
        dd_dict = dict()
        links = []

        for entry in jsonObj["entries"]:
            id = entry["issueid"]
            attrib_dict = entry["attributes"]
            issueType = attrib_dict['issuetype']
            summary = attrib_dict["summary"].lower()
            description = attrib_dict["description"].lower()
            if issueType == "Design Definition":
                dd_dict[id] = summary + "," + description
            if issueType == "Requirement":
                re_dict[id] = summary + "," + description
                if "children" in entry:
                    children_dict = entry["children"]
                    if "refinedby" in children_dict:
                        refined_by_list = children_dict["refinedby"]
                        for dd in refined_by_list:
                            if dd.startswith("DD"):
                                links.append((id, dd))
        artif_pair = ArtifactPair(re_dict, "re", dd_dict, "dd")
        for link in links:
            if link[0] not in re_dict:
                print(link[0])
        for link in links:
            if link[1] not in dd_dict:
                print(link[1])
        return Dataset([LinkSet(artif_pair, links)])


class GtiProjectReader:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def isIL(self, source_content: str, target_content: str) -> bool:
        if sentence_contains_foreign_lang(source_content) or sentence_contains_foreign_lang(target_content):
            return True
        else:
            return False

    def limit_artifacts_in_links(self, dataset: Dataset, origin_dataset: Dataset):
        """
        Remove the artifacts which did not appear in the golden links
        :param dataset:
        :return:
        """
        modified_link_sets = []
        data_set_infos = []
        for linkset_id in dataset.gold_link_sets:
            link_set: LinkSet = dataset.gold_link_sets[linkset_id]
            source_dict: dict = link_set.artiPair.source_artif
            target_dict: dict = link_set.artiPair.target_artif
            links = link_set.links

            gold_artif_set = set()

            # Fix for the bug when read translated data. Translated data have no Chinese at all
            origin_source_dict = origin_dataset.gold_link_sets[linkset_id].artiPair.source_artif
            origin_target_dict = origin_dataset.gold_link_sets[linkset_id].artiPair.target_artif
            links = [x for x in links if (self.isIL(origin_source_dict[x[0]], origin_target_dict[x[1]]))]

            print(len(links))

            for (s, t) in links:
                gold_artif_set.add(s)
                gold_artif_set.add(t)

            limited_source_dict = dict()
            for s_art in source_dict.keys():
                if s_art in gold_artif_set:
                    limited_source_dict[s_art] = source_dict[s_art]
            limited_target_dict = dict()
            for t_art in target_dict.keys():
                if t_art in gold_artif_set:
                    limited_target_dict[t_art] = target_dict[t_art]
            modified_artif_pair = ArtifactPair(limited_source_dict, link_set.artiPair.source_name, limited_target_dict,
                                               link_set.artiPair.target_name)
            modified_artif_pair.source_artif_extra_info = link_set.artiPair.source_artif_extra_info
            modified_artif_pair.target_artif_extra_info = link_set.artiPair.target_artif_extra_info
            # Keep the extra information
            modified_link_sets.append(LinkSet(modified_artif_pair, links))
            issue_num = len(modified_artif_pair.source_artif)
            commit_num = len(modified_artif_pair.target_artif)
            issue_commit_info = "{} issues and {} commits remains after limiting artifacts to links...".format(
                issue_num, commit_num)
            data_set_infos.append(issue_commit_info)
            # print(issue_commit_info)
            candidate_num = issue_num * commit_num
            base_accuracy = 0
            if candidate_num > 0:
                base_accuracy = len(links) / candidate_num
            # print("Baseline accuracy is {}/{} = {}".format(len(links), candidate_num, base_accuracy))
        return Dataset(modified_link_sets), "\n".join(data_set_infos)

    def link_comply_with_time_constrain(self, issue_close_time_str, commit_time_str) -> bool:
        """
        This rule will only impact 100 gold links
        :param issue_close_time_str:
        :param commit_time_str:
        :return:
        """
        if issue_close_time_str == 'None' or issue_close_time_str is None:  # If issue is still open, we assume it connect with no commit
            return False
        issue_close = datetime.strptime(issue_close_time_str.split()[0], '%Y-%m-%d')  # 2018-10-16 01:48:56
        commit_create = datetime.strptime(commit_time_str.split()[0], '%Y-%m-%d')  # 2018-10-26 20:06:02+08:00
        if (issue_close < commit_create):
            return False
        return True

    def __readData(self, issue_path, commit_path, link_path, do_filter=True):
        def all_english(content: str) -> bool:
            def get_en(doc):
                pattern = re.compile("[a-zA-Z]+")
                res = pattern.findall(doc)
                return res

            return len(get_en(content)) == len(content.split())

        issues = dict()
        commits = dict()
        issue_close_time_dict = dict()
        issue_create_time_dict = dict()
        commit_time_dict = dict()
        MIN_DOC_SIZE = 15
        filtered_issued = 0
        filtered_commit = 0
        with open(issue_path, encoding='utf8') as fin:
            for i, line in enumerate(fin):
                if i == 0:
                    continue
                id, content, close_time, create_time = line.strip("\n\t\r").split(",")
                if (len(content.split()) < MIN_DOC_SIZE) and do_filter:
                    filtered_issued += 1
                    continue
                issues[id] = content
                issue_close_time_dict[id] = close_time
                issue_create_time_dict[id] = create_time

        # print("{} issues are filtered with minimal lenght {}...".format(filtered_issued, MIN_DOC_SIZE,
        #                                                                 len(issues)))
        with open(commit_path, encoding='utf8') as fin:
            for i, line in enumerate(fin):
                if i == 0:
                    continue
                id, summary, content, commit_time_info = line.strip("\n\t\r").split(",")
                commit_content = summary + content
                if (len(commit_content.split()) < MIN_DOC_SIZE) and do_filter:
                    filtered_commit += 1
                    continue
                commits[id] = commit_content
                commit_time_dict[id] = commit_time_info
        # print("{} commit are filtered minimal lenght {}".format(filtered_commit, MIN_DOC_SIZE, len(commits)))
        artif_pair = ArtifactPair(issues, "issues", commits, "commits")
        issue_time_info = {}
        commit_time_info = {}
        issue_time_info["create"] = issue_create_time_dict
        issue_time_info["close"] = issue_close_time_dict
        commit_time_info["create"] = commit_time_dict
        artif_pair.source_artif_extra_info = issue_time_info
        artif_pair.target_artif_extra_info = commit_time_info

        links = []
        origin_link_cnt = 0
        with open(link_path) as fin:
            for i, line in enumerate(fin):
                if i == 0:
                    continue
                origin_link_cnt = i
                issue_id, commit_id = line.split(",")
                issue_id = issue_id.strip("\n\t\r")
                commit_id = commit_id.strip("\n\t\r")
                if do_filter:
                    if issue_id not in issues or commit_id not in commits:
                        continue
                    issue_content = issues[issue_id]
                    commit_content = commits[commit_id]
                    if all_english(issue_content) and all_english(commit_content):
                        continue
                link = (issue_id, commit_id)
                links.append(link)
        # print("Link size:{}/{}".format(len(links), origin_link_cnt))
        link_set = LinkSet(artif_pair, links)
        return Dataset([link_set])

    def readData(self, use_translated_data=False, do_filter_on_raw=True) -> Dataset:
        """

        :param use_translated_data: use the translated dataset or origin dataset
        :param do_filter_on_raw: whether applying filtering condition on origin dataset. The filtering operation will be
         mirrored to the translated dataset.
        :return:
        """
        issue_path = os.path.join(GIT_PROJECTS, self.repo_path, "clean_token_data", "issue.csv")
        commit_path = os.path.join(GIT_PROJECTS, self.repo_path, "clean_token_data", "commit.csv")
        link_path = os.path.join(GIT_PROJECTS, self.repo_path, "links.csv")
        origin_dataset = self.__readData(issue_path, commit_path, link_path, do_filter_on_raw)
        if use_translated_data:
            issue_path = os.path.join(GIT_PROJECTS, self.repo_path, "translated_data", "clean_translated_tokens",
                                      "issue.csv")
            commit_path = os.path.join(GIT_PROJECTS, self.repo_path, "translated_data", "clean_translated_tokens",
                                       "commit.csv")
            trans_dataset = self.__readData(issue_path, commit_path, link_path, do_filter=False)
            # map the translated gold linkset back to origin datset, any filtering on origin dataset will reflect on trans dataset
            for link_set_id in trans_dataset.gold_link_sets:
                origin_link_set: LinkSet = origin_dataset.gold_link_sets[link_set_id]
                trans_link_set: LinkSet = trans_dataset.gold_link_sets[link_set_id]

                trans_link_set.links = origin_link_set.links
                remove_elements = []
                for s_id in trans_link_set.artiPair.source_artif:
                    if s_id not in origin_link_set.artiPair.source_artif:
                        remove_elements.append(s_id)
                for s_id in remove_elements:
                    del trans_link_set.artiPair.source_artif[s_id]
                remove_elements = []
                for t_id in trans_link_set.artiPair.target_artif:
                    if t_id not in origin_link_set.artiPair.target_artif:
                        remove_elements.append(t_id)
                for t_id in remove_elements:
                    del trans_link_set.artiPair.target_artif[t_id]
            return trans_dataset
        else:
            return origin_dataset


class Exp3DataReader:
    def __init__(self, git_dir, repo_path):
        self.repo_path = repo_path
        self.git_dir = git_dir

    def limit_artifacts_in_links(self, dataset: Dataset):
        """
        Remove the artifacts which did not appear in the golden links
        :param dataset:
        :return:
        """
        modified_link_sets = []
        data_set_infos = []
        for linkset_id in dataset.gold_link_sets:
            link_set: LinkSet = dataset.gold_link_sets[linkset_id]
            source_dict: dict = link_set.artiPair.source_artif
            target_dict: dict = link_set.artiPair.target_artif
            links = link_set.links

            gold_artif_set = set()
            for (s, t) in links:
                gold_artif_set.add(s)
                gold_artif_set.add(t)

            limited_source_dict = dict()
            for s_art in source_dict.keys():
                if s_art in gold_artif_set:
                    limited_source_dict[s_art] = source_dict[s_art]
            limited_target_dict = dict()
            for t_art in target_dict.keys():
                if t_art in gold_artif_set:
                    limited_target_dict[t_art] = target_dict[t_art]
            modified_artif_pair = ArtifactPair(limited_source_dict, link_set.artiPair.source_name, limited_target_dict,
                                               link_set.artiPair.target_name)
            # Keep the extra information
            modified_link_sets.append(LinkSet(modified_artif_pair, links))
            issue_num = len(modified_artif_pair.source_artif)
            commit_num = len(modified_artif_pair.target_artif)
            issue_commit_info = "{} issues and {} commits remains after limiting artifacts to links...".format(
                issue_num, commit_num)
            data_set_infos.append(issue_commit_info)
            # print(issue_commit_info)
            candidate_num = issue_num * commit_num
            base_accuracy = 0
            if candidate_num > 0:
                base_accuracy = len(links) / candidate_num
            # print("Baseline accuracy is {}/{} = {}".format(len(links), candidate_num, base_accuracy))
        return Dataset(modified_link_sets), "\n".join(data_set_infos)

    def link_comply_with_time_constrain(self, issue_close_time_str, commit_time_str) -> bool:
        """
        This rule will only impact 100 gold links
        :param issue_close_time_str:
        :param commit_time_str:
        :return:
        """
        if issue_close_time_str == 'None' or issue_close_time_str is None:  # If issue is still open, we assume it connect with no commit
            return False
        issue_close = datetime.strptime(issue_close_time_str.split()[0], '%Y-%m-%d')  # 2018-10-16 01:48:56
        commit_create = datetime.strptime(commit_time_str.split()[0], '%Y-%m-%d')  # 2018-10-26 20:06:02+08:00
        if (issue_close < commit_create):
            return False
        return True

    def __readData(self, issue_path, commit_path, link_path, do_filter=True):
        def all_english(content: str) -> bool:
            def get_en(doc):
                pattern = re.compile("[a-zA-Z]+")
                res = pattern.findall(doc)
                return res

            return len(get_en(content)) == len(content.split())

        issues = dict()
        commits = dict()
        issue_close_time_dict = dict()
        commit_time_dict = dict()
        MIN_DOC_SIZE = 15
        filtered_issued = 0
        filtered_commit = 0
        with open(issue_path, encoding='utf8') as fin:
            for i, line in enumerate(fin):
                if i == 0:
                    continue
                id, content, close_time = line.strip("\n\t\r").split(",")
                if (len(content.split()) < MIN_DOC_SIZE) and do_filter:
                    filtered_issued += 1
                    continue
                issues[id] = content
                issue_close_time_dict[id] = close_time

        # print("{} issues are filtered with minimal lenght {}...".format(filtered_issued, MIN_DOC_SIZE,
        #                                                                 len(issues)))
        with open(commit_path, encoding='utf8') as fin:
            for i, line in enumerate(fin):
                if i == 0:
                    continue
                id, summary, content, commit_time = line.strip("\n\t\r").split(",")
                commit_content = summary + content
                if (len(commit_content.split()) < MIN_DOC_SIZE) and do_filter:
                    filtered_commit += 1
                    continue
                commits[id] = commit_content
                commit_time_dict[id] = commit_time
        # print("{} commit are filtered minimal lenght {}".format(filtered_commit, MIN_DOC_SIZE, len(commits)))
        artif_pair = ArtifactPair(issues, "issues", commits, "commits")

        links = []
        origin_link_cnt = 0
        with open(link_path) as fin:
            for i, line in enumerate(fin):
                if i == 0:
                    continue
                origin_link_cnt = i
                issue_id, commit_id = line.split(",")
                issue_id = issue_id.strip("\n\t\r")
                commit_id = commit_id.strip("\n\t\r")
                if issue_id not in issues or commit_id not in commits:
                    continue
                link = (issue_id, commit_id)
                links.append(link)
        # print("Link size:{}/{}".format(len(links), origin_link_cnt))
        link_set = LinkSet(artif_pair, links)
        return Dataset([link_set])

    def readData(self, use_translated_data=False, do_filter_on_raw=True) -> Dataset:
        """

        :param use_translated_data: use the translated dataset or origin dataset
        :param do_filter_on_raw: whether applying filtering condition on origin dataset. The filtering operation will be
         mirrored to the translated dataset.
        :return:
        """
        issue_path = os.path.join(self.git_dir, self.repo_path, "clean_token_data", "issue.csv")
        commit_path = os.path.join(self.git_dir, self.repo_path, "clean_token_data", "commit.csv")
        link_path = os.path.join(self.git_dir, self.repo_path, "links.csv")
        origin_dataset = self.__readData(issue_path, commit_path, link_path, do_filter=False)
        if use_translated_data:
            issue_path = os.path.join(self.git_dir, self.repo_path, "en_trans", "clean_translated_tokens",
                                      "issue.csv")
            commit_path = os.path.join(self.git_dir, self.repo_path, "en_trans", "clean_translated_tokens",
                                       "commit.csv")
            trans_dataset = self.__readData(issue_path, commit_path, link_path, do_filter=False)
            # map the translated gold linkset back to origin datset, any filtering on origin dataset will reflect on trans dataset
            for link_set_id in trans_dataset.gold_link_sets:
                origin_link_set: LinkSet = origin_dataset.gold_link_sets[link_set_id]
                trans_link_set: LinkSet = trans_dataset.gold_link_sets[link_set_id]

                trans_link_set.links = origin_link_set.links
                remove_elements = []
                for s_id in trans_link_set.artiPair.source_artif:
                    if s_id not in origin_link_set.artiPair.source_artif:
                        remove_elements.append(s_id)
                for s_id in remove_elements:
                    del trans_link_set.artiPair.source_artif[s_id]
                remove_elements = []
                for t_id in trans_link_set.artiPair.target_artif:
                    if t_id not in origin_link_set.artiPair.target_artif:
                        remove_elements.append(t_id)
                for t_id in remove_elements:
                    del trans_link_set.artiPair.target_artif[t_id]
            return trans_dataset
        else:
            return origin_dataset


if __name__ == "__main__":
    mr = DronologyReader()
    data = mr.readData()
    pass
