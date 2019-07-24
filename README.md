# MIDSC

Micro service Infrastructure for Data Stream Clustering

## Prerequisites

* python 3.7 (3.5 won't work, some source files have f strings)
* pip
* docker

## Installing

Install all dependecies described in requirements.txt using pip as root user

```bash
pip3 install -r requirements.txt
```

and if you use docker nodes make sure to log in with your docker account with

```bash
docker login
```
and have pulled python image and built this repo

```bash
docker pull python:3.7.3
docker build -t python:3.7.3 -f dockerfile .
```

## Usage
cd to the src with directory 

```bash
cd src
```

and
to run master node, use `-h` flag for more options
```bash
./master.py [PATH OR URL TO CSV FILE]
```
to run slave node, use `-h` flag for more options
```bash
./master [IP ADDRESS TO THE MASTER NODE]
```
<!-- ## Authors

* **Giuliano Oliveira** - [llpinokio](https://github.com/llpinokio) -->