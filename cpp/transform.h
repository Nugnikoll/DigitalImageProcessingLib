#ifndef TRANSFROM_H
#define TRANSFORM_H

#include <complex>

using namespace std;

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
void resize_naive(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int h, int w);
void resize_near(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int h, int w);
void resize_linear(int** ptrm, int* m1, int* ptri, int i1, int n);
void resize_linear(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int h, int w);
void equalize(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int low = 0, int high = 256);

#endif //TRANSFORM_H
