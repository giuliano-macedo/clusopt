import socket
from . import Socket
class ClientSocket(Socket):
	def __init__(self,addr,port,timeout=0):
		sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((addr, port))
		super().__init__(sock,timeout)

