from matplotlib import pyplot as plt;
import numpy as np;
import sys;

sys.path.append("../python");
import dipl;

num = 40;
x = np.array([0, 2, -1, 1], dtype = np.float64);
y = np.array([-1, 1, 1, -1], dtype = np.float64);
xx = dipl.bezier(x, num);
yy = dipl.bezier(y, num);

plt.plot(xx, yy, "b-", x, y, "r*");
plt.show();
