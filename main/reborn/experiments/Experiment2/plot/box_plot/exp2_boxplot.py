import argparse
import os

import matplotlib.pyplot as plt


def split_gvsm(data_dict):
    gvsms = dict()
    others = dict()
    for k in data_dict.keys():
        if k.startswith("gvsm"):
            if k == "gvsm_clwv":
                t = "clwv_gvsm"
            if k == "gvsm_enwv":
                t = "enwv_gvsm"
            if k == "gvsm_enwv_trans":
                t = "enwv_gvsm+trans"
            gvsms[t] = data_dict[k]
        else:
            if k == "lda_trans":
                t = "lda+trans"
            if k == "lsi_trans":
                t = "lsi+trans"
            if k == "vsm_trans":
                t = "vsm+trans"
            others[t] = data_dict[k]
    return gvsms, others


def box_plot(data_dict, output):
    data_to_plot = list(data_dict.values())
    labels = list(data_dict.keys())
    # basic plot
    plt.clf()
    fig = plt.figure(1, figsize=(9, 6))
    # Create an axes instance
    ax = fig.add_subplot(111)

    # Create the boxplot
    bp = ax.boxplot(data_to_plot)
    ax.set_xticklabels(labels)
    # Save the figure
    fig.savefig('{}.png'.format(output), bbox_inches='tight')


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
                           "Tencent/weui", "NetEase/Emmagee", ])
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
            parts = cur_line.split(",")
            model_name = parts[0].strip("\"")
            map_dict[model_name] = []
            f2_dict[model_name] = []
            f1_dict[model_name] = []
            for i in range(0, (int)((len(parts) - 1) / 7)):
                project_name = project_names[i * 3 + 1]
                if project_name not in valid_projects:
                    continue
                f1 = float(parts[(i * 7) + 3].strip("\"\n()"))
                f2 = float(parts[(i * 7) + 6].strip("\"\n()"))
                map = float(parts[(i * 7) + 7].strip("\"\n()"))
                f1_dict[model_name].append(f1)
                f2_dict[model_name].append(f2)
                map_dict[model_name].append(map)
        f1_gvsm, f1_other = split_gvsm(f1_dict)
        f2_gvsm, f2_other = split_gvsm(f2_dict)
        map_gvsm, map_other = split_gvsm(map_dict)

        box_plot(f1_gvsm, "f1_gvsm")
        box_plot(f1_other, "f1_other")

        box_plot(f2_gvsm, "f2_gvsm")
        box_plot(f2_other, "f2_other")

        box_plot(map_gvsm, "map_gvsm")
        box_plot(map_other, "map_other")

        fig3_f2 = dict()
        fig3_map = dict()

        fig3_f2["vsm+trans"] = f2_other["vsm+trans"]
        fig3_f2["enwv_gvsm+trans"] = f2_gvsm["enwv_gvsm+trans"]

        fig3_map["vsm+trans"] = map_other["vsm+trans"]
        fig3_map["enwv_gvsm+trans"] = map_gvsm["enwv_gvsm+trans"]

        box_plot(fig3_f2, "Compare F2 score of gvsm_tran and vsm_trans ")
        box_plot(fig3_map, "Compare MAP score of gvsm_tran and vsm_trans ")
