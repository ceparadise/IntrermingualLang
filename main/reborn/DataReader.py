from common import *
import xml.etree.ElementTree as ET

from reborn.Datasets import ArtifactPair, LinkSet, Dataset


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


if __name__ == "__main__":
    mr = MavenReader()
    data = mr.readData()

