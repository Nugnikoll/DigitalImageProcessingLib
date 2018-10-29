import numpy as np;
from matplotlib import pyplot as plt;
from matplotlib import cm;
from PIL import Image as image;
from jpeg import jpeg;

#img = image.open("../img/artery.jpg");
img = image.open("../img/scene.jpg");
data = np.array(img.getdata(), dtype = np.uint8);
data = data.reshape((img.height, img.width, 3));
plt.imshow(data);
plt.show();
plt.close();

delta = np.empty(data.shape, dtype = np.int32);
delta_next = np.empty(data.shape, dtype = np.int32);
for i in range(3):
	delta[:, :, i] = jpeg.laplacian(data[:, :, i].astype(np.int32));

#for i in range(3):
#	delta_next[:, :, i] += - np.min(delta[:, :, i]);
delta_next = delta - np.min(delta);

plt.imshow(delta_next.astype(np.uint8));
plt.show();
plt.close();

result = data - delta * 0.65;
result[result < 0] = 0;
result[result > 255] = 255;
#bound_l = np.min(result, axis = (0, 1), keepdims = True);
#bound_u = np.max(result, axis = (0, 1), keepdims = True);
#result = (result - bound_l) * 255 / (bound_u - bound_l);

plt.imshow(result.astype(np.uint8));
plt.show();
plt.close();

