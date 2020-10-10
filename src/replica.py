#!/usr/bin/env python3
"""
replica.py
====================================
The replica node
"""
from replica.args import get_args
from replica.core import Silhouette;Silhouette #force compile
from network import ClientSocket,PAYID,ServerSocket
from collections import namedtuple
import numpy as np
from pandas import DataFrame
from os import system

def print_config(config):
	df=DataFrame([
		("algorithm:",config.algorithm),
		("seed:",config.seed),
		("repetitions:",config.repetitions),
		("distance matrix method:",config.distance_matrix_method),
		("batch_size:",config.batch_size),
		("kappa:",config.kappa),
		("kappa length:",len(config.kappa)),
		("kappa sum:",sum(config.kappa)),
		("kappa variance:",np.var(config.kappa))
	])
	print("CONFIG RECEIVED FROM MASTER")
	print("-"*48)
	print(df.to_string(header=None,index=None))
	print("-"*48)

def main(server,opts):
	print(f"Connected to {server.ip}")
	config=server.recv(PAYID.pickle).obj
	config=namedtuple('Config', sorted(config))(**config) #dict -> namedtuple
	print_config(config)
	replica_args=dict(
		server=server,
		kappa=config.kappa,
		seed=config.seed,
		repetitions=config.repetitions,
		distance_matrix_method=config.distance_matrix_method,
		batch_size=config.batch_size,
		**opts
	)

	if config.algorithm=="minibatch":
		from replica import ReplicaMiniBatch as ReplicaAlgorithm
		replica_args.update(
		)
	elif config.algorithm=="minibatchsplit":
		from replica import ReplicaMiniBatchSplit as ReplicaAlgorithm
		replica_args.update(
		)
	elif config.algorithm=="clustream":
		from replica import ReplicaCluStream as ReplicaAlgorithm
		replica_args.update(
		)
	elif config.algorithm=="streamkm":
		from replica import ReplicaStreamkm as ReplicaAlgorithm
		replica_args.update(
		)
	else:
		raise RuntimeError("Unrecognized algorith",config.algorith)
	replica=ReplicaAlgorithm(**replica_args)
	replica.run()
	print("done")

if __name__=="__main__":
	
	args=get_args()

	if args.loop!=None:
		system(f"while true; do ./replica.py {args.primary_addr} ; sleep {args.loop} ; done")
		exit()

	if args.server_mode:
		print("auxiliar server started")
		print("waiting connection:")
		aux_server=ServerSocket(3523)
		server=aux_server.accept()
		print(f"connected to {server.ip}")
	else:
		try:
			server=ClientSocket(args.primary_addr,3523)
		except ConnectionRefusedError:
			print("Error connecting to",args.primary_addr)
			exit(-1)
	opts=vars(args)
	
	#not needed in Replica class
	del(opts["primary_addr"])
	del(opts["verbose"])
	del(opts["server_mode"])
	del(opts["loop"])

	main(server,opts)
	
	
