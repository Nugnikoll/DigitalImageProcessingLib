
CC = gcc
CXX = g++
LD = ld
AS = as
RM = rm -f
CCFLAGS = 
CXXFLAGS = -I/usr/include/python3.5m -I/home/nugnikoll/.local/lib/python3.5/site-packages/numpy/core/include -fPIC -Wall -O2 -std=c++11

CPP_DIR = ../cpp/
OBJ = $(CPP_DIR)jpeg.o $(CPP_DIR)transform.o jpeg_wrap.o
TARGET = _jpeg.so

$(TARGET): $(OBJ)
	$(CXX) -shared $(OBJ) -o $@ -lpython3.5m 

$(CPP_DIR)jpeg.o: $(CPP_DIR)jpeg.cc $(CPP_DIR)jpeg.h
	$(CXX) -c $(CXXFLAGS) $< -o $@ 

$(CPP_DIR)transform.o: $(CPP_DIR)transform.cc $(CPP_DIR)transform.h
	$(CXX) -c $(CXXFLAGS) $< -o $@ 

jpeg_wrap.o: jpeg_wrap.cc
	$(CXX) -c $(CXXFLAGS) $< -o $@ 

jpeg_wrap.cc: jpeg.i $(CPP_DIR)jpeg.h $(CPP_DIR)transform.h
	swig -python -c++ -threads -o $@ jpeg.i 
