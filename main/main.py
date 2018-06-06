from common import *
from CL_LSA import CL_LSA


class Experiment_easyClinic:
    def __init__(self):
        self.answer = dict()
        self.percent_dict = dict()

    def readData(self):
        dirs = os.listdir(os.path.join(DATA_DIR, "easyClinic"))
        for dir_name in dirs:
            percent = dir_name.split("-")[1]
            self.percent_dict[percent] = dict()
            for file in os.listdir(os.path.join(DATA_DIR, "easyClinic", dir_name)):
                file_path = os.path.join(DATA_DIR, "easyClinic", dir_name, file)
                with open(file_path, encoding='utf8') as fin:
                    first_line = fin.readline()
                    if 'content' in first_line:
                        for line in fin.readlines():
                            parts = line.split(",")
                            id = parts[0].strip("\"")
                            content = parts[1].strip("\"\n")
                            self.percent_dict[percent][id] = content
                    else:
                        for line in fin.readlines():
                            parts = line.split(",")
                            from_id = parts[0].strip("\"")
                            to_id = parts[1].strip("\"\n")
                            if from_id not in self.answer:
                                self.answer[from_id] = []
                            if to_id not in self.answer:
                                self.answer[to_id] = []
                            self.answer[from_id].append(to_id)
                            self.answer[to_id].append(from_id)

    def eval(self):
        pass

    def run(self):
        self.readData()
        cl_lsa = CL_LSA()
        project_name = "0_EasyClinic"
        cnt = 0
        for percent in self.percent_dict:
            cnt += 1
            if cnt < 2:
                continue
            docs = self.percent_dict[percent]
            for doc in docs.values():
                print(cl_lsa.train_CL_LSA(doc, project_name))
                print(doc)


if __name__ == "__main__":
    exp = Experiment_easyClinic()
    exp.run()
