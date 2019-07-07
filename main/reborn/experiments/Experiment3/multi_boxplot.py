import argparse
import os


import matplotlib.pyplot as plt


if __name__ == "__main__":
    parser = argparse.ArgumentParser("boxPlot")
    parser.add_argument("-r", default="results")
    args = parser.parse_args()
    valid_projects = ["baidu/san", "Tencent/bk-cmdb",
                      "Tencent/ncnn", "Tencent/QMUI_Android", "Tencent/QMUI_IOS",
                      "Tencent/weui", "Tencent/xLua",
                      "NetEase/Emmagee", "meituan/EasyReact",
                      "XiaoMi/pegasus"
                      ]
    valid_projects.extend(
        ["alibaba/ARouter", "alibaba/arthas", "alibaba/canal", "alibaba/druid", "alibaba/nacos", "alibaba/rax"])
    valid_projects = [x.split("/")[1] for x in valid_projects]

    f2_dict = {}
    map_dict = {}
    data_dir = "crc_result"
    for lang in os.listdir(os.path.join(args.r,data_dir)):
        with open(os.path.join(args.r, data_dir,lang, "result_summary.csv"), encoding='utf8') as fin:
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

data_to_plot = list(map_dict.values())
labels = list(f2_dict.keys())

# basic plot
fig = plt.figure(1, figsize=(9, 6))

# Create an axes instance
ax = fig.add_subplot(111)

# Create the boxplot
bp = ax.boxplot(data_to_plot)
ax.set_xticklabels(labels)
# Save the figure
fig.savefig('multi_lang_boxplot.png', bbox_inches='tight')
