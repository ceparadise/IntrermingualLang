from common import *
import xml.etree.ElementTree as ET
from .Datasets import Dataset, LinkSet, ArtifactPair


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

        arti_name_convert = {"1 - use cases": "UC", "2 - interaction diagrams": "ID", "3 - test cases": "TC",
                             "4 - class description": "CC"}

        artifact_dict = dict()
        link_sets = []

        for artifact_dir in aritfacts_dirs:
            artif_code = arti_name_convert[artifact_dir]
            tmp_dict = dict()
            for artifact_file in os.listdir(artifact_dir):
                file_path = os.path.join(data_dir_path, artifact_dir, artifact_file)
                with open(file_path, encoding='utf8', errors="ignore") as fin:
                    content = fin.read()
                    id = artifact_file.replace(".txt", "")
                    tmp_dict[id] = content
            artifact_dict[artif_code] = tmp_dict

        for link_file in os.listdir(os.path.join(DATA_DIR, "oracle")):
            artif_type_codes = link_file.strip(".txt").split("_")
            source_code = artif_type_codes[0]
            target_code = artif_type_codes[1]
            links = []
            with open(os.path.join(DATA_DIR, "oracle", link_file)) as fin:
                for line in fin:
                    parts = line.split(":")
                    from_artif = parts[0]
                    to_artifs = parts[1].split(",")
                    for to_artif in to_artifs:
                        from_artif_id = from_artif.strip(".txt")
                        to_artif_id = to_artif.strip(".txt")
                        links.append((from_artif_id, to_artif_id))
            artif_pair = ArtifactPair(artifact_dict[source_code], source_code, artifact_dict[target_code], target_code)
            link_set = LinkSet(artif_pair, links)
            link_sets.append(link_set)
        return Dataset(link_sets)

