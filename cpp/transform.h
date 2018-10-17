#ifndef TRANSFROM_H
#define TRANSFORM_H

void rgb2ycc(int** ptrm, int* m1, int* m2, int* m3, int* ptri, int i1, int i2, int i3);
void ycc2rgb(int** ptrm, int* m1, int* m2, int* m3, int* ptri, int i1, int i2, int i3);
void resize_naive(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int h, int w);
void resize_near(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int h, int w);
void resize_linear(int** ptrm, int* m1, int* ptri, int i1, int n);
void resize_linear(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int h, int w);
void equalize(int** ptrm, int* m1, int* m2, int* ptri, int i1, int i2, int low = 0, int high = 256);

#endif //TRANSFORM_H
