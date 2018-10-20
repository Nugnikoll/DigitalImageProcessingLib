import numpy as np;
from matplotlib import pyplot as plt;
from matplotlib import cm;
from PIL import Image as image;
from jpeg import jpeg;

img = image.open("../img/dark.jpg");
#img = image.open("../img/artery.jpg");
data = np.array(img.getdata(), dtype = np.uint8);
data = data.reshape((img.height, img.width, 3));
plt.imshow(data);
plt.show();
plt.close();
result = np.empty(data.shape, dtype = data.dtype);
for i in range(3):
	result[:, :, i] = jpeg.power_law(data[:, :, i].astype(np.int32), 0.4);
plt.imshow(result);
plt.show();
plt.close();
