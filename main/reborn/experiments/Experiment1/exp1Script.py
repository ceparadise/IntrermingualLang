from experiments.Experiment1.experiment1 import Experiment1

if __name__ == "__main__":
    replace_interval = 10
    model_types = ["lda", "vsm"]
    data_sets = ["ezclinic", "cm1", "dronology"]
    for model_type in model_types:
        for data_set in data_sets:
            replace_file = data_set + "_both_side_contain.txt"
            exp = Experiment1(replace_interval, model_type=model_type, data_set=data_set,
                              replace_list_name=replace_file, average_time=5)
            exp.run()
