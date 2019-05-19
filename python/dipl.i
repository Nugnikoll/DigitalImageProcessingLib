// -*- c++ -*-

%module dipl

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

#define ARRAY_1D(TYPE) \
	%apply (TYPE* INPLACE_ARRAY1, int DIM1) \
	{(TYPE* ptri, int i1)}; \
	%apply (TYPE* INPLACE_ARRAY1, int DIM1) \
	{(TYPE* ptrj, int j1)}; \
	%apply (TYPE** ARGOUTVIEW_ARRAY1, int* DIM1) \
	{(TYPE** ptro, int* o1)}; \
	%apply (TYPE** ARGOUTVIEWM_ARRAY1, int* DIM1) \
	{(TYPE** ptrm, int* m1)};

#define ARRAY_2D(TYPE) \
	%apply (TYPE* INPLACE_ARRAY2, int DIM1, int DIM2) \
	{(TYPE* ptri, TYPE i1, TYPE i2)}; \
	%apply (TYPE* INPLACE_ARRAY2, int DIM1, int DIM2) \
	{(TYPE* ptrj, int j1, int j2)}; \
	%apply (TYPE** ARGOUTVIEW_ARRAY2, int* DIM1, int* DIM2) \
	{(TYPE** ptro, TYPE* o1, TYPE* o2)}; \
	%apply (TYPE** ARGOUTVIEWM_ARRAY2, int* DIM1, int* DIM2) \
	{(TYPE** ptrm, int* m1, int* m2)};

#define ARRAY_3D(TYPE) \
	%apply (TYPE* INPLACE_ARRAY3, int DIM1, int DIM2, int DIM3) \
	{(TYPE* ptri, int i1, int i2, int i3)}; \
	%apply (TYPE* INPLACE_ARRAY3, int DIM1, int DIM2, int DIM3) \
	{(TYPE* ptrj, int j1, int j2, int j3)}; \
	%apply (TYPE** ARGOUTVIEW_ARRAY3, int* DIM1, int* DIM2, int* DIM3) \
	{(TYPE** ptro, int* o1, int* o2, int* o3)}; \
	%apply (TYPE** ARGOUTVIEWM_ARRAY3, int* DIM1, int* DIM2, int* DIM3) \
	{(TYPE** ptrm, int* m1, int* m2, int* m3)}; \

#define ARRAY_ND(TYPE) \
	ARRAY_1D(TYPE) \
	ARRAY_2D(TYPE) \
	ARRAY_3D(TYPE)

ARRAY_ND(int)
ARRAY_ND(float)
ARRAY_ND(double)
ARRAY_ND(std::complex<double>)

%include "../cpp/jpeg.h"
%include "../cpp/transform.h"

//%template(complex_d) std::complex<double>;
//%template(ary_i) std::array<int, 64>;
//%template(ary_u16) std::array<uint16_t, >;
