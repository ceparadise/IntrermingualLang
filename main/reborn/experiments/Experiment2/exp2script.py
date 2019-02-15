import datetime
import sys, os

base_dir = os.path.dirname(os.path.realpath(__file__));
sys.path.append(os.path.join(base_dir, "../../../reborn"))
sys.path.append(os.path.join(base_dir, "../../../../main"))

from experiments.Experiment2.experiment2 import Experiment2

if __name__ == "__main__":
    projects = ["baidu/san", "Tencent/bk-cmdb",
                "Tencent/ncnn", "Tencent/QMUI_Android", "Tencent/QMUI_IOS",
                "Tencent/weui", "Tencent/xLua",
                "NetEase/Emmagee", "meituan/EasyReact",
                "XiaoMi/pegasus"
                ]
    projects.extend(
        ["alibaba/ARouter", "alibaba/arthas", "alibaba/canal", "alibaba/druid", "alibaba/nacos", "alibaba/rax"])
    # models = ["vsm", "gvsm", "lda"]
    models = ["gvsm"]
    # use_translate_flags = [True, False]
    use_translate_flags = [True]
    time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for project in projects:
        print("Processing project {}".format(project))
        for model in models:
            for use_translate_flag in use_translate_flags:
                exp = Experiment2(project, model, use_translate_flag, "cl_wv_en", output_sub_dir=time)
                exp.run()
