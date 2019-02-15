import datetime
import sys, os

base_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base_dir, "../../../reborn"))
sys.path.append(os.path.join(base_dir, "../../../../main"))

import common
from experiments.Experiment3.experiment3 import Experiment3

if __name__ == "__main__":
    projects = ["baidu/san", "Tencent/bk-cmdb",
                "Tencent/ncnn", "Tencent/QMUI_Android", "Tencent/QMUI_IOS",
                "Tencent/weui", "Tencent/xLua",
                "NetEase/Emmagee", "meituan/EasyReact",
                "XiaoMi/pegasus"
                ]
    projects.extend(
        ["alibaba/ARouter", "alibaba/arthas", "alibaba/canal", "alibaba/druid", "alibaba/nacos", "alibaba/rax"])
    models = ["vsm", "gvsm", "lda"]
    use_translate_flags = [False, True]
    # languages = common.language_list
    languages = ["fr"]
    time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for language in languages:
        for project in projects:
            print("Processing project {}".format(project))
            git_project = os.path.join("data", language)
            for model in models:
                for use_translate_flag in use_translate_flags:
                    term_similarity_type = "cl_wv"
                    if use_translate_flag is True:
                        term_similarity_type += "_en"
                    else:
                        term_similarity_type += "_" + language
                    exp = Experiment3(project, model, use_translate_flag, term_similarity_type, output_sub_dir=time,
                                      github_projects_dir=git_project, lang_code=language)
                    exp.run()
                    del exp
