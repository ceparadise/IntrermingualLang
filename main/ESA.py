import os
import shutil
import sys

sys.path.insert(0, r'G:\Projects\InterLingualTrace\algorithms\Wiki-ESA-master')

from common import ALG_DIR
from model import Model
from subprocess import Popen
from cunning_linguistics import SemanticAnalyser


class ESA(Model):
    def __init__(self, fo_lang_code):
        super(ESA, self).__init__(fo_lang_code)

    def build(self, en_wiki, fo_wiki, rebuild_en=False, rebuild_fo=True):
        project_dir = os.path.join(ALG_DIR, "Wiki-ESA-master")
        default_matrix_dir = os.path.join(project_dir, "matrix")
        fo_matrix_dir = os.path.join(project_dir, "matrix_" + self.fo_lang_code)
        en_matrix_dir = os.path.join(project_dir, "matrix_en")
        cwd = project_dir
        if rebuild_en:
            print("parsing en xml...")
            s1 = Popen('C:\Python27\python.exe xml_parse.py {}'.format(en_wiki).split(), cwd=cwd)
            s1.wait()
            print("Building index...")
            s2 = Popen('C:\Python27\python.exe generate_indices.py'.split(), cwd=cwd)
            s2.wait()
            print("Building matrix...")
            s3 = Popen('C:\Python27\python.exe matrix_builder.py'.split(), cwd=cwd)
            s3.wait()
            shutil.copytree(default_matrix_dir, en_matrix_dir)
            shutil.rmtree(os.path.join(project_dir, "temp"))

        if rebuild_fo:
            print("parsing {} xml...".format(self.fo_lang_code))
            s1 = Popen('C:\Python27\python.exe xml_parse.py {}'.format(fo_wiki).split(), cwd=cwd)
            s1.wait()
            print("Building index...")
            s2 = Popen('C:\Python27\python.exe generate_indices.py'.split(), cwd=cwd)
            s2.wait()
            print("Building matrix...")
            s3 = Popen('C:\Python27\python.exe matrix_builder.py'.split(), cwd=cwd)
            s3.wait()
            print("Finished builing")
            shutil.copytree(default_matrix_dir, fo_matrix_dir)
            shutil.rmtree(os.path.join(project_dir, "temp"))

        self.en_esa = SemanticAnalyser(matrix_dir=en_matrix_dir)
        self.fo_esa = SemanticAnalyser(matrix_dir=fo_matrix_dir)

    def get_doc_similarity(self, doc1, doc2):
        doc1_lang_dict = self.split_tokens_by_lang(self.get_tokens(doc1))
        doc2_lang_dict = self.split_tokens_by_lang(self.get_tokens(doc2))
        doc1_en = doc1_lang_dict["en"]
        doc1_fo = doc1_lang_dict[self.fo_lang_code]
        doc2_en = doc2_lang_dict["en"]
        doc2_fo = doc2_lang_dict[self.fo_lang_code]

        doc1_en = " ".join(doc1_en)
        doc1_fo = " ".join(doc1_fo)
        doc2_en = " ".join(doc2_en)
        doc2_fo = " ".join(doc2_fo)

        en_sim = self.en_esa.cosine_similarity(doc1_en, doc2_en)
        fo_sim = self.fo_esa.cosine_similarity(doc1_fo, doc2_fo)
        return (en_sim * len(doc1_en + doc2_en) + fo_sim * len(doc1_fo + doc2_fo)) / (
            len(doc1_en) + len(doc1_fo) + len(doc2_en) + len(doc2_fo))

    def get_model_name(self):
        return "ESA"


if __name__ == "__main__":
    esa = ESA("zh")
    esa.build(en_wiki="data/enwiki-20180320-pages-articles-multistream.xml",
              fo_wiki="data/zhwiki-20180301-pages-articles-multistream.xml", rebuild_en=False,rebuild_fo=True)
    text1 = "蔡凤云"
    text2 = "蔡凤云"
    text3 = "苹果公司也是开发软件的硬件公司"
    print(esa.get_doc_similarity(text1, text2))

