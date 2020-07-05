#I probably don't need mt19937ar kMeansUtilityFunctions stuff

PYTHON_INCLUDES=$(shell python3 -m pybind11 --includes)
PYTHON_EXTENSION=$(shell python3-config --extension-suffix)
OUTPUT=../streamkm$(PYTHON_EXTENSION)
FLAGS=-O2 -Wall -shared -std=c++11 -fPIC $(PYTHON_INCLUDES) #-g -D DEBUG

ALL:$(OUTPUT)

stream.o:original/*.c original/*.h
	
	cd original && g++ $(FLAGS) -w *.c -c
	ld -relocatable original/*.o -o stream.o



$(OUTPUT):wrapper.hpp bindings.cpp wrapper.cpp stream.o
	g++ $(FLAGS) wrapper.cpp bindings.cpp stream.o -o $(OUTPUT)

clean:
	rm -rf stream.o original/*.o $(OUTPUT)