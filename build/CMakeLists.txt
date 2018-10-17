cmake_minimum_required (VERSION 2.6)
project (reversi)
set (REVERSI_VERSION 2.1)

set (CMAKE_VERBOSE_MAKEFILE ON)

include (CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG ("-std=c++11" COMPILER_SUPPORTS_CXX11)
if (NOT COMPILER_SUPPORTS_CXX11)
    message(FATAL_ERROR "Compiler ${CMAKE_CXX_COMPILER} has no C++11 support.")
endif ()

set (cpp_dir "${PROJECT_SOURCE_DIR}/../cpp")
set (python_dir "${PROJECT_SOURCE_DIR}/../python")

if (WIN32)
	if ("${CMAKE_SIZEOF_VOID_P}" EQUAL "8")
		set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -D_hypot=hypot -DMS_WIN64")
	else ()
		set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -D_hypot=hypot -DMS_WIN32")
	endif ()
else ()
	set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")
endif ()
set (CMAKE_CXX_FLAGS_DEBUG "-Og -g -DDEBUG")
set (CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")

set (CMAKE_SHARED_LIBRARY_PREFIX "")

include (FindPythonLibs)
include (FindPythonInterp)
message (${PYTHON_LIBRARIES})
execute_process(
	COMMAND "${PYTHON_EXECUTABLE}" "-c"
	"import numpy; print(numpy.get_include());"
	OUTPUT_VARIABLE NUMPY_INCLUDE_DIR
)
message (${NUMPY_INCLUDE_DIR})

include_directories ("${PYTHON_INCLUDE_DIRS}" "${NUMPY_INCLUDE_DIR}")

set (
	head_file
	${cpp_dir}/jpeg.h
	${cpp_dir}/transform.h
)

set (
	source_file
	${cpp_dir}/jpeg.cc
	${cpp_dir}/transform.cc
	${python_dir}/jpeg_wrap.cc
)

add_custom_command (
	OUTPUT ${python_dir}/jpeg_wrap.cc
	COMMAND swig -python -c++ -threads -w-314,-362,-389,-503,-509 -o ${python_dir}/jpeg_wrap.cc ${python_dir}/jpeg.i
	DEPENDS ${python_dir}/jpeg.i ${head_file}
)

add_library(_jpeg SHARED ${source_file})
set_property(TARGET _jpeg PROPERTY CXX_STANDARD 11)
set_property(TARGET _jpeg PROPERTY CXX_STANDARD_REQUIRED ON)
set_property(TARGET _jpeg PROPERTY CXX_EXTENSIONS OFF)
target_link_libraries (_jpeg ${PYTHON_LIBRARIES})

if (WIN32)
	add_custom_command(TARGET _jpeg POST_BUILD
		COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:_jpeg> ${python_dir}/_jpeg.pyd
	)
else ()
	add_custom_command(TARGET _jpeg POST_BUILD
		COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:_jpeg> ${python_dir}/
	)
endif ()
