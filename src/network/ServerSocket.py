import socket
from . import Socket
class ServerSocket:
	def __init__(self,port,listen_arg=5):
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(("0.0.0.0",port))
		self.sock.listen(listen_arg)
	def accept(self):
		return Socket(self.sock.accept()[0])
	def close(self):
		self.sock.close()