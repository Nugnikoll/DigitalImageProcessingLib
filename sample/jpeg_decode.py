from matplotlib import pyplot as plt;
from matplotlib import cm;
import numpy as np;
import sys;

sys.path.append("../python");
import jpeg;

jdecoder = jpeg.jpeg_decoder();

#jdecoder.loadfile('../img/scene.jpg');
jdecoder.loadfile('../img/JPEG_example_JPG_RIP_100.jpg');
jdecoder._print();
#data = jdecoder.decode();
data = jdecoder.decode(True);

plt.imshow(data[:, :, 0], cmap = cm.gray);
plt.show();
plt.close();
plt.imshow(data[:, :, 1], cmap = cm.gray);
plt.show();
plt.close();
plt.imshow(data[:, :, 2], cmap = cm.gray);
plt.show();
plt.close();

data = jpeg.ycc2rgb(data);

data[data > 255] = 255;
data[data < 0] = 0;
data = data.astype(np.uint8);

plt.imshow(data[:,:,0], cmap = cm.gray);
plt.show();
plt.close();
plt.imshow(data[:,:,1], cmap = cm.gray);
plt.show();
plt.close();
plt.imshow(data[:,:,2], cmap = cm.gray);
plt.show();
plt.close();

plt.imshow(data);
plt.show();
plt.close();

plt.imshow(255 - data);
plt.show();
plt.close();
