import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import spline

if __name__ == "__main__":
    files = ["cm1", "dronology", "ezclinic"]
    for file in files:
        file_name = file + ".csv"
        with open(file_name, encoding='utf-8') as fin:
            cnt = 0
            x = []
            model_scores = dict()
            for line in fin:
                parts = line.strip("\n").split(",")
                scores = parts[1:]
                scores = [(float)(d) for d in scores]
                if cnt == 0:
                    x = np.array(scores)
                    smooth_x = np.linspace(x.min(), x.max(), 300)
                else:
                    model = parts[0]
                    y = np.array(scores)
                    smooth_y = spline(x, y, smooth_x)
                    model_scores[model] = smooth_y
                cnt += 1

            fig = plt.figure(figsize=(11, 8))
            ax1 = fig.add_subplot(111)
            for model in model_scores:
                scores = model_scores[model]
                if model.startswith("VSM"):
                    color = 'b'
                else:
                    color = 'r'
                if model.endswith("AP"):
                    lineType = "dashed"
                else:
                    lineType = "solid"
                ax1.plot(smooth_x, scores, label=model, color=color,linestyle=lineType)
            ax1.legend(loc=3)
            ax1.grid()
            ax1.set_xlim(xmin=0,xmax=100)
            plt.xticks(np.arange(0,101,10))
            plt.savefig(file+".png", bbox_inches="tight")
            plt.clf()
