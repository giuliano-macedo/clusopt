import argparse
import logging
from math import ceil,sqrt
from utils import count_flines

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
		'-n',
		'--number_nodes',
		type=int,
		help="number of docker nodes (default 0)",
		default=0
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
		help="lower threshold for kappa set generation, default is sqrt(ceil(batch_size|m|coresetsize))"
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
	minibatch.add_argument(
		"-b",
		"--batch-size",
		type=int,
		help="size of chunks to send to slaves (default 2000)",
		default=2000
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
	#streamkm
	#------------------------------------------------------------------------------------
	streamkm=subparsers.add_parser(
		"streamkm",
		help="StreamKm++ online clustering algorithm"
	)
	streamkm.add_argument(
		"-c",
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
	print(args)
	if args.verbose:
		logging.basicConfig(format='[%(levelname)s]%(message)s',level=logging.DEBUG)
	if args.algorithm=="minibatch" and args.lower_threshold==None:
		args.lower_threshold=int(ceil(sqrt(args.batch_size)))
	elif args.algorithm=="clustream" and args.lower_threshold==None:
		args.lower_threshold=int(ceil(sqrt(args.microclusters)))
	elif args.algorithm=="streamkm":
		if args.lower_threshold==None:
			args.lower_threshold=int(ceil(sqrt(args.coreset_size)))
		if args.length==None:
			args.length=count_flines(args.input)
	return args