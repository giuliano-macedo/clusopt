from argparse import ArgumentTypeError,ArgumentParser
def parse_alg(s):
	ans={
		"minibatch":		"minibatch",
		"minibatchkmeans":	"minibatch",
		"clustream":		"clustream",
		"streamkm":			"streamkm",
		"streamkm++":		"streamkm",
		"streamkmeans":		"streamkm",
		"streamkmeans++":	"streamkm"
	}.get(s.lower(),None)
	if not ans:
		raise ArgumentTypeError("invalid algorithm")
	return ans
def parse_args():
	parser=ArgumentParser()
	parser.add_argument(
		"algorithm",
		help="aglortihm to use, availabe are (minibatch,clustream,streamkm)",
		type=parse_alg
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
	#minibatch
	#------------------------------------------------------------------------------------
	parser.add_argument(
		"-b",
		"--batch_size",
		type=int,
		help="(minibatch) size of chunks to send to slaves (default 2000)",
		default=2000
	)
	#clustream
	#------------------------------------------------------------------------------------
	parser.add_argument(
		"-h",
		"--window_range",
		type=int,
		help="(clustream) Range of the window (default 100)",
		default=100
	)
	parser.add_argument(
		"-m",
		"--microkernels",
		type=int,
		default=1000,
		help="(clustream) Maximum number of micro kernels to use (default 1000)"
	)
	parser.add_argument(
		"-b",
		"--batch_size",
		type=int,
		default=2,
		help="(clustream) Multiplier for the kernel radius (default 2)"
	)
	#streamkm
	#------------------------------------------------------------------------------------
	parser.add_argument(
		"-c",
		"--coreset_size",
		type=int,
		help="(streamkm) Number of coresets to use (default 1000)",
		default=1000
	)
	parser.add_argument(
		"-L",
		"--length",
		type=int,
		help="(streamkm) Number of datapoints to process (default:length of the dataset)",
		default=None
	)
	return parser.get_args()