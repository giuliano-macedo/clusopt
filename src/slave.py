from network import Payload,ClientSocket
import numpy as np
import json
from collections import namedtuple
from argparse import ArgumentParser
from threading import Thread,Lock
from core import Clusterer
import socket
class Slave:
	def __init__(self,**kwargs):
		self.config=namedtuple("config",list(config.keys()))(*list(config.values()))
	def __check_pay_id(pay,payid):
		if pay.id!=payid:
			raise RuntimeError(f"invalid packet id {pay.id}")
	def run(self,server):
		config=self.config
		#---------------------------------------------------------------------------------
		#get kcs
		pay=server.recv()
		Slave.__check_pay_id(pay,Payload.Id.k_coeficient)
		kc=pay.obj

		pay=server.recv()
		Slave.__check_pay_id(pay,Payload.Id.k_coeficient_inc)
		kci=pay.obj

		clusterer=Clusterer(kc,kci,config.batch_size)
		#---------------------------------------------------------------------------------
		#for every payload calc sil_score
		bc=0
		while True:
			pay=server.recv()
			if pay.id==Payload.Id.end:
				break
			Slave.__check_pay_id(pay,Payload.Id.datapoints)
			for k,sil in clusterer.add_and_get_score(pay.obj):
				server.send(Payload(Payload.Id.silhouette,(bc,k,sil)))
			bc+=1
		server.send(Payload(Payload.Id.end))


if __name__=="__main__":
	parser=ArgumentParser()
	parser.add_argument("master_addr",help="address of the master")
	args=parser.parse_args()
	with open("config.json") as f:
		config=json.load(f)
	config=dict(**vars(args),**config)
	server=ClientSocket(args.master_addr,3523)
	print(f"Connected to {server.ip}")
	Slave(**config).run(server)
