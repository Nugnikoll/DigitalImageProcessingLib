#ifndef TRANSFROM_H
#define TRANSFORM_H

#include <complex>
#include <chrono>
#include <random>
#include <functional>

using namespace std;

#define ARRAY_1D_IN_I(TYPE) TYPE* ptri, int i1
#define ARRAY_1D_IN_J(TYPE) TYPE* ptrj, int j1
#define ARRAY_1D_OUT_O(TYPE) TYPE** ptro, int* o1
#define ARRAY_1D_OUT_M(TYPE) TYPE** ptrm, int* m1
#define ARRAY_2D_IN_I(TYPE) TYPE* ptri, int i1, int i2
#define ARRAY_2D_IN_J(TYPE) TYPE* ptrj, int j1, int j2
#define ARRAY_2D_OUT_O(TYPE) TYPE** ptro, int* o1, int* o2
#define ARRAY_2D_OUT_M(TYPE) TYPE** ptrm, int* m1, int* m2
#define ARRAY_3D_IN_I(TYPE) TYPE* ptri, int i1, int i2, int i3
#define ARRAY_3D_IN_J(TYPE) TYPE* ptrj, int j1, int j2, int j3
#define ARRAY_3D_OUT_O(TYPE) TYPE** ptro, int* o1, int* o2, int* o3
#define ARRAY_3D_OUT_M(TYPE) TYPE** ptrm, int* m1, int* m2, int* m3

extern default_random_engine engine;

void padding(
	ARRAY_2D_OUT_M(int), ARRAY_2D_IN_I(int),
	const int& margin_t, const int& margin_b,
	const int& margin_l, const int& margin_r, const int& value = 0
);
void trim(
	ARRAY_2D_OUT_M(int), ARRAY_2D_IN_I(int),
	const int& margin_t, const int& margin_b,
	const int& margin_l, const int& margin_r
);

void fft_preprocess(const int& size);
void fft(ARRAY_1D_OUT_M(std::complex<double>), ARRAY_1D_IN_I(std::complex<double>));
void ifft(ARRAY_1D_OUT_M(std::complex<double>), ARRAY_1D_IN_I(std::complex<double>));
void dct(ARRAY_1D_OUT_M(double), ARRAY_1D_IN_I(double));
void idct(ARRAY_1D_OUT_M(double), ARRAY_1D_IN_I(double));
//void fct_preprocess(const int& size);
//void fct(ARRAY_1D_OUT_M(double), ARRAY_1D_IN_I(double));

void rgb2ycc(ARRAY_3D_OUT_M(int), ARRAY_3D_IN_I(int));
void ycc2rgb(ARRAY_3D_OUT_M(int), ARRAY_3D_IN_I(int));
void power_law(ARRAY_2D_OUT_M(int), ARRAY_2D_IN_I(int), double power);
void map_linear(ARRAY_2D_OUT_M(int), ARRAY_2D_IN_I(int), int h, int w, int y, int x, double scale);
void map_linear3(ARRAY_3D_OUT_M(int), ARRAY_3D_IN_I(int), int h, int w, int y, int x, double scale);
void resize_naive(ARRAY_2D_OUT_M(int), ARRAY_2D_IN_I(int), int h, int w);
void resize_near(ARRAY_2D_OUT_M(int), ARRAY_2D_IN_I(int), int h, int w);
void resize_linear(ARRAY_1D_OUT_M(int), ARRAY_1D_IN_I(int), int n);
void resize_linear(ARRAY_2D_OUT_M(int), ARRAY_2D_IN_I(int), int h, int w);
void equalize(ARRAY_2D_OUT_M(int), ARRAY_2D_IN_I(int), int low = 0, int high = 256);

void laplacian(ARRAY_2D_OUT_M(int), ARRAY_2D_IN_I(int));
void correlate(ARRAY_1D_OUT_M(double), ARRAY_1D_IN_I(double), ARRAY_1D_IN_J(double));
void correlate2(ARRAY_2D_OUT_M(double), ARRAY_2D_IN_I(double), ARRAY_2D_IN_J(double));

void noise_guass(ARRAY_2D_IN_I(int), const double& variance);
void noise_salt(ARRAY_2D_IN_I(int), const double& probability, const int& value);

void filter_median(ARRAY_2D_OUT_M(int), ARRAY_2D_IN_I(int), const int& kernel_size);

void bezier(ARRAY_1D_OUT_M(double), ARRAY_1D_IN_I(double), int num);

#endif //TRANSFORM_H
