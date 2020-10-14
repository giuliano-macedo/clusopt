from argparse import ArgumentParser
import logging
def get_args():
	parser=ArgumentParser()
	parser.add_argument(
		"primary_addr",
		help="address of the primary"
	)
	parser.add_argument(
		"-l",
		"--loop",
		metavar="TIME",
		help="tries to connect to primary node and sleep for TIME seconds (default None, meaning 'try once')",
		type=int,
		default=None
	)

	parser.add_argument(
		'-v',
		'--verbose',
		action='store_true',
		help="enable verbose"
	)
	parser.add_argument(
		'-s',
		'--server-mode',
		action='store_true',
		help="starts as a server, so that the primary starts the connection"
	)
	parser.add_argument(
		'-m',
		'--max-mem',
		type=int,
		help="set maximum number of BATCHES to store in memory, disk cache rest (default 10)",
		metavar="BATCHES",
		default=10
	)
	
	args=parser.parse_args()
	if args.verbose:
		logging.basicConfig(format='[%(levelname)s]%(message)s',level=logging.DEBUG)
	return args