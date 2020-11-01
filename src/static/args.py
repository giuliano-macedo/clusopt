import argparse
from pathlib import Path
from utils import create_results_dir,choose_zip_fname
from primary.core import Stream
from .algos import (
	StaticClustream,
	StaticStreamkm,
	StaticMinibatch,
	StaticMinibatchSplit,
)

def parse_args():
	parser=argparse.ArgumentParser()
	subparsers=parser.add_subparsers(
		title="algorithm",
		help="which core algorithm will be used",
		dest="algorithm"
	)
	parser.add_argument(
		"input",
		help="path or url of the comma-separated dataset",
		type=Path
	)
	parser.add_argument(
		"k",
		help="number of final clusters",
		type=int
	)
	parser.add_argument(
		"-c",
		"--chunk-size",
		type=int,
		help="size of chunks that the dataset will be splitted (default 2000)",
		default=2000,
	)
	parser.add_argument(
		"-o",
		"--output",
		help=".zip output path that contains information on primary and replica nodes (default results/algorithm_uuid.zip)",
		type=Path,
		default=None
	)
	parser.add_argument(
		"-s",
		'--seed',
		type=int,
		help="seed to use in both replicas and primary (default 42)",
		default=42
	)
	#minibatch
	#------------------------------------------------------------------------------------
	minibatch=subparsers.add_parser(
		StaticMinibatch.NAME,
		help="MiniBatchKmeans online clustering algorithm"
	);minibatch
	
	#minibatch split
	minibatch_split=subparsers.add_parser(
		StaticMinibatchSplit.NAME,
		help="Modified minibatch with micro-macro clustering"
	)
	minibatch_split.add_argument(
		"-m",
		"--microclusters",
		type=int,
		default=1000,
		help="number of microclusters to use (default 1000)"
	)

	#------------------------------------------------------------------------------------
	#clustream
	#------------------------------------------------------------------------------------
	clustream=subparsers.add_parser(
		StaticClustream.NAME,
		help="CluStream online clustering algorithm"
	)
	clustream.add_argument(
		"-H",
		"--window-range",
		type=int,
		help="Range of the window (default length of the dataset)",
		default=None
	)
	clustream.add_argument(
		"-m",
		"--microclusters",
		type=int,
		default=1000,
		help="Maximum number of micro clusters to use (default 1000)"
	)
	clustream.add_argument(
		"-T",
		"--kernel-radius",
		type=int,
		default=2,
		help="Multiplier for the kernel radius (default 2)"
	)
	#streamkm
	#------------------------------------------------------------------------------------
	streamkm=subparsers.add_parser(
		StaticStreamkm.NAME,
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
	args=parser.parse_args()
	create_results_dir()
	if args.output==None:
		args.output=choose_zip_fname(args.algorithm+"_static")
	if not args.input.exists():
		raise FileNotFoundError(str(args.input))

	args.input=Stream(
		args.input,
		args.chunk_size,
		"float32" if args.algorithm=="minibatch" else "float64"
	)

	algo_args=dict(k=args.k,seed=args.seed)
	if args.algorithm==StaticClustream.NAME:
		Algorithm=StaticClustream
		algo_args.update(
			window_range=args.window_range if args.window_range!=None else args.input.lines,
			microclusters=args.microclusters,
			kernel_radius=args.kernel_radius
		)
	elif args.algorithm==StaticStreamkm.NAME:
		Algorithm=StaticStreamkm
		algo_args.update(
			coresetsize=args.coreset_size,
			length=args.length if args.length!=None else args.input.lines
		)
	elif args.algorithm==StaticMinibatch.NAME:
		Algorithm=StaticMinibatch
		algo_args.update(
			chunk_size=args.chunk_size
		)
	elif args.algorithm==StaticMinibatchSplit.NAME:
		Algorithm=StaticMinibatchSplit
		algo_args.update(
			chunk_size=args.chunk_size,
			microclusters=args.microclusters
		)
	else:
		raise RuntimeError("not recognized algorithm")

	args.algorithm=Algorithm(**algo_args)
	return args