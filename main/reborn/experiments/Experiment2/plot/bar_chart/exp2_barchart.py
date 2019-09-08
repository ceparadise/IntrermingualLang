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


def fig3_plot(data_dict, title, labels):
    key = list(data_dict.keys())[0]
    n_groups = len(data_dict[key])
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.2
    opacity = 0.8

    rects1 = plt.bar(index, data_dict["gvsm_enwv_trans"], bar_width,
                     alpha=opacity,
                     color='r',
                     label='gvsm_enwv_trans')
    rects1 = plt.bar(index + bar_width * 1, data_dict["vsm_trans".format(model)], bar_width,
                     alpha=opacity,
                     color='g',
                     label='vsm_trans')

    plt.xlabel('Project')
    plt.ylabel('Scores')
    plt.title(title)

    titles = [str(x) for x in labels]
    plt.xticks(index + bar_width, titles, rotation='vertical')
    plt.legend()

    plt.tight_layout()
    plt.savefig(title)
    plt.clf()


def bar_plot(data_dict, model, title, labels):
    key = list(data_dict.keys())[0]
    # data to plot
    n_groups = len(data_dict[key])

    # create plot
    fig, ax = plt.subplots()

    index = np.arange(n_groups)
    bar_width = 0.2
    opacity = 0.8
    if model.startswith("gvsm"):
        rects1 = plt.bar(index, data_dict["{}_enwv".format(model)], bar_width,
                         alpha=opacity,
                         color='r',
                         label='enwv',
                         edgecolor="k",
                         hatch="///")
        rects1 = plt.bar(index + bar_width * 1, data_dict["{}_clwv".format(model)], bar_width,
                         alpha=opacity,
                         color='g',
                         label='clwv',
                         edgecolor="k",
                         hatch="---")
        rects1 = plt.bar(index + bar_width * 2, data_dict["{}_enwv_trans".format(model)], bar_width,
                         alpha=opacity,
                         color='b',
                         label='enwv_trans',
                         edgecolor="k",
                         hatch="xxx")
    else:
        rects1 = plt.bar(index, data_dict[model], bar_width,
                         alpha=opacity,
                         color='b',
                         label='basic')
        rects1 = plt.bar(index+bar_width, data_dict["{}_trans".format(model)], bar_width,
                         alpha=opacity,
                         color='g',
                         label='trans')

    plt.xlabel('Project')
    plt.ylabel('Scores')
    plt.title(title)

    # titles = [str(x) for x in range(26)]
    titles = [str(x) for x in labels]
    plt.xticks(index + bar_width, titles, rotation='vertical')
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
    valid_projects = []
    valid_projects.extend(
        ["alibaba/arthas", "alibaba/canal", "alibaba/druid", "alibaba/nacos", "alibaba/rax"])
    valid_projects.extend(["baidu/san", "Tencent/bk-cmdb",
                           "Tencent/ncnn", "Tencent/QMUI_Android", "Tencent/QMUI_IOS",
                           "Tencent/weui", "Tencent/xLua", "XiaoMi/pegasus",
                           "NetEase/Emmagee"])
    valid_projects.extend(
        ["marlonbernardes/awesome-berlin", "konlpy/konlpy", "miiton/Cica"])

    valid_projects = [x.split("/")[1] for x in valid_projects]

    f1_dict = {}
    f2_dict = {}
    map_dict = {}
    labels = []
    with open(os.path.join(args.r, args.d, "result_summary.csv"), encoding='utf8') as fin:
        lines = fin.readlines()
        project_names = lines[0].split(",")
        for line_num in range(2, len(lines)):
            cur_line = lines[line_num]
            parts = cur_line.split(",")
            model_name = parts[0].strip("\"")
            map_dict[model_name] = []
            f2_dict[model_name] = []
            f1_dict[model_name] = []
            for i in range(0, (int)((len(parts) - 1) / 7)):
                project_name = project_names[i * 3 + 1]
                if project_name not in valid_projects:
                    print(project_name)
                    continue
                labels.append(project_name)
                f1 = float(parts[(i * 7) + 3].strip("\"\n()"))
                f2 = float(parts[(i * 7) + 6].strip("\"\n()"))
                map = float(parts[(i * 7) + 7].strip("\"\n()"))
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
                bar_plot(data_list[index], model, title, labels)

        fig3_f2 = dict()
        fig3_map = dict()

        fig3_f2["vsm_trans"] = f2_other["vsm_trans"]
        fig3_f2["gvsm_enwv_trans"] = f2_gvsm["gvsm_enwv_trans"]

        fig3_plot(fig3_f2, "Fig3_f2", labels)

        fig3_map["vsm_trans"] = map_other["vsm_trans"]
        fig3_map["gvsm_enwv_trans"] = map_gvsm["gvsm_enwv_trans"]

        fig3_plot(fig3_map,"Fig3_map",labels)
