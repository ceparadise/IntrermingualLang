# Collect result from the project result and create a csv file for comparision
import argparse, os


def F(beta, precision, recall):
    if precision + recall == 0:
        return 0
    return (beta * beta + 1) * precision * recall / (beta * beta * precision + recall)


def get_best_result(line: str):
    best_f1, best_f2 = (0, 0, 0), (0, 0, 0)
    res_list = eval(line)
    for res in res_list:
        p = res[0]
        r = res[1]
        f1 = res[2]
        f2 = F(2, p, r)
        if f2 > best_f2[2]:
            best_f2 = (p, r, f2)
        if f1 > best_f1[2]:
            best_f1 = (p, r, f1)
    return best_f1, best_f2


class ResultCollector():
    def __init__(self, result_dir):  # the path is as results/<time>/<langaue>/<group>/<project>
        for time in os.listdir(result_dir):
            time_dir = os.path.join(result_dir, time)
            for lang in os.listdir(time_dir):
                lang_dir = os.path.join(time_dir, lang)
                groups_name = os.listdir(lang_dir)
                with open(os.path.join(lang_dir, "result_summary.csv"), "w", encoding='utf8') as fout:
                    project_csv_title_line = []
                    project_csv_title_line.append("")
                    measure_csv_title_line = []
                    measure_csv_title_line.append("")
                    data = dict()
                    for group_name in groups_name:
                        group_path = os.path.join(lang_dir, group_name)
                        if not os.path.isdir(group_path):
                            continue
                        project_dirs_name = os.listdir(group_path)
                        for project_dir_name in project_dirs_name:
                            print(project_dir_name)
                            project_dir_path = os.path.join(group_path, project_dir_name)

                            project_csv_title_line.append(project_dir_name)
                            project_csv_title_line.append("")
                            project_csv_title_line.append("")
                            measure_csv_title_line.append("best_f1")
                            measure_csv_title_line.append("best_f2")
                            measure_csv_title_line.append("MAP")

                            result_dirs_name = os.listdir(project_dir_path)
                            for result_dir_name in result_dirs_name:
                                print("    -" + result_dir_name)
                                result_dir_path = os.path.join(project_dir_path, result_dir_name)
                                files = os.listdir(result_dir_path)
                                for file_name in files:
                                    if "link" not in file_name:
                                        file_path = os.path.join(result_dir_path, file_name)
                                        with open(file_path, 'r', encoding='utf8') as fin:
                                            lines = fin.readlines()
                                            map = lines[1].strip("MAP=").strip("\n\t\r ")
                                            prf_line = lines[3].strip("\n\t\r ")
                                            best_f1, best_f2 = get_best_result(prf_line)
                                            data.setdefault(result_dir_name, [])
                                            data[result_dir_name].append(best_f1)
                                            data[result_dir_name].append(best_f2)
                                            data[result_dir_name].append(map)
                    fout.write(",".join(project_csv_title_line) + "\n")
                    fout.write(",".join(measure_csv_title_line) + "\n")

                    for model_name in data.keys():
                        data_line = data[model_name]

                        avg_f1 = average([float(x[2]) for i, x in enumerate(data_line) if i % 3 == 0])
                        avg_f2 = average([float(x[2]) for i, x in enumerate(data_line) if i % 3 == 1])
                        avg_map = average([float(x) for i, x in enumerate(data_line)if i % 3 == 2])

                        data_line = ["\"" + str(x) + "\"" for x in data_line]
                        data_line.insert(0, model_name)
                        data_line.append(str(avg_f1))
                        data_line.append(str(avg_f2))
                        data_line.append(str(avg_map))
                        fout.write(",".join(data_line) + "\n")


def average(list_num):
    return sum(list_num) / len(list_num)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Result Collector")
    parser.add_argument("-r", default="results")
    args = parser.parse_args()
    rc = ResultCollector(args.r)
