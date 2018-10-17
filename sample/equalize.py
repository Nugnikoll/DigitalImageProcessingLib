from matplotlib import pyplot as plt;
from matplotlib import cm;
from PIL import Image as image;
import numpy as np;
from jpeg import jpeg;

#img = image.open("../img/IMG_20181016_020153.jpg");
img = image.open("../img/IMG_20181016_023212.jpg");
#img = image.open("../img/IMG_20181016_020223.jpg");
#img = image.open("../img/738b4710b912c8fcc7977bd3f1039245d6882143.jpg");
data = np.array(img.getdata(), dtype = np.uint8);
data = data.reshape((img.height, img.width, 3));

plt.imshow(data);
plt.show();
plt.close();

result = data.copy();
result[:, :, 0] = jpeg.equalize(result[:, :, 0].astype(np.int32), np.min(result[:, :, 0]), np.max(result[:, :, 0]));
result[:, :, 1] = jpeg.equalize(result[:, :, 1].astype(np.int32), np.min(result[:, :, 1]), np.max(result[:, :, 1]));
result[:, :, 2] = jpeg.equalize(result[:, :, 2].astype(np.int32), np.min(result[:, :, 2]), np.max(result[:, :, 2]));
result = result.astype(np.uint8);

plt.imshow(result);
plt.show();
plt.close();

result = jpeg.rgb2ycc(data.astype(np.int32));
result[:, :, 0] = jpeg.equalize(result[:, :, 0].astype(np.int32), -128, 128);
result[:, :, 1] = jpeg.equalize(result[:, :, 1].astype(np.int32), np.min(result[:, :, 1]), np.max(result[:, :, 1]));
result[:, :, 2] = jpeg.equalize(result[:, :, 2].astype(np.int32), np.min(result[:, :, 2]), np.max(result[:, :, 2]));
result = jpeg.ycc2rgb(result);
result[result > 255] = 255;
result[result < 0] = 0;
result = result.astype(np.uint8);

plt.imshow(result);
plt.show();
plt.close();
