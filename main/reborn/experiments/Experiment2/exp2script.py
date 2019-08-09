import datetime
import sys, os

from hanziconv import HanziConv

base_dir = os.path.dirname(os.path.realpath(__file__));
sys.path.append(os.path.join(base_dir, "../../../reborn"))
sys.path.append(os.path.join(base_dir, "../../../../main"))
from experiments.Experiment2.experiment2 import Experiment2
from common import DATA_DIR


def load_vectors(fname):
    """
    Return word embedding vectors as map
    :return:
    """
    data = {}
    with open(fname, 'r', encoding='utf-8') as fin:
        n, d = map(int, fin.readline().split())
        print("vector #:{} vector dimension:{}".format(n, d))
        for line in fin:
            tokens = line.rstrip().split()
            term = tokens[0]
            term = HanziConv.toSimplified(term)  # conver to simpified Chinese
            try:
                data[term] = [float(x) for x in tokens[1:]]
            except Exception as e:
                pass
    return data


def get_cl_wv_en():
    """
    Get the english cross lingual wordvector. This will be shared by multiple experiment to avoid repeated model loading
    :return:
    """
    word_vec_root = os.path.join(DATA_DIR, "wordVectors")
    print("Building {} word embedding ...".format("en"))
    vec_file_path = os.path.join(word_vec_root, "wiki.{}.align.vec".format("en"))
    cl_wv = load_vectors(vec_file_path)
    return cl_wv


if __name__ == "__main__":
    projects = {}
    # zh_projects = []
    # zh_projects.extend(["baidu/san", "Tencent/bk-cmdb",
    #                     "Tencent/ncnn", "Tencent/QMUI_Android", "Tencent/QMUI_IOS",
    #                     "Tencent/weui", "Tencent/xLua",
    #                     "NetEase/Emmagee", "XiaoMi/pegasus"
    #                     ])
    # zh_projects.extend(
    #     ["alibaba/arthas", "alibaba/canal", "alibaba/druid", "alibaba/nacos", "alibaba/rax"])
    #
    # for zpj in zh_projects:
    #     projects[zpj] = "zh"

    # projects.extend(
    #     ["marlonbernardes/awesome-berlin", "konlpy/konlpy", "open-korean-text/open-korean-text",
    #      "pgrimaud/horaires-ratp-api", "miiton/Cica"])

    #projects["marlonbernardes/awesome-berlin"] = "de"
    projects["konlpy/konlpy"] = "ko"
    projects["open-korean-text/open-korean-text"] ="ko"
    projects["pgrimaud/horaires-ratp-api"] = "fr"
    projects["miiton/Cica"] = "zh"

    models = ["vsm", "gvsm", "lda", "lsi"]
    # "vsm", "gvsm", "lda",lsi
    use_translate_flags = [False,True]
    # use_translate_flags = [False]
    time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    cl_wv = None
    # cl_wv = get_cl_wv_en()
    for project in projects.keys():
        lang = projects[project]
        print("Processing project {}".format(project))
        for model in models:
            for use_translate_flag in use_translate_flags:
                exp = Experiment2(project, model, use_translate_flag, "cl_wv_en", output_sub_dir=time, lang_code=lang)
                exp.cl_wv = cl_wv
                exp.run()
