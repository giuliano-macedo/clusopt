from threading import Lock
from .Payload import Payload
import logging
import numpy as np
class Socket:
	"""
	MT Safe Socket class, implements common protocol meachanisms
	
	Args:
		socket (socket) : python's socket to wrap around
		timeout (int) : timeout for recv and send
	Attributes:
		read_lock (Lock) : lock for reading operations
		write_lock (Lock) : lock for writing operations
		ip (str) : this socket destination ip
		socket (socket): python's socket to wrap around
	"""
	def __init__(self,socket,timeout=0):
		self.read_lock=Lock()
		self.write_lock=Lock()
		self.socket=socket
		self.ip=self.socket.getpeername()[0]
		if timeout!=0:
			self.socket.settimeout(timeout)
	def recv(self,*pays_ids):
		"""
		recv any payload that have the ids defined in the arguments

		Args:
			*pay_ids (int) : ids to accept
		Returns:
			Payload object
		Raises:
			RuntimeError:if payload recieved is not expected int pays_ids or if it is midsc.network.Payload.id.err

		"""
		with self.read_lock:
			ans=Payload()
			logging.debug(f"[SOCK RECV {self.ip}] starting")
			ans.readFrom(self.socket)
			if (len(pays_ids)!=0) and (ans.id not in pays_ids):
				raise RuntimeError(f"Unexpected payload {ans.id}")
			if ans.id==Payload.Id.err:
				raise RuntimeError(f"Host {self.ip} sent a err payload")
			if ans.id==Payload.Id.datapoints:
				pay_type=f"ndarray with shape={ans.obj.shape} {ans.obj[0],ans.obj[-1]}"
				# breakpoint()
			else:
				pay_type=repr(ans.obj)[:64]
			logging.debug(f"[SOCK RECV {self.ip}] {ans.id.name} {pay_type}")
			return ans
	def send(self,pay):
		"""
		send payload to destination
		
		Args:
			pay (midsc.network.Payload) : payload to send

		"""
		with self.write_lock:
			if pay.id==Payload.Id.datapoints:
				ndarray,compressed=pay.obj
				pay_type=f"datapoints with shape={ndarray.shape} {ndarray[0],ndarray[-1]}"
			else:
				pay_type=repr(pay.obj)[:64]
			logging.debug(f"[SOCK SEND {self.ip}] {pay.id.name} {pay_type}")
			pay.sendTo(self.socket)
			logging.debug(f"[SOCK SEND {self.ip}] sent")
	def close(self):
		"""
		closes the socket
		"""
		with self.write_lock:
			with self.read_lock:
				self.socket.close()
	def __str__(self):
		return f"Socket({self.ip})"
	def __repr__(self):
		return str(self)
	def __hash__(self):
		return hash(self.ip)