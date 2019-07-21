from threading import Lock
from .Payload import Payload
DEBUG=False
class Socket:
	def __init__(self,socket,timeout=0):
		self.read_lock=Lock()
		self.write_lock=Lock()
		self.socket=socket
		self.ip=self.socket.getpeername()[0]
		if timeout!=0:
			self.socket.settimeout(timeout)
	def recv(self,*pays_ids):
		with self.read_lock:
			ans=Payload()
			if DEBUG:print(f"[SOCK RECV {self.ip}] starting")
			ans.readFrom(self.socket)
			if (len(pays_ids)!=0) and (ans.id not in pays_ids):
				raise RuntimeError(f"Unexpected payload {ans.id}")
			if ans.id==Payload.Id.err:
				raise RuntimeError(f"Host {self.ip} sent a err payload")
			if DEBUG: print(f"[SOCK RECV {self.ip}] {ans.id.name} {repr(ans.obj)[:64]}")
			return ans
	def send(self,pay):
		with self.write_lock:
			if DEBUG: print(f"[SOCK SEND {self.ip}] {pay.id.name} {repr(pay.obj)[:64]}")
			pay.sendTo(self.socket)
			if DEBUG: print(f"[SOCK SEND {self.ip}] sent")
	def close(self):
		with self.write_lock:
			with self.read_lock:
				self.socket.close()
	def __str__(self):
		return f"Socket({self.ip})"
	def __repr__(self):
		return str(self)
	def __hash__(self):
		return hash(self.ip)