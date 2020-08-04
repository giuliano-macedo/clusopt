#!/usr/bin/env python3
"""
slave.py
====================================
The slave node
"""
from slave.args import get_args
from slave.core import Silhouette;Silhouette #force compile
from network import ClientSocket,PAYID,ServerSocket
from collections import namedtuple
import numpy as np
from pandas import DataFrame

def print_config(config):
	df=DataFrame(
		[
			("algorithm:",config.algorithm),
			("seed:",config.seed),
			("repetitions:",config.repetitions),
			("distance matrix method:",config.distance_matrix_method),
			("batch_size:",config.batch_size),
			("kappa:",config.kappa),
			("kappa length:",len(config.kappa)),
			("kappa sum:",sum(config.kappa)),
			("kappa variance:",np.var(config.kappa))
		]
	)
	print("CONFIG RECEIVED FROM MASTER")
	print("-"*48)
	print(df.to_string(header=None,index=None))
	print("-"*48)



def main(server,opts):
	print(f"Connected to {server.ip}")
	config=server.recv(PAYID.pickle).obj
	config=namedtuple('Config', sorted(config))(**config) #dict -> namedtuple
	print_config(config)
	slave_args=dict(
		server=server,
		kappa=config.kappa,
		seed=config.seed,
		repetitions=config.repetitions,
		distance_matrix_method=config.distance_matrix_method,
		batch_size=config.batch_size,
		**opts
	)

	if config.algorithm=="minibatch":
		from slave import SlaveMiniBatch as SlaveAlgorithm
		# slave_args={**slave_args,**{

		# }}
	elif config.algorithm=="clustream":
		from slave import SlaveCluStream as SlaveAlgorithm
		# slave_args={**slave_args,**{
			
		# }}
	elif config.algorithm=="streamkm":
		from slave import SlaveStreamkm as SlaveAlgorithm
		# slave_args={**slave_args,**{
			
		# }}
	else:
		raise RuntimeError("Unexpected error")
	slave=SlaveAlgorithm(**slave_args)
	slave.run()
	print("done")

if __name__=="__main__":
	
	args=get_args()
	if args.server_mode:
		print("auxiliar server started")
		print("waiting connection:")
		aux_server=ServerSocket(3523)
		server=aux_server.accept()
		print(f"connected to {server.ip}")
	else:
		try:
			server=ClientSocket(args.master_addr,3523)
		except ConnectionRefusedError:
			print("Error connecting to",args.master_addr)
			exit(-1)
	opts=vars(args)
	
	#not needed in Server class
	del(opts["master_addr"])
	del(opts["verbose"])
	del(opts["server_mode"])

	main(server,opts)
	
	
