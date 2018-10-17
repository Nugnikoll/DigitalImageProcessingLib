#include <iostream>
#include <cmath>
#include <algorithm>
#include <cstring>
#include <cassert>

#include "transform.h"

using namespace std;

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

//	cout << "bound_l: " << bound_l << " bound_h: " << bound_h << endl;
//	cout << "low: " << low << " high: " << high << endl;
//	for(int i = 0; i != range; ++i){
//		cout << table_count[i] << " ";
//	}cout << endl;
//	for(int i = 0; i != range; ++i){
//		cout << table_map[i] << " ";
//	}cout << endl;
}
