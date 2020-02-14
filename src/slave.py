#!/usr/bin/env python3
"""
slave.py
====================================
The slave node
"""
from network import Payload,ClientSocket,PAYID
from collections import namedtuple
from argparse import ArgumentParser
from core import Clusterer
import logging
		
class Slave:
	"""
	Args:
		batch_size (int) : size of the chunks that the dataset will be splitted
	Attributes:
		
	"""
	def __init__(self):
		pass
	def run(self,server):
		"""
		main method, run slave's node algorithm
		"""
		config=self.config
		#---------------------------------------------------------------------------------
		#get kcs
		pay=server.recv(PAYID.k_coeficient)
		kc=pay.obj

		pay=server.recv(PAYID.k_coeficient_inc)
		kci=pay.obj

		clusterer=Clusterer(kc,kci,config.batch_size)
		#---------------------------------------------------------------------------------
		#for every payload calc sil_score
		bc=0
		while True:
			pay=server.recv(PAYID.datapoints,PAYID.end)
			if pay.id==PAYID.end:
				print(f"ended with {bc}")
				break
			for k,sil in clusterer.add_and_get_score(pay.obj):
				server.send(Payload(PAYID.silhouette,(bc,k,sil)))
			print(f"i am finished with t={bc}")
			bc+=1
		server.send(Payload(PAYID.end))
		#---------------------------------------------------------------------------------
		#check if is winner for some k and t
		while True:
			pay=server.recv(PAYID.labels_req,PAYID.end)
			if pay.id==PAYID.labels_req:
				t,k=pay.obj
				print(f"i am the winner for t={t} and k={k}")
				winner_shelve=next((shelve for shelve in clusterer.drawer if shelve.k==k),None) #TODO O(N) but not that slow
				if winner_shelve==None:
					server.send(Payload(PAYID.err))
					raise RuntimeError(f"Requested k not found ({pay.obj}) ks available {[o.k for o in clusterer.drawer]}")
				tbatch_size=t*config.batch_size
				tbatch_size_plus=(t+1)*config.batch_size
				server.send(Payload(PAYID.labels,winner_shelve.labels[tbatch_size:tbatch_size_plus]))
			elif pay.id==PAYID.end:
				break

if __name__=="__main__":
	parser=ArgumentParser()
	parser.add_argument("master_addr",help="address of the master")
	parser.add_argument('-v','--verbose', action='store_true',help="enbale verbose")
	args=parser.parse_args()
	if args.verbose:
		logging.basicConfig(format='[%(levelname)s]%(message)s',level=logging.DEBUG)
	server=ClientSocket(args.master_addr,3523)
	print(f"Connected to {server.ip}")
	config=server.recv(PAYID.json).obj
	print(config)
	server.send(Payload(PAYID.err))
	
