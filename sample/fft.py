import numpy as np;
from jpeg import jpeg;

jpeg.fft_preprocess(8);
a = np.array([1,2,3,4,-1,4,3,2], dtype = np.complex128);
b = jpeg.fft(a);
c = jpeg.ifft(b);

print(a);
print(b);
print(c);
