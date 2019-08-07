from scipy.interpolate import make_interp_spline, BSpline, interp1d
import matplotlib.pyplot as plt
import numpy as np

# 	7	1118	2544	10570	22728	23332	112198
# Optimized	3919	6117	5900	6454	8689	14600	17849
# Not Optimized	5259	7172	8107	8927	11952	17632	24968
# TraceDynamo 	260	2548	2358	9589	17642	12124	90694

x = np.array(  [7, 1118, 2544, 10570, 22728, 23332,112198])
opt = np.array([3919, 6117, 5900, 6454, 8689, 14600, 17849])
unopt = np.array([5259, 7172, 8107, 8927, 11952, 17632, 24968])
tdm = np.array([260, 2548, 2358, 9589, 17642, 12124, 90694])
xnew = np.linspace(x.min(), x.max(), 300)  # 300 represents number of points to make between T.min and T.max
f = interp1d(x, opt)

plt.plot(xnew, f(xnew))
plt.scatter (x, opt)
plt.show()

