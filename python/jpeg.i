// -*- c++ -*-

%module jpeg

%{
	#define SWIG_FILE_WITH_INIT
%}

%include "numpy.i"

%include <std_string.i>
%include <std_array.i>
%include <std_vector.i>
%include <std_pair.i>
%include <std_complex.i>

%{
	#include "../cpp/jpeg.h"
	#include "../cpp/transform.h"
%}

%init %{
	import_array();
%}

%apply (int* INPLACE_ARRAY1, int DIM1)
{(int* ptri, int i1)};
%apply (int* INPLACE_ARRAY1, int DIM1)
{(int* ptrj, int j1)};
%apply (int** ARGOUTVIEW_ARRAY1, int* DIM1)
{(int** ptro, int* o1)};
%apply (int** ARGOUTVIEWM_ARRAY1, int* DIM1)
{(int** ptrm, int* m1)};

%apply (int* INPLACE_ARRAY2, int DIM1, int DIM2)
{(int* ptri, int i1, int i2)};
%apply (int* INPLACE_ARRAY2, int DIM1, int DIM2)
{(int* ptrj, int j1, int j2)};
%apply (int** ARGOUTVIEW_ARRAY2, int* DIM1, int* DIM2)
{(int** ptro, int* o1, int* o2)};
%apply (int** ARGOUTVIEWM_ARRAY2, int* DIM1, int* DIM2)
{(int** ptrm, int* m1, int* m2)};

%apply (int* INPLACE_ARRAY3, int DIM1, int DIM2, int DIM3)
{(int* ptri, int i1, int i2, int i3)};
%apply (int* INPLACE_ARRAY3, int DIM1, int DIM2, int DIM3)
{(int* ptrj, int j1, int j2, int j3)};
%apply (int** ARGOUTVIEW_ARRAY3, int* DIM1, int* DIM2, int* DIM3)
{(int** ptro, int* o1, int* o2, int* o3)};
%apply (int** ARGOUTVIEWM_ARRAY3, int* DIM1, int* DIM2, int* DIM3)
{(int** ptrm, int* m1, int* m2, int* m3)};

%apply (float* INPLACE_ARRAY1, int DIM1)
{(float* ptri, int i1)};
%apply (float* INPLACE_ARRAY1, int DIM1)
{(float* ptrj, int j1)};
%apply (float** ARGOUTVIEW_ARRAY1, int* DIM1)
{(float** ptro, int* o1)};
%apply (float** ARGOUTVIEWM_ARRAY1, int* DIM1)
{(float** ptrm, int* m1)};

%apply (float* INPLACE_ARRAY2, int DIM1, int DIM2)
{(float* ptri, int i1, int i2)};
%apply (float* INPLACE_ARRAY2, int DIM1, int DIM2)
{(float* ptrj, int j1, int j2)};
%apply (float** ARGOUTVIEW_ARRAY2, int* DIM1, int* DIM2)
{(float** ptro, int* o1, int* o2)};
%apply (float** ARGOUTVIEWM_ARRAY2, int* DIM1, int* DIM2)
{(float** ptrm, int* m1, int* m2)};

%apply (float* INPLACE_ARRAY3, int DIM1, int DIM2, int DIM3)
{(float* ptri, int i1, int i2, int i3)};
%apply (float* INPLACE_ARRAY3, int DIM1, int DIM2, int DIM3)
{(float* ptrj, int j1, int j2, int j3)};
%apply (float** ARGOUTVIEW_ARRAY3, int* DIM1, int* DIM2, int* DIM3)
{(float** ptro, int* o1, int* o2, int* o3)};
%apply (float** ARGOUTVIEWM_ARRAY3, int* DIM1, int* DIM2, int* DIM3)
{(float** ptrm, int* m1, int* m2, int* m3)};


%apply (double* INPLACE_ARRAY1, int DIM1)
{(double* ptri, int i1)};
%apply (double* INPLACE_ARRAY1, int DIM1)
{(double* ptrj, int j1)};
%apply (double** ARGOUTVIEW_ARRAY1, int* DIM1)
{(double** ptro, int* o1)};
%apply (double** ARGOUTVIEWM_ARRAY1, int* DIM1)
{(double** ptrm, int* m1)};

%apply (double* INPLACE_ARRAY2, int DIM1, int DIM2)
{(double* ptri, int i1, int i2)};
%apply (double* INPLACE_ARRAY2, int DIM1, int DIM2)
{(double* ptrj, int j1, int j2)};
%apply (double** ARGOUTVIEW_ARRAY2, int* DIM1, int* DIM2)
{(double** ptro, int* o1, int* o2)};
%apply (double** ARGOUTVIEWM_ARRAY2, int* DIM1, int* DIM2)
{(double** ptrm, int* m1, int* m2)};

%apply (double* INPLACE_ARRAY3, int DIM1, int DIM2, int DIM3)
{(double* ptri, int i1, int i2, int i3)};
%apply (double* INPLACE_ARRAY3, int DIM1, int DIM2, int DIM3)
{(double* ptrj, int j1, int j2, int j3)};
%apply (double** ARGOUTVIEW_ARRAY3, int* DIM1, int* DIM2, int* DIM3)
{(double** ptro, int* o1, int* o2, int* o3)};
%apply (double** ARGOUTVIEWM_ARRAY3, int* DIM1, int* DIM2, int* DIM3)
{(double** ptrm, int* m1, int* m2, int* m3)};

%apply (std::complex<double>* INPLACE_ARRAY1, int DIM1)
{(std::complex<double>* ptri, int i1)};
%apply (std::complex<double>* INPLACE_ARRAY1, int DIM1)
{(std::complex<double>* ptrj, int j1)};
%apply (std::complex<double>** ARGOUTVIEW_ARRAY1, int* DIM1)
{(std::complex<double>** ptro, int* o1)};
%apply (std::complex<double>** ARGOUTVIEWM_ARRAY1, int* DIM1)
{(std::complex<double>** ptrm, int* m1)};

%apply (std::complex<double>* INPLACE_ARRAY2, int DIM1, int DIM2)
{(std::complex<double>* ptri, int i1, int i2)};
%apply (std::complex<double>* INPLACE_ARRAY2, int DIM1, int DIM2)
{(std::complex<double>* ptrj, int j1, int j2)};
%apply (std::complex<double>** ARGOUTVIEW_ARRAY2, int* DIM1, int* DIM2)
{(std::complex<double>** ptro, int* o1, int o2)};
%apply (std::complex<double>** ARGOUTVIEWM_ARRAY2, int* DIM1, int* DIM2)
{(std::complex<double>** ptrm, int* m1, int m2)};

%apply (std::complex<double>* INPLACE_ARRAY3, int DIM1, int DIM2, int DIM3)
{(std::complex<double>* ptri, int i1, int i2, int i3)};
%apply (std::complex<double>* INPLACE_ARRAY3, int DIM1, int DIM2, int DIM3)
{(std::complex<double>* ptrj, int j1, int j2, int j3)};
%apply (std::complex<double>** ARGOUTVIEW_ARRAY3, int* DIM1, int* DIM2, int* DIM3)
{(std::complex<double>** ptro, int* o1, int o2, int o3)};
%apply (std::complex<double>** ARGOUTVIEWM_ARRAY3, int* DIM1, int* DIM2, int* DIM3)
{(std::complex<double>** ptrm, int* m1, int m2, int m3)};

%include "../cpp/jpeg.h"
%include "../cpp/transform.h"

//%template(complex_d) std::complex<double>;
//%template(ary_i) std::array<int, 64>;
//%template(ary_u16) std::array<uint16_t, >;
