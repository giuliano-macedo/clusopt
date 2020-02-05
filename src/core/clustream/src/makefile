PYTHON_INCLUDES=$(shell python3 -m pybind11 --includes)
PYTHON_EXTENSION=$(shell python3-config --extension-suffix)
OUTPUT=../clustream$(PYTHON_EXTENSION)
FLAGS=-g -O3 -Wall -shared -std=c++11 -fPIC $(PYTHON_INCLUDES)

ALL:$(OUTPUT)

kernel.o:kernel.cpp kernel.hpp
	g++ $(FLAGS) kernel.cpp -c -o kernel.o
clustream.o:clustream.cpp clustream.hpp
	g++ $(FLAGS) clustream.cpp -c -o clustream.o


$(OUTPUT):bindings.cpp clustream.o kernel.o
	g++ $(FLAGS) kernel.o clustream.o bindings.cpp -o $(OUTPUT)

clean:
	rm -rf clustream.o kernel.o $(OUTPUT)