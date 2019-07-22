from network import Payload,ClientSocket
import numpy as np
import json
from collections import namedtuple
from argparse import ArgumentParser
from threading import Thread,Lock
from core import Clusterer
import socket
import logging
class Slave:
	def __init__(self,**kwargs):
		self.config=namedtuple("config",list(config.keys()))(*list(config.values()))
	def run(self,server):
		config=self.config
		#---------------------------------------------------------------------------------
		#get kcs
		pay=server.recv(Payload.Id.k_coeficient)
		kc=pay.obj

		pay=server.recv(Payload.Id.k_coeficient_inc)
		kci=pay.obj

		clusterer=Clusterer(kc,kci,config.batch_size)
		#---------------------------------------------------------------------------------
		#for every payload calc sil_score
		bc=0
		while True:
			pay=server.recv(Payload.Id.datapoints,Payload.Id.end)
			if pay.id==Payload.Id.end:
				break
			for k,sil in clusterer.add_and_get_score(pay.obj):
				server.send(Payload(Payload.Id.silhouette,(bc,k,sil)))
			bc+=1
		server.send(Payload(Payload.Id.end))
		#---------------------------------------------------------------------------------
		#check if is winner
		pay=server.recv(Payload.Id.labels_req,Payload.Id.end)
		if pay.id==Payload.Id.labels_req:
			print("i am the winner")
			winner_shelve=next((shelve for shelve in clusterer.drawer if shelve.k==pay.obj),None) #SLOW
			if winner_shelve==None:
				server.send(Payload(Payload.Id.err))
				raise RuntimeError(f"Requested k not found ({pay.obj}) ks available {[o.k for o in clusterer.drawer]}")
			server.send(Payload(Payload.Id.labels,winner_shelve.labels))
		else:
			print("i am not the winner")

if __name__=="__main__":
	parser=ArgumentParser()
	parser.add_argument("master_addr",help="address of the master")
	parser.add_argument('-v','--verbose', action='store_true',help="enbale verbose")
	args=parser.parse_args()
	if args.verbose:
		logging.basicConfig(format='[%(levelname)s]%(message)s',level=logging.DEBUG)
	with open("config.json") as f:
		config=json.load(f)
	config=dict(**vars(args),**config)
	server=ClientSocket(args.master_addr,3523)
	print(f"Connected to {server.ip}")
	Slave(**config).run(server)
