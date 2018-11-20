from common import *
import xml.etree.ElementTree as ET

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


class GtiProjectReader:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def limit_artifacts_in_links(self, dataset: Dataset):
        modified_link_sets = []
        for linkset_id in dataset.gold_link_sets:
            link_set: LinkSet = dataset.gold_link_sets[linkset_id]
            source_dict: dict = link_set.artiPair.source_artif
            target_dict: dict = link_set.artiPair.target_artif
            source_extra = link_set.artiPair.source_artif_extra_info
            target_extra = link_set.artiPair.target_artif_extra_info
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
            modified_artif_pair.source_artif_extra_info = source_extra
            modified_artif_pair.target_artif_extra_info = target_extra
            modified_link_sets.append(LinkSet(modified_artif_pair, links))
        return Dataset(modified_link_sets)

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

    def __readData(self, issue_path, commit_path, link_path):
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
                if len(content.split()) < MIN_DOC_SIZE:
                    filtered_issued += 1
                    continue
                issues[id] = content
                issue_close_time_dict[id] = close_time
        print("{} issues are filtered with minimal lenght {}...".format(filtered_issued, MIN_DOC_SIZE))
        with open(commit_path, encoding='utf8') as fin:
            for i, line in enumerate(fin):
                if i == 0:
                    continue
                id, summary, content, commit_time = line.strip("\n\t\r").split(",")
                commit_content = summary + content
                if len(commit_content.split()) < MIN_DOC_SIZE:
                    filtered_commit += 1
                    continue
                commits[id] = commit_content
                commit_time_dict[id] = commit_time
        print("{} commit are filtered minimal lenght {}...".format(filtered_commit, MIN_DOC_SIZE))
        artif_pair = ArtifactPair(issues, "issues", commits, "commits")
        artif_pair.source_artif_extra_info["issue_close_time_dict"] = issue_close_time_dict
        artif_pair.target_artif_extra_info["commit_time"] = commit_time_dict
        links = []

        all_english_cnt = 0

        with open(link_path) as fin:
            for i, line in enumerate(fin):
                if i == 0:
                    continue
                issue_id, commit_id = line.split(",")
                issue_id = issue_id.strip("\n\t\r")
                commit_id = commit_id.strip("\n\t\r")
                if issue_id not in issues or commit_id not in commits:
                    continue

                if all_english(issues[issue_id]) or all_english(commits[commit_id]):
                    all_english_cnt += 1
                    continue
                self.link_comply_with_time_constrain(issue_close_time_dict[issue_id], commit_time_dict[commit_id])
                link = (issue_id, commit_id)
                links.append(link)
        print("all english filter removed {} links".format(all_english_cnt))
        print("Link size:{}".format(len(links)))
        link_set = LinkSet(artif_pair, links)
        return Dataset([link_set])

    def readData(self, use_translated_data=False) -> Dataset:
        issue_path = os.path.join(GIT_PROJECTS, self.repo_path, "clean_token_data", "issue.csv")
        commit_path = os.path.join(GIT_PROJECTS, self.repo_path, "clean_token_data", "commit.csv")
        link_path = os.path.join(GIT_PROJECTS, self.repo_path, "links.csv")
        origin_dataset = self.__readData(issue_path, commit_path, link_path)
        if use_translated_data:
            issue_path = os.path.join(GIT_PROJECTS, self.repo_path, "translated_data", "clean_translated_tokens",
                                      "issue.csv")
            commit_path = os.path.join(GIT_PROJECTS, self.repo_path, "translated_data", "clean_translated_tokens",
                                       "commit.csv")
            trans_dataset = self.__readData(issue_path, commit_path, link_path)
            for link_set_id in trans_dataset.gold_link_sets:
                trans_dataset.gold_link_sets[link_set_id].links = origin_dataset.gold_link_sets[
                    link_set_id].links  # map the translated gold linkset back to origin datset, any filtering on origin dataset will reflect on trans dataset
            return trans_dataset
        else:
            return origin_dataset


if __name__ == "__main__":
    mr = MavenReader()
    data = mr.readData()
