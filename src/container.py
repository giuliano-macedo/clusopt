#!/usr/bin/env python3
"""
container.py
====================================
The container node, uses the same slave algorithm, but it creates an auxiliar server first, when the first
socket connects, it assumes it have a master node executing, so it connects itself as a slave.
"""
from slave import main
import logging
from network import ServerSocket
from argparse import ArgumentParser

if __name__=="__main__":

	parser=ArgumentParser()
	parser.add_argument('-v','--verbose', action='store_true',help="enbale verbose")
	args=parser.parse_args()
	if args.verbose:
		logging.basicConfig(format='[%(levelname)s]%(message)s',level=logging.DEBUG)

	print("auxiliar server started")
	server=ServerSocket(3523)
	master=server.accept()
	print(f"connected to {master.ip}")
	main(master)
