from matplotlib import pyplot as plt;
from matplotlib import cm;
from PIL import Image as image;
import numpy as np;
import sys;

sys.path.append("../python");
import dipl;

#img = image.open("../img/dark.jpg");
img = image.open("../img/scene.jpg");
#img = image.open("../img/artery.jpg");
data = np.array(img.getdata(), dtype = np.uint8);
data = data.reshape((img.height, img.width, 3));

plt.imshow(data);
plt.show();
plt.close();

result = data.copy();
result[:, :, 0] = dipl.equalize(result[:, :, 0].astype(np.int32), int(np.min(result[:, :, 0])), int(np.max(result[:, :, 0])));
result[:, :, 1] = dipl.equalize(result[:, :, 1].astype(np.int32), int(np.min(result[:, :, 1])), int(np.max(result[:, :, 1])));
result[:, :, 2] = dipl.equalize(result[:, :, 2].astype(np.int32), int(np.min(result[:, :, 2])), int(np.max(result[:, :, 2])));
result = result.astype(np.uint8);

plt.imshow(result);
plt.show();
plt.close();

result = dipl.rgb2ycc(data.astype(np.int32));
result[:, :, 0] = dipl.equalize(result[:, :, 0].astype(np.int32), -128, 128);
result[:, :, 1] = dipl.equalize(result[:, :, 1].astype(np.int32), int(np.min(result[:, :, 1])), int(np.max(result[:, :, 1])));
result[:, :, 2] = dipl.equalize(result[:, :, 2].astype(np.int32), int(np.min(result[:, :, 2])), int(np.max(result[:, :, 2])));
result = dipl.ycc2rgb(result);
result[result > 255] = 255;
result[result < 0] = 0;
result = result.astype(np.uint8);

plt.imshow(result);
plt.show();
plt.close();
