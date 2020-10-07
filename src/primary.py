#!/usr/bin/env python3
"""
primary.py
====================================
The primary node
"""
from primary.args import parse_args
from primary.core import (
	Stream,
	get_kappas_gauss,
	get_kappas_v1,
	get_kappas_v2,
	get_kappas_random
)
if __name__=="__main__":
	args=parse_args()
	primary_args={
		"algorithm":args.algorithm,
		"output":args.output,
		"number_nodes":args.number_nodes,
		"seed":args.seed,
		"repetitions":args.repetitions,
		"lower_threshold":args.lower_threshold,
		"remote_nodes":args.remote_nodes,
		"distance_matrix_method":args.distance_matrix_method,
		"time_to_wait":args.time_to_wait
	}
	if args.algorithm=="minibatch":
		from primary import PrimaryMiniBatch as PrimaryAlgorithm
		primary_args={**primary_args,**{
		}}
	elif args.algorithm=="clustream":
		from primary import PrimaryCluStream as PrimaryAlgorithm
		primary_args={**primary_args,**{
			"window_range":args.window_range,
			"microkernels":args.microclusters,
			"kernel_radius":args.kernel_radius,
			"clustream_seed":args.clustream_seed
		}}
	elif args.algorithm=="streamkm":
		from primary import PrimaryStreamkm as PrimaryAlgorithm
		primary_args={**primary_args,**{
			"coreset_size":args.coreset_size,
			"length":args.length,
			"streamkm_seed":args.streamkm_seed
		}}
	else:
		raise RuntimeError("unexpected error")
	primary_args["kappas_method"]=dict(
		gauss=get_kappas_gauss,
		v1=get_kappas_v1,
		v2=get_kappas_v2,
		random=get_kappas_random
	)[args.kappas_method]
	primary_args["stream"]=Stream(args.input,args.chunk_size,PrimaryAlgorithm.BATCH_DTYPE)
	primary=PrimaryAlgorithm(**primary_args)
	primary.run()
	