import numpy as np;
import sys;

sys.path.append("../python");
import dipl;

dipl.fft_preprocess(8);
a = np.array([1,2,3,4,-1,4,3,2], dtype = np.complex128);
b = dipl.fft(a);
c = dipl.ifft(b);

print(a);
print(b);
print(c);
