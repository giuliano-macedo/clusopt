# MIDSC

Micro service Infrastructure for Data Stream Clustering.

![Infraestructure](imgs/midsc-1.jpg)

## Prerequisites

* python >= 3.6
* pip
* boost-thread
* docker [optional]

## Installing

Install all dependecies described in `requirements.txt` using pip.

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
then use `-n` flag to set how many nodes you want to use in the primary node

## Usage
cd to the src directory 

```bash
cd src
```

---

to run primary node, use `-h` and `[ALGORITHM] -h` for more help
```bash
./primary.py [ALGORITHM] [PATH OR URL TO CSV FILE]
```


NOTE: CSV File must be `,` separated, `\n` line ended and **must not have a header**.

---

to run replica node, use `-h` flag for more options
```bash
./replica [IP ADDRESS TO THE PRIMARY NODE]
```

## Published Works

<a id="1">[1]</a> 
G. O. MACEDO and J. A. SILVA and D. M. L. FILHO. (2020). 
UM MODELO DE INFRAESTRUTURA DE MICROSSERVIÇOS PARA ALGORITMOS DE AGRUPAMENTO DE FLUXOS CONTÍNUOS DE DADOS.
SODEBRAS Journal, 15(178), 48-52.
https://doi.org/10.29367%2Fissn.1809-3957.15.2020.178.48

## Authors
* **Giuliano Oliveira de Macedo** - *Coder* [giuliano-oliveira](https://github.com/giuliano-oliveira)
* **Jonathan Andrade Silva** - *Advisor*
* **Dionisio Leite Machado Filho** - *Advisor*

## Acknowledgments

#### Thanks to:

* **Dionisio** for all the the tips to solve all the networking/cloud/virtualization related problems.
* **Jonathan** to all stream clustering/clustering in general /clustering evaluation information used to build this system.
* **Marcel R. Ackermann et al.** for the StreamKM++ algorithm - [link](https://cs.uni-paderborn.de/cuk/forschung/abgeschlossene-projekte/dfg-schwerpunktprogramm-1307/streamkm/)
* **The university of Waikato** for the MOA framework - [link](https://moa.cms.waikato.ac.nz/)