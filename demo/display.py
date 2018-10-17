from matplotlib import pyplot as plt;
from matplotlib import cm;
import numpy as np;
from jpeg import jpeg;

jdecoder = jpeg.jpeg_decoder();

jdecoder.loadfile('../img/738b4710b912c8fcc7977bd3f1039245d6882143.jpg');
#jdecoder.loadfile('../img/JPEG_example_JPG_RIP_100.jpg');
#jdecoder._print();
data = jdecoder.decode();
#data = jdecoder.decode(True);

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

#data_next = data.copy();
#data[:, :, 0] = data_next[:, :, 0] + 1.402 * data_next[:, :, 2] + 128;
#data[:, :, 1] = data_next[:, :, 0] - 0.34414 * data_next[:, :, 1] - 0.71414 * data_next[:, :, 2] + 128;
#data[:, :, 2] = data_next[:, :, 0] + 1.772 * data_next[:, :, 1] + 128;

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

#data = data.swapaxes(0, 2).swapaxes(0, 1);
#data[data > 255] = 255;
#data[data < 0] = 0;
#data = data.astype(np.uint8)

plt.imshow(data);
plt.show();
plt.close();

plt.imshow(255 - data);
plt.show();
plt.close();
