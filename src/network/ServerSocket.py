import socket
from . import Socket
class ServerSocket:
	"""
	Creates a midsc.network.Socket wrapped server

	Args:
		port (int) : port to listen to
		listen_arg (int) : maximum number of concurrent listen sockets
	Attributes:
		sock (midsc.network.Socket) : socket instance
	"""
	def __init__(self,port,listen_arg=5):
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(("0.0.0.0",port))
		self.sock.listen(listen_arg)
	def accept(self):
		"""
		Accept connection and returns  socket

		Returns:
			midsc.network.Socket object
		"""
		return Socket(self.sock.accept()[0])
	def close(self):
		"""
		closes socket
		"""
		self.sock.close()