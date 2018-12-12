import numpy as np;
from matplotlib import pyplot as plt;
from matplotlib import cm;
from PIL import Image as image;
import sys;

sys.path.append("../python");
import dipl;

img = image.open("../img/scene.jpg");
data = np.array(img.getdata(), dtype = np.uint8);
data = data.reshape((img.height, img.width, 3));
plt.imshow(data);
plt.show();
plt.close();

kernel = np.array([
	[1, 2, 1],
	[2, 4, 2],
	[1, 2, 1]
], dtype = np.float64);
kernel = kernel / np.sum(kernel);

data = data.astype(np.float64);
size = [data.shape[i] + kernel.shape[i] - 1 for i in range(2)];
result = np.empty(size + [3], dtype = np.float64);

for i in range(3):
	result[:, :, i] = dipl.correlate2(data[:, :, i].copy(), kernel);

plt.imshow(result.astype(np.uint8));
plt.show();
plt.close();

