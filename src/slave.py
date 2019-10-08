#!/usr/bin/env python3
from network import Payload,ClientSocket
import numpy as np
import json
from collections import namedtuple
from argparse import ArgumentParser
from threading import Thread,Lock
from core import Clusterer,CarriageClusterer
import socket
import logging
		
class Slave:

	def __init__(self,**config):
		self.config=namedtuple("config",list(config.keys()))(*list(config.values()))
	def run(self,server):
		config=self.config
		#---------------------------------------------------------------------------------
		#get kcs
		pay=server.recv(Payload.Id.k_coeficient)
		kc=pay.obj

		pay=server.recv(Payload.Id.k_coeficient_inc)
		kci=pay.obj

		clusterer=Clusterer(kc,kci,config.batch_size) if not config.carriage else CarriageClusterer(kc,kci,config.batch_size)
		#---------------------------------------------------------------------------------
		#for every payload calc sil_score
		bc=0
		while True:
			pay=server.recv(Payload.Id.datapoints,Payload.Id.end)
			if pay.id==Payload.Id.end:
				print(f"ended with {bc}")
				break
			for k,sil in clusterer.add_and_get_score(pay.obj):
				server.send(Payload(Payload.Id.silhouette,(bc,k,sil)))
			print(f"i am finished with t={bc}")
			bc+=1
		server.send(Payload(Payload.Id.end))
		#---------------------------------------------------------------------------------
		#check if is winner for some k and t
		while True:
			pay=server.recv(Payload.Id.labels_req,Payload.Id.end)
			if pay.id==Payload.Id.labels_req:
				t,k=pay.obj
				print(f"i am the winner for t={t} and k={k}")
				winner_shelve=next((shelve for shelve in clusterer.drawer if shelve.k==k),None) #TODO O(N) but not that slow
				if winner_shelve==None:
					server.send(Payload(Payload.Id.err))
					raise RuntimeError(f"Requested k not found ({pay.obj}) ks available {[o.k for o in clusterer.drawer]}")
				tbatch_size=t*config.batch_size
				tbatch_size_plus=(t+1)*config.batch_size
				server.send(Payload(Payload.Id.labels,winner_shelve.labels[tbatch_size:tbatch_size_plus]))
			elif pay.id==Payload.Id.end:
				break

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
