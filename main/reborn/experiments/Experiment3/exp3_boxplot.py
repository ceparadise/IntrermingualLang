import argparse
import os

import matplotlib.pyplot as plt


def average(num_list):
    sum = 0
    for x in num_list:
        sum += x
    return sum / len(num_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("exp3_boxPlot")
    parser.add_argument("-d", help="directory of projects.")
    parser.add_argument("-r", default="results")
    args = parser.parse_args()
    root = os.path.join(args.r, args.d)
    valid_projects = ["baidu/san", "Tencent/bk-cmdb",
                      "Tencent/ncnn", "Tencent/QMUI_Android", "Tencent/QMUI_IOS",
                      "Tencent/weui", "Tencent/xLua",
                      "NetEase/Emmagee", "meituan/EasyReact",
                      "XiaoMi/pegasus"
                      ]
    valid_projects.extend(
        ["alibaba/arthas", "alibaba/canal", "alibaba/druid", "alibaba/nacos", "alibaba/rax"])
    valid_projects = [x.split("/")[1] for x in valid_projects]

    res_dir = os.path.join(args.r, args.d)
    for i, language_dir in enumerate(os.listdir(res_dir)):
        language_dir_path = os.path.join(res_dir, language_dir)
        f2_dict = {}
        map_dict = {}
        with open(os.path.join(language_dir_path, "result_summary.csv"), encoding='utf8') as fin:
            lines = fin.readlines()
            project_names = lines[0].split(",")
            for line_num in range(2, len(lines)):
                cur_line = lines[line_num]
                parts = cur_line.split(",\"")
                model_name = parts[0].strip("\"")
                map_dict[model_name] = []
                f2_dict[model_name] = []
                for i in range(0, (int)((len(parts) - 1) / 3)):
                    project_name = project_names[i * 3 + 1]
                    if project_name not in valid_projects:
                        continue
                    f2 = float(parts[(i * 3) + 2].split(",")[2].strip("\"\n)"))
                    map = float(parts[(i * 3) + 3].strip("\"\n"))
                    f2_dict[model_name].append(f2)
                    map_dict[model_name].append(map)

        data_to_plot = list(f2_dict.values())
        name_translate = dict()
        name_translate["gvsm_origin"] = "CLWE-G"
        name_translate["gvsm_trans"] = "WE-G+Trans"
        name_translate["lda_origin"] = "LDA"
        name_translate["lda_trans"] = "LDA+Trans"
        name_translate["vsm_origin"] = "VSM"
        name_translate["vsm_trans"] = "VSM+Trans"
        labels = list([name_translate[x] for x in f2_dict.keys()])

        print(language_dir)
        for model_name in f2_dict:
            f2_avg = average(f2_dict[model_name])
            print(name_translate[model_name],f2_avg)
        for model_name in map_dict:
            map_avg = average(map_dict[model_name])
            print(name_translate[model_name],map_avg)

        # basic plot
        fig = plt.figure(i, figsize=(9, 6))

        # Create an axes instance
        ax = fig.add_subplot(111)

        # Create the boxplot
        bp = ax.boxplot(data_to_plot)
        ax.set_xticklabels(labels)
        # Save the figure
        fig.savefig(language_dir + '.png', bbox_inches='tight')
        fig.clf()
