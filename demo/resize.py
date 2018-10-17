from matplotlib import pyplot as plt;
from matplotlib import cm;
from PIL import Image as image;
import numpy as np;
from jpeg import jpeg;

#img = image.open("../img/738b4710b912c8fcc7977bd3f1039245d6882143.jpg");
img = image.open("../img/apple.png");
data = np.array(img.getdata(), dtype = np.uint8);
data = data.reshape((img.height, img.width, 3));

plt.imshow(data);
plt.show();
plt.close();

h = 139;
w = 139;
result = np.empty((h, w, 3), dtype = np.uint8);

#for i in range(result.shape[2]):
#	result[:, :, i] = jpeg.resize_naive(data[:, :, i].astype(np.int32), h, w);

#for i in range(result.shape[2]):
#	result[:, :, i] = jpeg.resize_near(data[:, :, i].astype(np.int32), h, w);

for i in range(result.shape[2]):
	result[:, :, i] = jpeg.resize_linear(data[:, :, i].astype(np.int32), h, w);

plt.imshow(result);
plt.show();
plt.close();
