# MIDSC

Micro service Infrastructure for Data Stream Clustering.

![Infraestructure](imgs/midsc-1.png)

## Prerequisites

* python 3.7 (3.5 won't work, some source files have literal string interpolation)
* pip
* docker (if you use remote nodes)
* gcc >=6
* make

## Installing

Install all dependecies described in `requirements.txt` using pip,
c++ source code will be compiled in the first run.

```bash
pip3 install -r requirements.txt
```

And if you want to use remote nodes, create a file `remote_nodes.txt` in the `src` directory and put all
the ip addresses of your remote nodes.
Your nodes must be running midsc container in docker, to do so use the following commands on each remote node
```bash
docker build -t midsc .
docker run -p 3523:3523 midsc
```
then use `-n` flag to set how many nodes you want to use in the master node

## Usage
cd to the src directory 

```bash
cd src
```

---

to run master node, use `-h` and `[ALGORITHM] -h` for more help
```bash
./master.py [ALGORITHM] [PATH OR URL TO CSV FILE]
```


NOTE: CSV File must be `,` separated, `\n` line ended and **must not have a header**.

---

to run slave node, use `-h` flag for more options
```bash
./master [IP ADDRESS TO THE MASTER NODE]
```
## Authors
* **Giuliano Oliveira de Macedo** - *Coder* [llpinokio](https://github.com/llpinokio)
* **Jonathan Andrade Silva** - *Advisor*
* **Dionisio Leite Machado Filho** - *Advisor*
## Acknowledgments
Thanks to Dionisio for all the the tips to solve all the networking/cloud/virtualization related problems.
To Jonathan to all stream clustering/clustering in general /clustering evaluation information used to build this system.
---
Marcel R. Ackermann et al. for the StreamKM++ algorithm - [link](https://cs.uni-paderborn.de/cuk/forschung/abgeschlossene-projekte/dfg-schwerpunktprogramm-1307/streamkm/)
The university of Waikato for the MOA framework - [link](https://moa.cms.waikato.ac.nz/)