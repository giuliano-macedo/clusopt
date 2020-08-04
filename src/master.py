#!/usr/bin/env python3
"""
master.py
====================================
The master node
"""
import os
from master.args import parse_args
from master.core import (
	Stream,get_kappas_gauss,
	get_kappas_v1,
	get_kappas_v2,
	get_kappas_random
)

def create_results_dir():
	path="./results"
	if os.path.exists(path) and not os.path.isdir(path):
		raise RuntimeError(f"{os.getcwd()}/results is not a directory")
	elif not os.path.exists(path):
		os.mkdir(path)

if __name__=="__main__":
	args=parse_args()
	create_results_dir()
	master_args={
		"algorithm":args.algorithm,
		"number_nodes":args.number_nodes,
		"seed":args.seed,
		"repetitions":args.repetitions,
		"lower_threshold":args.lower_threshold,
		"remote_nodes":args.remote_nodes,
		"distance_matrix_method":args.distance_matrix_method
	}
	if args.algorithm=="minibatch":
		from master import MasterMiniBatch as MasterAlgorithm
		master_args={**master_args,**{
		}}
	elif args.algorithm=="clustream":
		from master import MasterCluStream as MasterAlgorithm
		master_args={**master_args,**{
			"window_range":args.window_range,
			"microkernels":args.microclusters,
			"kernel_radius":args.kernel_radius,
			"clustream_seed":args.clustream_seed
		}}
	elif args.algorithm=="streamkm":
		from master import MasterStreamkm as MasterAlgorithm
		master_args={**master_args,**{
			"coreset_size":args.coreset_size,
			"length":args.length,
			"streamkm_seed":args.streamkm_seed
		}}
	else:
		raise RuntimeError("unexpected error")
	master_args["kappas_method"]=dict(
		gauss=get_kappas_gauss,
		v1=get_kappas_v1,
		v2=get_kappas_v2,
		random=get_kappas_random
	)[args.kappas_method]
	master_args["stream"]=Stream(args.input,args.chunk_size,MasterAlgorithm.BATCH_DTYPE)
	master=MasterAlgorithm(**master_args)
	master.run()
	