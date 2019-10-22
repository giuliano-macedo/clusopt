import socket
from . import Socket
class ClientSocket(Socket):
	"""
	creates a wrapped midsc.network.Socket connected to a server
	
	Args:
		addr (str): Ip to the server
		port (int): port to connect to
		timeout (int): timeout propagated to itself
	"""
	def __init__(self,addr,port,timeout=0):
		sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((addr, port))
		super().__init__(sock,timeout)

