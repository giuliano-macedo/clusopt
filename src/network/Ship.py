from time import sleep
from . import ClientSocket

class Ship:
	def __init__(self,n,tries=15):
		self.n=n
		self.tries=tries
		self.ips=open("remote_nodes.txt").read().split("\n")[:self.n]
		
	def get_node_sockets(self):
		for ip in self.ips:
			ans=None
			for i in range(self.tries):
				print(f"trying to connect to {ip}:3523 ({i+1})")
				try:
					ans=ClientSocket(ip,3523)
					break
				except Exception as e:
					# print(e)
					sleep(2)
					pass
			assert ans!=None,f"Error connecting to {ip}"
			yield ans
