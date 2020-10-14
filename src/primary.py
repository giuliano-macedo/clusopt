#!/usr/bin/env python3
"""
primary.py
====================================
The primary node
"""
from primary.args import parse_args
from primary.core import (
	get_kappas_gauss,
	get_kappas_v1,
	get_kappas_v2,
	get_kappas_random
)
if __name__=="__main__":
	args=parse_args()
	primary_args={
		"stream_fname":args.input,
		"chunk_size":args.chunk_size,
		"algorithm":args.algorithm,
		"output":args.output,
		"number_nodes":args.number_nodes,
		"seed":args.seed,
		"repetitions":args.repetitions,
		"lower_threshold":args.lower_threshold,
		"remote_nodes":args.remote_nodes,
		"distance_matrix_method":args.distance_matrix_method,
		"time_to_wait":args.time_to_wait,
		"ghost":args.ghost
	}
	if args.algorithm=="minibatch":
		from primary import PrimaryMiniBatch as PrimaryAlgorithm
		primary_args.update(
		)
	elif args.algorithm=="minibatchsplit":
		from primary import PrimaryMiniBatchSplit as PrimaryAlgorithm
		primary_args.update(
			microclusters=args.microclusters
		)
	elif args.algorithm=="clustream":
		from primary import PrimaryCluStream as PrimaryAlgorithm
		primary_args.update(
			window_range=args.window_range,
			microkernels=args.microclusters,
			kernel_radius=args.kernel_radius
		)
	elif args.algorithm=="streamkm":
		from primary import PrimaryStreamkm as PrimaryAlgorithm
		primary_args.update(
			coreset_size=args.coreset_size,
			length=args.length
		)
	else:
		raise RuntimeError("unexpected error")
	primary_args["kappas_method"]=dict(
		gauss=get_kappas_gauss,
		v1=get_kappas_v1,
		v2=get_kappas_v2,
		random=get_kappas_random
	)[args.kappas_method]
	primary=PrimaryAlgorithm(**primary_args)
	primary.run()
	