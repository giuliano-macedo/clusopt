#!/usr/bin/env python3
"""
slave.py
====================================
The slave node
"""
from network import ClientSocket,PAYID
from argparse import ArgumentParser
from collections import namedtuple
import logging
		
class Slave:
	"""
	Args:
		batch_size (int) : size of the chunks that the dataset will be splitted
		kappa (ndarray) : K's to test
	Attributes:
		
	"""
	def __init__(self,server,kappa):
		self.server=server
		self.kappa=kappa
	def run(self,server):
		"""
		main method, run slave's node algorithm
		"""
		pass

def get_args():
	parser=ArgumentParser()
	parser.add_argument("master_addr",help="address of the master")
	parser.add_argument('-v','--verbose', action='store_true',help="enbale verbose")
	args=parser.parse_args()
	if args.verbose:
		logging.basicConfig(format='[%(levelname)s]%(message)s',level=logging.DEBUG)
	return args
def main(server):
	print(f"Connected to {server.ip}")
	config=server.recv(PAYID.json).obj
	print(config)
	config=namedtuple('Config', sorted(config))(**config) #dict -> namedtuple
	
	slave_args={
		"server":server,
		"kappa":config.kappa
	}

	if config.algorithm=="minibatch":
		from slave_algorithms import SlaveMiniBatch as SlaveAlgorithm
		slave_args={**slave_args,**{
			"batch_size":config.batch_size
		}}
	elif config.algorithm=="clustream":
		from slave_algorithms import SlaveCluStream as SlaveAlgorithm
		slave_args={**slave_args,**{
			#TODO
		}}
	elif config.algorithm=="streamkm":
		from slave_algorithms import SlaveStreamkm as SlaveAlgorithm
		slave_args={**slave_args,**{
			#TODO
		}}
	else:
		raise RuntimeError("Unexpected error")
	slave=SlaveAlgorithm(**slave_args)
	slave.run()

if __name__=="__main__":
	
	args=get_args()
	server=ClientSocket(args.master_addr,3523)
	main(server)
	
	
