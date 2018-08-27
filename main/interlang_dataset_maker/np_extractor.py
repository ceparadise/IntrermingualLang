import os
from subprocess import Popen, PIPE

from nltk import CoreNLPParser
import re


class np_extractor:
    def __init__(self, corpus_dir, output_dir):
        self.corpus_dir = corpus_dir
        self.noun_out_path = os.path.join(output_dir, 'nouns.csv')
        self.np_out_path = os.path.join(output_dir, 'noun_phrases.csv')
        self.parser = CoreNLPParser(url='http://localhost:9000')
        self.n_count = {}
        self.np_count = {}

    def get_parse_tree(self, sentence):
        return next(self.parser.raw_parse(sentence))

    def get_nps(self, tree):
        nps = []
        np_trees = list(tree.subtrees(filter=lambda x: x.label() == 'NP'))
        for np_tree in np_trees:
            np_str = " ".join(np_tree.leaves())
            np_str = re.sub("^[\d\s]+", "", np_str)
            np_str = re.sub("[^a-zA-Z\s]+", "", np_str)
            np_str = np_str.lower()
            if len(np_str) >2:
                nps.append(np_str)
        return nps

    def get_Nouns(self, tree):
        nouns = []
        for tag in tree.pos():
            if tag[1] == "NN" and len(tag[0])>2:
                nouns.append(tag[0].lower())
        return nouns

    def extract(self, sentence):
        try:
            tree = self.get_parse_tree(sentence)
            nps = self.get_nps(tree)
            nouns = self.get_Nouns(tree)
            return nps, nouns
        except StopIteration:
            return [], []

    def process_corpus(self):
        assert os.path.isdir(self.corpus_dir)
        for root, sub, files in os.walk(self.corpus_dir):
            for file in files:
                file_path = os.path.join(root, file)
                print("processing {}".format(file))
                with open(file_path, encoding='utf8', errors="ignore") as fin:
                    for line in fin:
                        nps, nouns = self.extract(line)
                        for np in nps:
                            if np not in self.np_count:
                                self.np_count[np] = 0
                            self.np_count[np] += 1
                        for noun in nouns:
                            if noun not in self.n_count:
                                self.n_count[noun] = 0
                            self.n_count[noun] += 1
        sort_nouns = sorted(self.n_count.items(), key=lambda x: x[1], reverse=True)
        sort_nps = sorted(self.np_count.items(), key=lambda x: x[1], reverse=True)

        with open(self.noun_out_path, 'w') as fout:
            for (noun, count) in sort_nouns:
                fout.write("{},{}\n".format(noun, count))

        with open(self.np_out_path, 'w') as fout:
            for (np, count) in sort_nps:
                fout.write("{},{}\n".format(np, count))

    def start_standford(self):
        stanforNLP_server_cmd = " java -mx4g -cp * edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload tokenize,ssplit,pos,lemma,parse,depparse  -status_port 9000 -port 9000 -timeout 15000"
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


if __name__ == "__main__":
    sent = "the quick brown fox jumps over the lazy dog."
    extract = np_extractor("./raw_data/EasyClinicDataset/2 - docs (English)", "./output/np_extractor_output")
    extract.process_corpus()
