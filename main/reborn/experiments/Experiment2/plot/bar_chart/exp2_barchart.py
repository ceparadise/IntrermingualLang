import argparse
import os

import matplotlib.pyplot as plt
import numpy as np


def split_gvsm(data_dict):
    gvsms = dict()
    others = dict()
    for k in data_dict.keys():
        if k.startswith("gvsm"):
            gvsms[k] = data_dict[k]
        else:
            others[k] = data_dict[k]
    return gvsms, others


def bar_plot(data_dict, model, title):
    key = list(data_dict.keys())[0]
    # data to plot
    n_groups = len(data_dict[key])

    # create plot
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.2
    opacity = 0.8
    if model.startswith("gvsm"):
        rects1 = plt.bar(index+bar_width, data_dict[model], bar_width,
                         alpha=opacity,
                         color='r',
                         label='basic')
        rects1 = plt.bar(index + bar_width, data_dict["{}_trans".format(model)], bar_width,
                         alpha=opacity,
                         color='g',
                         label='trans')
        rects1 = plt.bar(index + bar_width , data_dict["{}_clwv".format(model)], bar_width,
                         alpha=opacity,
                         color='b',
                         label='cross_lingual')
    else:
        rects1 = plt.bar(index, data_dict[model], bar_width,
                         alpha=opacity,
                         color='b',
                         label='basic')
        rects1 = plt.bar(index, data_dict["{}_trans".format(model)], bar_width,
                         alpha=opacity,
                         color='g',
                         label='trans')

    plt.xlabel('Project')
    plt.ylabel('Scores')
    plt.title(title)

    titles = [str(x) for x in range(26)]
    plt.xticks(index + bar_width, titles)
    plt.legend()

    plt.tight_layout()
    plt.savefig(title)
    plt.clf()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("boxPlot")
    parser.add_argument("-d", help="directory of projects.")
    parser.add_argument("-r", default="results")
    args = parser.parse_args()
    root = os.path.join(args.r, args.d)
    valid_projects = ["baidu/san", "Tencent/bk-cmdb",
                      "Tencent/ncnn", "Tencent/QMUI_Android", "Tencent/QMUI_IOS",
                      "Tencent/weui",
                      "NetEase/Emmagee", ]
    valid_projects.extend(
        ["alibaba/arthas", "alibaba/canal", "alibaba/druid", "alibaba/nacos", "alibaba/rax"])
    valid_projects.extend(
        ["marlonbernardes/awesome-berlin", "konlpy/konlpy", "miiton/Cica"])

    valid_projects = [x.split("/")[1] for x in valid_projects]

    f1_dict = {}
    f2_dict = {}
    map_dict = {}
    with open(os.path.join(args.r, args.d, "result_summary.csv"), encoding='utf8') as fin:
        lines = fin.readlines()
        project_names = lines[0].split(",")
        for line_num in range(2, len(lines)):
            cur_line = lines[line_num]
            parts = cur_line.split(",\"")
            model_name = parts[0].strip("\"")
            map_dict[model_name] = []
            f2_dict[model_name] = []
            f1_dict[model_name] = []
            for i in range(0, (int)((len(parts) - 1) / 3)):
                project_name = project_names[i * 3 + 1]
                if project_name not in valid_projects:
                    continue
                f1 = float(parts[(i * 3) + 1].split(",")[2].strip("\"\n)"))
                f2 = float(parts[(i * 3) + 2].split(",")[2].strip("\"\n)"))
                map = float(parts[(i * 3) + 3].strip("\"\n"))
                f1_dict[model_name].append(f1)
                f2_dict[model_name].append(f2)
                map_dict[model_name].append(map)
        f1_gvsm, f1_other = split_gvsm(f1_dict)
        f2_gvsm, f2_other = split_gvsm(f2_dict)
        map_gvsm, map_other = split_gvsm(map_dict)
        models = ["lda", "lsi", "vsm", "gvsm"]
        score_types = ["f1", "f2", "MAP"]
        other_data_list = [f1_other, f2_other, map_other]
        gvsm_data_list = [f1_gvsm, f2_gvsm, map_gvsm]
        for model in models:
            for index, score_type in enumerate(score_types):
                title = "{} {} score".format(model, score_type)
                if model == "gvsm":
                    data_list = gvsm_data_list
                else:
                    data_list = other_data_list
                bar_plot(data_list[index], model, title)