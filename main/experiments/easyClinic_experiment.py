import shutil

import common
from CL_ESA import CL_ESA
from ESA import ESA
from LDA import LDA
from TR_LDA import TR_LDA
from TR_VSM import TR_VSM
from VSM import VSM
from common import *
from CL_LDA import CL_LDA
from subprocess import Popen, PIPE

from trans_cache_manage import Trans_Agent


class Experiment_easyClinic:
    def __init__(self, lang_code, data_dir_name_root="easyClinic_"):
        self.answer = dict()
        self.file2links = dict()
        self.percent_dict = dict()
        self.id2artifact = {}  # map document id to artifact name
        self.artifact2id = {}  # Get the document ids belong to a artifact
        self.output_dir = "../../output"
        self.lang_code = lang_code
        self.data_dir_name_root = data_dir_name_root
        stanforNLP_server_cmd = " java -mx4g -cp * edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload tokenize,ssplit,pos,lemma,parse,depparse  -status_port 9000 -port 9000 -timeout 15000 -serverProperties StanfordCoreNLP-chinese.properties"
        self.start_server = Popen(stanforNLP_server_cmd.split(), cwd="G:\lib\stanford-corenlp-full-2016-10-31",
                                  stderr=PIPE, stdout=PIPE, shell=True)

        trans_cache_dir = os.path.join(self.output_dir, "trans_cache", lang_code)
        self.trans_agent = Trans_Agent(trans_cache_dir_path=trans_cache_dir)

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

    def readData(self):
        data_dir_path = os.path.join(DATA_DIR, self.data_dir_name_root + self.lang_code)
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
        vsm = VSM(self.lang_code)
        print("Building model:", vsm.get_model_name())
        vsm.build_model(docs)
        yield vsm

        tr_vsm = TR_VSM(self.lang_code, self.trans_agent)
        print("Building model:", tr_vsm.get_model_name())
        tr_vsm.build_model(docs)
        print(tr_vsm.get_model_name(), " ready")
        self.trans_agent.dump_trans_cache()
        yield tr_vsm

        # lda = LDA(self.lang_code)
        # lda.train(docs, num_topics=200)
        # yield lda

        # tr_lda = TR_LDA(self.lang_code)
        # tr_lda.train(docs, num_topics=200)
        # yield tr_lda

        wiki_dir = os.path.join(common.ALG_DIR, "Wiki-ESA-master", "data")
        en_wiki = os.path.join(wiki_dir, "enwiki-20180320-pages-articles-multistream.xml")
        fo_wiki = os.path.join(wiki_dir, "{}wiki-20180701-pages-articles-multistream.xml".format(self.lang_code))
        esa = ESA(self.lang_code)
        print("Building model:", esa.get_model_name())
        esa.build(en_wiki=en_wiki, fo_wiki=fo_wiki, rebuild_en=False, rebuild_fo=False)
        print(esa.get_model_name(), " ready")
        yield esa

        # cl_lda = CL_LDA(project_name, self.lang_code)
        # cl_lda.to_CL_LAS_data_files(docs)
        # cl_lda.train_CL_LSA(200)
        # cl_lda.get_tfidf_model()
        # yield cl_lda

        # corpus_dir = os.path.join(common.ALG_DIR, "cl-esa", "wiki_corpus")
        # en_ntf = os.path.join(corpus_dir, "short-abstracts_en.nt")
        # fo_ntf = os.path.join(corpus_dir, "short-abstracts-en-uris_{}.nt".format(self.lang_code))
        # cl_esa = CL_ESA(en_ntf_path=en_ntf, fo_ntf_path=fo_ntf, fo_lang_code=self.lang_code)
        # yield cl_esa

    def get_links(self, doc_dict, arti_type1, arti_type2, model, output_file, regen_links=True):
        links = []
        if os.path.isfile(output_file) and not regen_links:
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
                    # gen_links.extend(self.ID_CC(self.percent_dict[percent], model, percent_output_dir))
                    # gen_links.extend(self.UC_TC(self.percent_dict[percent], model, percent_output_dir))
                    gen_links.extend(self.UC_CC(self.percent_dict[percent], model, percent_output_dir))
                    # gold_links.extend(self.file2links["ID_CC"])
                    # gold_links.extend(self.file2links["UC_TC"])
                    gold_links.extend(self.file2links["UC_CC"])
                    total_num = len(gen_links)
                    for threshold in range(0, 100, 1):
                        threshold = threshold / 100.0
                        gen_links_above_thre = [(x[0], x[1]) for x in gen_links if (float)(x[2]) >= threshold]
                        res_out.write("threshod=" + str(threshold) + ":" +
                                      str(self.eval(gen_links_above_thre, gold_links, total_num)) + "\n")
                    print("Done - Model {}".format(model.get_model_name()))
        self.trans_agent.dump_trans_cache()


if __name__ == "__main__":
    exp = Experiment_easyClinic(lang_code='zh', data_dir_name_root="easyClinicWordReplace_")
    exp.run()