import argparse
import logging
from math import ceil,sqrt
from utils import count_flines

def create_results_dir():
	path="./results"
	if os.path.exists(path) and not os.path.isdir(path):
		raise RuntimeError(f"{os.getcwd()}/results is not a directory")
	elif not os.path.exists(path):
		os.mkdir(path)

def choose_zip_fname(algorithm_name):
	for _ in range(10):
		ans=os.path.join("./results",f"{algorithm_name}_{os.urandom(4).hex()}.zip")
		if not os.path.exists(ans):
			return ans
	raise RuntimeError("Couldnt choose a .zip file")

import os

def parse_args():
	parser=argparse.ArgumentParser()
	subparsers=parser.add_subparsers(
		title="algorithm",
		help="which core algorithm will be used",
		dest="algorithm"
	)
	parser.add_argument(
		"input",
		help="path or url of the comma-separated dataset"
	)
	parser.add_argument(
		"-c",
		"--chunk_size",
		type=int,
		help="size of chunks that the dataset will be splitted (default 2000)",
		default=2000,
	)
	parser.add_argument(
		"-o",
		"--output",
		help=".zip output path that contains information on primary and replica nodes (default results/algorithm_uuid.zip)",
		default=None
	)
	parser.add_argument(
		'-n',
		'--number-nodes',
		type=int,
		help="number of docker nodes (default 0)",
		default=0
	)
	parser.add_argument(
		"-k",
		'--kappas-method',
		type=str,
		help="kappas set method (default random for minibatch, gauss for others)",
		default=None,
		choices=["gauss","v1","v2","random"]
	)
	parser.add_argument(
		"-d",
		'--distance-matrix-method',
		type=str,
		help="distance matrix computation method, for large dimensions (>~160) sklearn is recomended, else custom (default custom)",
		default="custom",
		choices=["custom","sklearn"]
	)
	parser.add_argument(
		"-s",
		'--seed',
		type=int,
		help="seed to use in the replicas algorithm (default 42)",
		default=42
	)
	parser.add_argument(
		"-R",
		'--repetitions',
		type=int,
		help="number of times to repeat replica algorithm (default 10)",
		default=10
	)
	parser.add_argument(
		'-v',
		'--verbose',
		action='store_true',
		help="enbale verbose"
	)
	parser.add_argument(
		'-l',
		'--lower-threshold',
		type=int,
		default=None,
		help="lower threshold for kappa set generation, default is sqrt(ceil(chunk_size|m|coresetsize))"
	)
	parser.add_argument(
		"-r",
		"--remote-nodes",
		type=str,
		default="./remote_nodes.txt",
		help="list of remote notes ip txt file path"
	)
	#minibatch
	#------------------------------------------------------------------------------------
	minibatch=subparsers.add_parser(
		"minibatch",
		help="MiniBatchKmeans online clustering algorithm"
	)
	#clustream
	#------------------------------------------------------------------------------------
	clustream=subparsers.add_parser(
		"clustream",
		help="CluStream online clustering algorithm"
	)
	clustream.add_argument(
		"-H",
		"--window-range",
		type=int,
		help="Range of the window (default 100)",
		default=100
	)
	clustream.add_argument(
		"-m",
		"--microclusters",
		type=int,
		default=1000,
		help="Maximum number of micro clusters to use (default 1000)"
	)
	clustream.add_argument(
		"-t",
		"--kernel-radius",
		type=int,
		default=2,
		help="Multiplier for the kernel radius (default 2)"
	)
	clustream.add_argument(
		"--clustream-seed",
		type=int,
		help="clustream Kmeans++ offline initialization random number generator seed (default: 42)",
		default=42
	)
	#streamkm
	#------------------------------------------------------------------------------------
	streamkm=subparsers.add_parser(
		"streamkm",
		help="StreamKm++ online clustering algorithm"
	)
	streamkm.add_argument(
		"-C",
		"--coreset-size",
		type=int,
		help="Number of coresets to use (default 1000)",
		default=1000
	)
	streamkm.add_argument(
		"-L",
		"--length",
		type=int,
		help="Number of datapoints to process (default:length of the dataset)",
		default=None
	)
	streamkm.add_argument(
		"--streamkm-seed",
		type=int,
		help="Streamkm++ random number generator seed (default: 42)",
		default=42
	)
	args=parser.parse_args()
	create_results_dir()
	if args.output==None:
		args.output=choose_zip_fname(args.algorithm)
	if not os.path.isfile(args.input):
		raise FileNotFoundError(args.input)
	if args.verbose:
		logging.basicConfig(format='[%(levelname)s]%(message)s',level=logging.DEBUG)
	if args.kappas_method==None:
		args.kappas_method={"minibatch":"random"}.get(args.algorithm,"gauss")
	if args.algorithm=="minibatch" and args.lower_threshold is None:
		args.lower_threshold=int(ceil(sqrt(args.chunk_size)))
	elif args.algorithm=="clustream" and args.lower_threshold is None:
		args.lower_threshold=int(ceil(sqrt(args.microclusters)))
	elif args.algorithm=="streamkm":
		if args.lower_threshold is None:
			args.lower_threshold=int(ceil(sqrt(args.coreset_size)))
		if args.length is None:
			args.length=count_flines(args.input)
	return args