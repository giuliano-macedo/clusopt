from threading import Lock
from .Payload import Payload
class Socket:
	def __init__(self,socket,timeout=0):
		self.read_lock=Lock()
		self.write_lock=Lock()
		self.socket=socket
		self.ip=self.socket.getpeername()[0]
		if timeout!=0:
			self.socket.settimeout(timeout)
	def recv(self):
		with self.read_lock:
			ans=Payload()
			# print(f"[SOCK RECV {self.ip}] starting")
			ans.readFrom(self.socket)
			# print(f"[SOCK RECV {self.ip}] {ans.id.name} {repr(ans.obj)[:64]}")
			return ans
	def send(self,pay):
		with self.write_lock:
			# print(f"[SOCK SEND {self.ip}] {pay.id.name} {repr(pay.obj)[:64]}")
			pay.sendTo(self.socket)
			# print(f"[SOCK SEND {self.ip}] sent")
	def close(self):
		with self.write_lock:
			with self.read_lock:
				self.socket.close()