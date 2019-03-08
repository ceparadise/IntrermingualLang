import datetime
import sys, os
import argparse

base_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base_dir, "../../../reborn"))
sys.path.append(os.path.join(base_dir, "../../../../main"))

import common
from experiments.Experiment3.experiment3 import Experiment3

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', "--languages", nargs='+', help="languages to run", default=common.language_list)
    args = parser.parse_args()
    projects = []
    projects.extend(
        ["alibaba/arthas", "alibaba/canal", "alibaba/druid", "alibaba/nacos", "alibaba/rax"])
    projects.extend(["baidu/san",
                     "Tencent/ncnn", "Tencent/QMUI_Android", "Tencent/QMUI_iOS",
                     "Tencent/weui", "Tencent/xLua",
                     "NetEase/Emmagee", "meituan/EasyReact",
                     "XiaoMi/pegasus", "Tencent/bk-cmdb"
                     ])
    models = ["vsm", "gvsm", "lda"]
    # models = ["vsm"]
    use_translate_flags = [False, True]
    languages = args.languages
    # languages = ["fr"]
    time = datetime.datetime.now().strftime(
        "%Y%m%d-%H%M%S")  # TODO modify the output dir to make result group by langauge
    for language in languages:
        output_dir = os.path.join(time, language)
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
                    exp = Experiment3(project, model, use_translate_flag, term_similarity_type,
                                      output_sub_dir=output_dir,
                                      github_projects_dir=git_project, lang_code=language)
                    exp.run()
                    del exp
