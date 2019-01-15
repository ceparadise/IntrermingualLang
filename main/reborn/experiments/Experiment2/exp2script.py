import datetime

from experiments.Experiment2.experiment2 import Experiment2

if __name__ == "__main__":
    # projects = ["alibaba/ARouter", "alibaba/arthas", "alibaba/canal",
    #             "alibaba/druid", "alibaba/nacos", "alibaba/rax",
    #             "aliyun/aliyun-openapi-java-sdk", "baidu/san", "Tencent/bk-cmdb",
    #             "Tencent/ncnn", "Tencent/QMUI_Android", "Tencent/QMUI_IOS",
    #             "Tencent/westore", "Tencent/weui", "Tencent/xLua"
    #             ]
    projects = [
                "aliyun/aliyun-openapi-java-sdk", "baidu/san", "Tencent/bk-cmdb",
                "Tencent/ncnn", "Tencent/QMUI_Android", "Tencent/QMUI_IOS",
                "Tencent/westore", "Tencent/weui", "Tencent/xLua"
                ]
    models = ["vsm", "gvsm", "lda"]
    use_translate_flags = [True, False]
    time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for project in projects:
        for model in models:
            for use_translate_flag in use_translate_flags:
                try:
                    exp = Experiment2(project, model, use_translate_flag, "cl_wv", output_sub_dir=time)
                    exp.run()
                except Exception as e:
                    print(e)
