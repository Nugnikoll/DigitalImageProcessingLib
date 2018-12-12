#include <iostream>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <cstring>
#include <cassert>

#include "transform.h"

using namespace std;

default_random_engine engine(
	chrono::system_clock::now().time_since_epoch().count()
);

void padding(
	int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2,
	const int& margin_t, const int& margin_b,
	const int& margin_l, const int& margin_r, const int& value
){
	*m1 = margin_t + i1 + margin_b;
	*m2 = margin_l + i2 + margin_r;
	*ptrm = new int[*m1 * *m2];

	for(int i = 0; i != *m1; ++i){
		for(int j = 0; j != *m2; ++j){
			*ptrm[i * *m2 + j] = value;
		}
	}

	for(int i = 0; i != i1; ++i){
		for(int j = 0; j != i2; ++j){
			*ptrm[(i + margin_t) * *m2 + j + margin_l] = ptri[i * i2 + j];
		}
	}
}

void trim(
	int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2,
	const int& margin_t, const int& margin_b,
	const int& margin_l, const int& margin_r
){
	*m1 = - margin_t + i1 - margin_b;
	*m2 = - margin_l + i2 - margin_r;
	*ptrm = new int[*m1 * *m2];

	for(int i = 0; i != *m1; ++i){
		for(int j = 0; j != *m2; ++j){
			*ptrm[i * *m2 + j] = ptri[(i + margin_t) * i2 + j + margin_l];
		}
	}
}

int reverse_bit(const int& x, const int& n){
	int result = 0;
	for(int i = 0; i != n; ++i){
		result <<= 1;
		if(x & (1 << i)){
			result |= 1;
		}
	}
	return result;
}

const double pi = 3.141592653589793238462643383279502884197175105;
double table_sin[1024], table_cos[1024];
int table_reverse[1024];

void fft_preprocess(const int& size){
	#if __cplusplus >= 201103L
		int p = log2(size);
	#else
		int p = log(size) / log(2);
	#endif
	for(int i = 0; i != size; ++i){
		table_sin[i] = sin(2 * i * pi / size);
		table_cos[i] = cos(2 * i * pi / size);
		table_reverse[i] = reverse_bit(i, p);
	}
}

void fft(const int& size, double* in_real, double* in_img, double* out_real, double* out_img, const int& step){
	#if __cplusplus >= 201103L
		int p = log2(size);
	#else
		int p = log(size) / log(2);
	#endif
	int i1, i2;
	double cs, cc;
	double t1_real, t1_img, t2_real, t2_img;

	for(int i = 0; i != size; ++i){
		out_real[i * step] = in_real[table_reverse[i] * step];
		out_img[i * step] = in_img[table_reverse[i] * step];
	}

	for(int i = 0; i != p; ++i){
		for(int j = 0; j != 1 << (p - i - 1); ++j){
			for(int k = 0; k != 1 << i; ++k){
				i1 = ((j << (i + 1)) + k) * step;
				i2 = i1 + (1 << i) * step;
				cs = table_sin[k << (p - i - 1)];
				cc = table_cos[k << (p - i - 1)];
				t1_real = out_real[i1];
				t1_img = out_img[i1];
				t2_real = out_real[i2];
				t2_img = out_img[i2];
				out_real[i1] = t1_real + cc * t2_real + cs * t2_img;
				out_img[i1] = t1_img - cs * t2_real + cc * t2_img;
				out_real[i2] = t1_real - cc * t2_real - cs * t2_img;
				out_img[i2] = t1_img + cs * t2_real - cc * t2_img;
			}
		}
	}
}

void ifft(const int& size, double* in_real, double* in_img, double* out_real, double* out_img, const int& step){
	#if __cplusplus >= 201103L
		int p = log2(size);
	#else
		int p = log(size) / log(2);
	#endif
	int i1, i2;
	double cs, cc;
	double t1_real, t1_img, t2_real, t2_img;

	for(int i = 0; i != size; ++i){
		out_real[i * step] = in_real[table_reverse[i] * step];
		out_img[i * step] = in_img[table_reverse[i] * step];
	}

	for(int i = 0; i != p; ++i){
		for(int j = 0; j != 1 << (p - i - 1); ++j){
			for(int k = 0; k != 1 << i; ++k){
				i1 = ((j << (i + 1)) + k) * step;
				i2 = i1 + (1 << i) * step;
				cs = - table_sin[k << (p - i - 1)];
				cc = table_cos[k << (p - i - 1)];
				t1_real = out_real[i1];
				t1_img = out_img[i1];
				t2_real = out_real[i2];
				t2_img = out_img[i2];
				out_real[i1] = t1_real + cc * t2_real + cs * t2_img;
				out_img[i1] = t1_img - cs * t2_real + cc * t2_img;
				out_real[i2] = t1_real - cc * t2_real - cs * t2_img;
				out_img[i2] = t1_img + cs * t2_real - cc * t2_img;
			}
		}
	}

	for(int i = 0; i != size; ++i){
		out_real[i * step] /= size;
		out_img[i * step] /= size;
	}
}

void fft(std::complex<double>** ptrm, int* m1, std::complex<double>* ptri, int i1){
	*m1 = i1;
	*ptrm = new complex<double>[i1];
	fft(i1, (double*)ptri, ((double*)ptri) + 1, (double*)*ptrm, ((double*)*ptrm) + 1, 2);
}

void ifft(std::complex<double>** ptrm, int* m1, std::complex<double>* ptri, int i1){
	*m1 = i1;
	*ptrm = new complex<double>[i1];
	ifft(i1, (double*)ptri, ((double*)ptri) + 1, (double*)*ptrm, ((double*)*ptrm) + 1, 2);
}

void dct(const int& size, double* data_in, double* data_out, const int& step = 1){
	const double c[2] = {1.0 / sqrt(2.0), 1};
	double temp;

	for(int i = 0; i != size; ++i){
		temp = 0;
		for(int j = 0; j != size; ++j){
			temp += data_in[j * step] * table_cos[(2 * j + 1) * i % (size * 4)];
		}
		data_out[i * step] = c[i != 0] * temp;
	}
}

void idct(const int& size, double* data_in, double* data_out, const int& step = 1){
	const double c[2] = {1.0 / sqrt(2.0), 1};
	double temp;

	for(int j = 0; j != size; ++j){
		temp = 0;
		for(int i = 0; i != size; ++i){
			temp += c[i != 0] * data_in[i * step] * table_cos[(2 * j + 1) * i % (size * 4)];
		}
		data_out[j * step] = temp * 2 / size;
	}
}

void dct(double** ptrm, int* m1, double* ptri, int i1){
	*m1 = i1;
	*ptrm = new double[i1];
	dct(i1, ptri, *ptrm);
}
void idct(double** ptrm, int* m1, double* ptri, int i1){
	*m1 = i1;
	*ptrm = new double[i1];
	idct(i1, ptri, *ptrm);
}

//void fct_preprocess(const int& size){
//	#if __cplusplus >= 201103L
//		int p = log2(size);
//	#else
//		int p = log(size) / log(2);
//	#endif
//	for(int i = 0; i != size * 4; ++i){
//		table_sin[i] = sin(i * pi / size / 2);
//		table_cos[i] = cos(i * pi / size / 2);
//	}
//	for(int i = 0; i != size; ++i){
//		table_reverse[i] = reverse_bit(i, p);
//	}
//}

//void fct(const int& size, double* data_in, double* data_out, const int& step = 1){
//	#if __cplusplus >= 201103L
//		int p = log2(size) + 1;
//	#else
//		int p = log(size) / log(2) + 1;
//	#endif
//	int i1, i2;
//	double cs, cc;
//	double t1, t2;
//	double* buffer = new double[size << 1];

//	for(int i = 0; i != size; ++i){
//		buffer[i] = data_in[table_reverse[i] * step];
//		buffer[i] = data_in[(size * 2 - table_reverse[i] - 1) * step];
//	}

//	for(int i = 0; i != p; ++i){
//		for(int j = 0; j != 1 << (p - i - 1); ++j){
//			for(int k = 0; k != 1 << i; ++k){
//				i1 = ((j << (i + 1)) + k);
//				i2 = i1 + (1 << i);
//				cc = table_cos[k << (p - i - 1)];
//				t1 = buffer[i1];
//				t2 = buffer[i2];
//				buffer[i1] = t1 + cc * t2;
//				buffer[i2] = t1 - cc * t2;
//			}
//		}
//	}

//	for(int i = 0; i != size; ++i){
//		data_out[i * step] = buffer[i];
//	}

//	delete buffer;
//}
//void fct(double** ptrm, int* m1, double* ptri, int i1){
//	*m1 = i1;
//	*ptrm = new double[i1];
//	fct(i1, ptri, *ptrm);
//}

void rgb2ycc(int** ptrm, int* m1, int* m2, int* m3, int* ptri, int i1, int i2, int i3){
	assert(i3 == 3);

	*m1 = i1;
	*m2 = i2;
	*m3 = i3;
	*ptrm = new int[i1 * i2 * i3];

	for(int i = 0; i != i1; ++i){
		for(int j = 0; j != i2; ++j){
			(*ptrm)[(i * i2 + j) * i3 + 0] =
				0.299 * ptri[(i * i2 + j) * i3 + 0]
				+ 0.5870 * ptri[(i * i2 + j) * i3 + 1]
				+ 0.114 * ptri[(i * i2 + j) * i3 + 2] - 128;
			(*ptrm)[(i * i2 + j) * i3 + 1] = 
				- 0.1687 * ptri[(i * i2 + j) * i3 + 0]
				- 0.3313 * ptri[(i * i2 + j) * i3 + 1]
				+ 0.5 * ptri[(i * i2 + j) * i3 + 2];
			(*ptrm)[(i * i2 + j) * i3 + 2] =
				0.5 * ptri[(i * i2 + j) * i3 + 0]
				- 0.4187 * ptri[(i * i2 + j) * i3 + 1]
				- 0.0813 * ptri[(i * i2 + j) * i3 + 2];
		}
	}
}

void ycc2rgb(int** ptrm, int* m1, int* m2, int* m3, int* ptri, int i1, int i2, int i3){
	assert(i3 == 3);

	*m1 = i1;
	*m2 = i2;
	*m3 = i3;
	*ptrm = new int[i1 * i2 * i3];

	for(int i = 0; i != i1; ++i){
		for(int j = 0; j != i2; ++j){
			(*ptrm)[(i * i2 + j) * i3 + 0] =
				ptri[(i * i2 + j) * i3 + 0]
				+ 1.402 * ptri[(i * i2 + j) * i3 + 2] + 128;
			(*ptrm)[(i * i2 + j) * i3 + 1] = 
				ptri[(i * i2 + j) * i3 + 0]
				- 0.34414 * ptri[(i * i2 + j) * i3 + 1]
				- 0.71414 * ptri[(i * i2 + j) * i3 + 2] + 128;
			(*ptrm)[(i * i2 + j) * i3 + 2] =
				ptri[(i * i2 + j) * i3 + 0]
				+ 1.772 * ptri[(i * i2 + j) * i3 + 1] + 128;
		}
	}
}

void power_law(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, double gamma){
	*m1 = i1;
	*m2 = i2;
	*ptrm = new int[i1 * i2];

	for(int i = 0; i != i1; ++i){
		for(int j = 0; j != i2; ++j){
			(*ptrm)[i * i2 + j] = pow(double(ptri[i * i2 + j]) / 255, gamma) * 255;
		}
	}
}

void map_linear(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int h, int w, int y, int x, double scale){
	*m1 = h;
	*m2 = w;
	*ptrm = new int[h * w];

	for(int i = 0; i != h; ++i){
		for(int j = 0; j != w; ++j){
			(*ptrm)[i * w + j] = ptri[int(round((i + 0.5 - y) / scale - 0.5) * i2 + round((j + 0.5 - x) / scale - 0.5))];
		}
	}
}

void map_linear3(int** ptrm, int* m1, int* m2, int* m3, int* ptri, int i1, int i2, int i3, int h, int w, int y, int x, double scale){
	*m1 = h;
	*m2 = w;
	*m3 = i3;
	*ptrm = new int[h * w * i3];

	for(int i = 0; i != h; ++i){
		for(int j = 0; j != w; ++j){
			for(int k = 0; k != i3; ++k){
				(*ptrm)[(i * w + j) * i3 + k]
					= ptri[(int(round((i + 0.5 - y) / scale - 0.5) * i2 + round((j + 0.5 - x) / scale - 0.5))) * i3 + k];
			}
		}
	}
}

void resize_naive(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int h, int w){
	*m1 = h;
	*m2 = w;
	*ptrm = new int[h * w];

	for(int i = 0; i != h; ++i){
		for(int j = 0; j != w; ++j){
			(*ptrm)[i * w + j] = ptri[(i * i1 / h) * i2 + (j * i2 / w)];
		}
	}
}

void resize_near(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int h, int w){
	*m1 = h;
	*m2 = w;
	*ptrm = new int[h * w];

	for(int i = 0; i != h; ++i){
		for(int j = 0; j != w; ++j){
			(*ptrm)[i * w + j] = ptri[int(round((i + 0.5) * i1 / h - 0.5) * i2 + round((j + 0.5) * i2 / w - 0.5))];
		}
	}
}

void shrink_mean(int* ptrm, int n, int* ptri, int i1, int step = 1){
	double n_min, n_max;
	int n_i;
	double value;
	double ratio = double(n) / i1;

	for(int i = 0; i != n; ++i){
		value = 0;
		n_min = double(i) * i1 / n;
		n_max = double(i + 1) * i1 / n;

		n_i = ceil(n_min);
		if(n_i > n_min){
			value += ptri[n_i * step] * (n_i - n_min);
		}
		for(n_i = ceil(n_min); n_i < floor(n_max); ++n_i){
			value += ptri[n_i * step];
		}
		n_i = floor(n_max);
		if(n_i < n_max){
			value += ptri[n_i * step] * (n_max - n_i);
		}

		ptrm[i * step] = value * ratio;
	}
}

void enlarge_linear(int* ptrm, int n, int* ptri, int i1, int step = 1){
	double n_i;
	int n_min, n_max;

	for(int i = 0; i != n; ++i){
		n_i = double(i * (i1 - 1)) / n;
		n_min = floor(n_i);
		n_max = ceil(n_i);

		if(n_min == n_max){
			ptrm[i * step] = ptri[n_min * step];
		}else{
			ptrm[i * step] = ptri[n_min * step] * (n_max - n_i) + ptri[n_max * step] * (n_i - n_min);
		}
	}
}

void resize_linear(int* ptrm, int n, int* ptri, int i1, int step = 1){
	if(n > i1){
		enlarge_linear(ptrm, n, ptri, i1, step);
	}else if(n < i1){
		shrink_mean(ptrm, n, ptri, i1, step);
	}else{
		for(int i = 0; i != n; ++i){
			ptrm[i * step] = ptri[i * step];
		}
	}
}

void resize_linear(int** ptrm, int* m1, int* ptri, int i1, int n){
	*m1 = n;
	*ptrm = new int[n];

	resize_linear(*ptrm, n, ptri, i1);
}

void resize_linear(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int h, int w){
	int* ptr_mid;

	*m1 = h;
	*m2 = w;
	*ptrm = new int[h * w];
	ptr_mid = new int[i1 * w];

	for(int i = 0; i != i1; ++i){
		resize_linear(ptr_mid + i * w, w, ptri + i * i2, i2, 1);
	}
	for(int i = 0; i != w; ++i){
		resize_linear(*ptrm + i, h, ptr_mid + i, i1, w);
	}

	delete ptr_mid;
}

void equalize(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int low, int high){
	int bound_l = *min_element(ptri, ptri + i1 * i2);
	int bound_h = *max_element(ptri, ptri + i1 * i2) + 1;
	int range = bound_h - bound_l;
	long long* table_count = new long long[range];
	long long* table_map = new long long[range];
	long long sum, acc;

	*m1 = i1;
	*m2 = i2;
	*ptrm = new int[i1 * i2];

	memset(table_count, 0, sizeof(long long) * range);
	for(int i = 0; i != i1; ++i){
		for(int j = 0; j != i2; ++j){
			++table_count[ptri[i * i2 + j] - bound_l];
		}
	}

	sum = accumulate(table_count, table_count + range, 0);
	acc = 0;
	for(int i = 0; i != range; ++i){
		table_map[i] = (acc * 2 + table_count[i]) * (high - low) / 2 / sum + low;
		acc += table_count[i];
	}

	for(int i = 0; i != i1; ++i){
		for(int j = 0; j != i2; ++j){
			(*ptrm)[i * i2 + j] = table_map[ptri[i * i2 + j] - bound_l];
		}
	}

	delete table_count;
	delete table_map;
}

void differentiate(const int& size, int* data_in, int* data_out, const int& step = 1){
	for(int i = 0; i != size - 1; ++i){
		data_out[i * step] = data_in[(i + 1) * step] - data_in[i * step];
	}
}

void laplacian(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2){
	int* buffer_v;
	int* buffer_h;

	*m1 = i1;
	*m2 = i2;
	*ptrm = new int[i1 * i2];
	buffer_v = new int[i1 * i2];
	buffer_h = new int[i1 * i2];

	for(int i = 0; i != i2; ++i){
		differentiate(i1, ptri + i, *ptrm + i, i2);
	}
	for(int i = 0; i != i2; ++i){
		differentiate(i1 - 1, *ptrm + i, buffer_v + i + i2, i2);
	}

	for(int i = 0; i != i1; ++i){
		differentiate(i2, ptri + i * i2, *ptrm + i * i2);
	}
	for(int i = 0; i != i1; ++i){
		differentiate(i2 - 1, *ptrm + i * i2, buffer_h + i * i2 + 1);
	}

	for(int i = 0; i != i2; ++i){
		buffer_v[i] = 0;
		buffer_v[i1 * i2 - i - 1] = 0;
	}
	for(int i = 0; i != i1; ++i){
		buffer_h[i * i2] = 0;
		buffer_h[i * i2 + i2 - 1] = 0;
	}

	for(int i = 0; i != i1; ++i){
		for(int j = 0; j != i2; ++j){
			(*ptrm)[i * i2 + j] = buffer_v[i * i2 + j] + buffer_h[i * i2 + j];
		}
	}

	delete buffer_v;
	delete buffer_h;
}

void correlate(double** ptrm, int* m1, double* ptri, int i1, double* ptrj, int j1){
	double value;
	*m1 = i1 + j1 - 1;
	*ptrm = new double[*m1];

	for(int i = 0; i != *m1; ++i){
		value = 0;
		for(int j = max(0, j1 - i - 1); j != min(i1 + j1 - i - 1, j1); ++j){
			value += ptri[i + j - j1 + 1] * ptrj[j];
		}
		(*ptrm)[i] = value;
	}
}

void correlate2(double** ptrm, int* m1, int* m2, double* ptri, int i1, int i2, double* ptrj, int j1, int j2){
	double value;
	*m1 = i1 + j1 - 1;
	*m2 = i2 + j2 - 1;
	*ptrm = new double[*m1 * *m2];

	for(int i = 0; i != *m1; ++i){
		for(int j = 0; j != *m2; ++j){
			value = 0;
			for(int k = max(0, j1 - i - 1); k != min(i1 + j1 - i - 1, j1); ++k){
				for(int l = max(0, j2 - j - 1); l != min(i2 + j2 - j - 1, j2); ++l){
					value += ptri[(i + k - j1 + 1) * i2 + (j + l - j2 + 1)] * ptrj[k * j2 + l];
				}
			}
			(*ptrm)[i * *m2 + j] = value;
		}
	}
}

void noise_guass(int* ptri, int i1, int i2, const double& variance){
	normal_distribution<double> dist(0, variance);
	for(int i = 0; i != i1; ++i){
		for(int j = 0; j != i2; ++j){
			ptri[i * i2 + j] += dist(engine);
		}
	}
}

void noise_salt(int* ptri, int i1, int i2, const double& probability, const int& value){
	bernoulli_distribution dist(probability);
	for(int i = 0; i != i1; ++i){
		for(int j = 0; j != i2; ++j){
			if(dist(engine)){
				ptri[i * i2 + j] += value;
			}
		}
	}
}

void filter_median(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, const int& kernel_size){
	*m1 = i1;
	*m2 = i2;
	*ptrm = new int[i1 * i2];

	vector<int> vec;
	vec.reserve(kernel_size * kernel_size);
	int median;
	int half1 = kernel_size / 2;
	int half2 = kernel_size - half1;

	for(int i = 0; i != i1; ++i){
		for(int j = 0; j != i2; ++j){
			vec.clear();
			for(int k = max(0, i - half1); k != min(i1, i + half2); ++k){
				for(int l = max(0, j - half1); l != min(i2, j + half2); ++l){
					vec.push_back(ptri[k * i2 + l]);
				}
			}
			nth_element(vec.begin(), vec.begin() + vec.size() / 2, vec.end());
			median = vec[vec.size() / 2];
			(*ptrm)[i * i2 + j] = median;
		}
	}
}
