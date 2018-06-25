import shutil

import common
from CL_ESA import CL_ESA
from LDA import LDA
from VSM import VSM
from common import *
from CL_LDA import CL_LDA


class Experiment_easyClinic:
    def __init__(self, lang_code):
        self.answer = dict()
        self.file2links = dict()
        self.percent_dict = dict()
        self.id2artifact = {}  # map document id to artifact name
        self.artifact2id = {}  # Get the document ids belong to a artifact
        self.output_dir = "../output"
        self.lang_code = lang_code

    def readData(self):
        data_dir_path = os.path.join(DATA_DIR, "easyClinic_" + self.lang_code)
        percent_dirs = os.listdir(data_dir_path)
        for dir_name in percent_dirs:
            percent = dir_name.split("-")[1]
            self.percent_dict[percent] = dict()
            for file in os.listdir(os.path.join(data_dir_path, dir_name)):
                file_path = os.path.join(data_dir_path, dir_name, file)
                with open(file_path, encoding='utf8') as fin:
                    type = file[:-len(".csv")]
                    first_line = fin.readline()
                    if 'content' in first_line:
                        for line in fin.readlines():
                            parts = line.split(",")
                            id = parts[0].strip("\"")
                            content = parts[1].strip("\"\n")
                            self.percent_dict[percent][id] = content
                            if id in self.id2artifact.keys() and self.id2artifact[id] != type:
                                print("warning: overwriting id from artifact:{} to artifact:{}".format(
                                    self.id2artifact[id], type))
                            self.id2artifact[id] = type
                            if type not in self.artifact2id:
                                self.artifact2id[type] = set()
                            self.artifact2id[type].add(id)
                    else:
                        for line in fin.readlines():
                            parts = line.split(",")
                            from_id = parts[0].strip("\"")
                            to_id = parts[1].strip("\"\n")
                            if from_id not in self.answer:
                                self.answer[from_id] = set()
                            if to_id not in self.answer:
                                self.answer[to_id] = set()
                            self.answer[from_id].add(to_id)
                            self.answer[to_id].add(from_id)
                            if type not in self.file2links.keys():
                                self.file2links[type] = set()
                            self.file2links[type].add((from_id, to_id))

    def cleanData(self):
        # TODO clean the documents and IO with files to accelaerate
        pass

    def __gen_link_between_artifact(self, doc_dict, arti_type1, arti_type2, trace_model):
        """
        Calculate the scores for the links between the artifacts.
        :param doc_dict:
        :param arti_type1:
        :param arti_type2:
        :param trace_model: Model must implement the method get_doc_similarity(self, doc1, doc2):
        :return:
        """
        links = []
        arti1_doc_ids = self.artifact2id[arti_type1]
        arti2_doc_ids = self.artifact2id[arti_type2]
        print("Generate link between {}and {}".format(arti_type1, arti_type2))
        cnt = 0
        total = len(arti1_doc_ids) * len(arti2_doc_ids)
        print("{} links will be processed in total ...".format(total))
        for arti1_doc_id in arti1_doc_ids:
            for arti2_doc_id in arti2_doc_ids:
                cnt += 1
                # if cnt % 100 == 0:
                print("progress: {}/{}".format(cnt, total))
                arti1_doc = doc_dict[arti1_doc_id]
                arti2_doc = doc_dict[arti2_doc_id]
                sim_score = trace_model.get_doc_similarity(arti1_doc, arti2_doc)
                links.append((arti1_doc_id, arti2_doc_id, sim_score))
        return links

    def get_models(self, project_name, docs):
        if self.lang_code == "zh":
            vsm = VSM("zh")
            vsm.build_model(docs)
            yield vsm
            # lda = LDA("zh")
            # lda.train(docs, num_topics=200)
            # yield lda

            # cl_lsa = CL_LDA(project_name,"zh")
            # cl_lsa.to_CL_LAS_data_files(docs)
            # cl_lsa.train_CL_LSA(200)
            # cl_lsa.get_tfidf_model()
            # yield cl_lsa
        elif self.lang_code == "fr":
            vsm = VSM("fr")
            vsm.build_model(docs)
            yield vsm
            # corpus_dir = os.path.join(common.ALG_DIR, "cl-esa", "wiki_corpus")
            # en_ntf = os.path.join(corpus_dir, "short-abstracts_en.nt")
            # fr_ntf = os.path.join(corpus_dir, "short-abstracts-en-uris_fr.nt")
            # cl_esa = CL_ESA(en_ntf_path=en_ntf, fo_ntf_path=fr_ntf, fo_lang_code='fr')
            # cl_esa.set_model(os.path.join(cl_esa.output_dir, "final_multi_lingual_OTDFIndex"))
            # yield cl_esa

    def get_links(self, doc_dict, arti_type1, arti_type2, model, output_file):
        links = []
        if os.path.isfile(output_file):
            with open(output_file, encoding='utf8') as fin:
                for line in fin.readlines():
                    from_id, to_id, score = line.split(",")
                    links.append((from_id, to_id, score))
        else:
            links = self.__gen_link_between_artifact(doc_dict, arti_type1, arti_type2, model)
            with open(output_file, 'w', encoding='utf8') as fout:
                for from_id, to_id, score in links:
                    fout.write("{},{},{}\n".format(from_id, to_id, score))
        return links

    def UC_TC(self, doc_dict, model, output_dir):
        output_file = os.path.join(output_dir, "UC_TC_{}.links".format(model.get_model_name()))
        return self.get_links(doc_dict, "use_cases", "test_cases", model, output_file)

    def ID_CC(self, doc_dict, model, output_dir):
        output_file = os.path.join(output_dir, "ID_CC_{}.links".format(model.get_model_name()))
        return self.get_links(doc_dict, "interaction_diagrams", "class_description", model, output_file)

    def UC_CC(self, doc_dict, model, output_dir):
        output_file = os.path.join(output_dir, "UC_CC_{}.links".format(model.get_model_name()))
        return self.get_links(doc_dict, "use_cases", "class_description", model, output_file)

    def eval(self, gen_links, gold_links, total_num):
        gen_links = set(gen_links)
        gold_links = set(gold_links)
        tp = len(gen_links & gold_links)
        fp = len(gen_links - gold_links)
        fn = len(gold_links - gen_links)
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
        return precision, recall, f1

    def run(self):
        self.readData()
        cnt = 0
        for percent in self.percent_dict:
            cnt += 1
            if cnt != 1:
                continue
            print("processing " + percent)
            project_name = "_".join(["0_EasyClinic", percent])
            percent_output_dir = os.path.join(self.output_dir, project_name, self.lang_code)

            if not os.path.exists(percent_output_dir):
                os.makedirs(percent_output_dir)
            docs = self.percent_dict[percent].values()
            for model in self.get_models(project_name, docs):
                with open(os.path.join(percent_output_dir, model.get_model_name() + ".txt"), "w") as res_out:
                    print("Running model {}".format(model.get_model_name()))
                    gen_links = []
                    gold_links = []
                    gen_links.extend(self.UC_TC(self.percent_dict[percent], model, percent_output_dir))
                    gen_links.extend(self.ID_CC(self.percent_dict[percent], model, percent_output_dir))
                    gen_links.extend(self.UC_CC(self.percent_dict[percent], model, percent_output_dir))
                    gold_links.extend(self.file2links["UC_TC"])
                    gold_links.extend(self.file2links["ID_CC"])
                    gold_links.extend(self.file2links["UC_CC"])
                    total_num = len(gen_links)
                    for threshold in range(0, 100, 10):
                        threshold = threshold / 100.0
                        gen_links_above_thre = [(x[0], x[1]) for x in gen_links if (float)(x[2]) >= threshold]
                        res_out.write(str(self.eval(gen_links_above_thre, gold_links, total_num)) + "\n")


if __name__ == "__main__":
    exp = Experiment_easyClinic(lang_code='fr')
    exp.run()
