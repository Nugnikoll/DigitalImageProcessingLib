#ifndef TRANSFROM_H
#define TRANSFORM_H

#include <complex>

using namespace std;

void padding(
	int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2,
	const int& margin_t, const int& margin_b,
	const int& margin_l, const int& margin_r, const int& value = 0
);
void trim(
	int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2,
	const int& margin_t, const int& margin_b,
	const int& margin_l, const int& margin_r
);

void fft_preprocess(const int& size);
void fft(std::complex<double>** ptrm, int* m1, std::complex<double>* ptri , int i1);
void ifft(std::complex<double>** ptrm, int* m1, std::complex<double>* ptri , int i1);
void dct(double** ptrm, int* m1, double* ptri, int i1);
void idct(double** ptrm, int* m1, double* ptri, int i1);
//void fct_preprocess(const int& size);
//void fct(double** ptrm, int* m1, double* ptri, int i1);

void rgb2ycc(int** ptrm, int* m1, int* m2, int* m3, int* ptri, int i1, int i2, int i3);
void ycc2rgb(int** ptrm, int* m1, int* m2, int* m3, int* ptri, int i1, int i2, int i3);
void power_law(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, double power);
void map_linear(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int h, int w, int y, int x, double scale);
void map_linear3(int** ptrm, int* m1, int* m2, int* m3, int* ptri, int i1, int i2, int i3, int h, int w, int y, int x, double scale);
void resize_naive(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int h, int w);
void resize_near(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int h, int w);
void resize_linear(int** ptrm, int* m1, int* ptri, int i1, int n);
void resize_linear(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int h, int w);
void equalize(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int low = 0, int high = 256);

void laplacian(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2);
void correlate(double** ptrm, int* m1, double* ptri, int i1, double* ptrj, int j1);
void correlate2(double** ptrm, int* m1, int* m2, double* ptri, int i1, int i2, double* ptrj, int j1, int j2);

#endif //TRANSFORM_H
