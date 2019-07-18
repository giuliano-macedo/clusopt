from enum import IntEnum
import numpy as np
import struct
class Payload:
	class Id(IntEnum):
		ok=					0
		#null
		err=				1
		#null
		end=				2
		#null
		datapoints=			3
		#uint32 m,uint32 n,float32 matrix(m,n)
		labels=				4
		#uint32 m,uint32 vector(m)
		k_coeficient=		5
		#uint32 kc
		k_coeficient_inc=	6
		#uint32 kci
		silhouette=			7
		#uint32 batch_counter uint32 k float32 sil

	def __init__(self,payloadid=Id.ok,obj=None):
		self.id=payloadid
		self.obj=obj
	def readFrom(self,sock):
		sockid,=struct.unpack("B",sock.recv(1))
		try:
			sockid=Payload.Id(sockid)
		except ValueError:
			raise ValueError("Invalid socket id")
		self.id=sockid
		if self.id==Payload.Id.datapoints:
			#read two uint32
			m,n=struct.unpack("II",sock.recv(8))
			#read float32 matrix
			data=bytearray(sock.recv(m*n*4))
			self.obj=np.frombuffer(data,dtype=np.float32).reshape((m, n))
		elif self.id==Payload.Id.labels:
			#read uint32
			m,=struct.unpack("I",sock.recv(4))
			#read float32 vector
			data=bytearray(sock.recv(m*4))
			self.obj=np.frombuffer(data,dtype=np.float32).reshape((m))
		elif self.id==Payload.Id.silhouette:
			#read uint32 and uint32 and float32
			self.obj=struct.unpack("IIf",sock.recv(12))
		elif self.id in {Payload.Id.k_coeficient,Payload.Id.k_coeficient_inc}:
			#read uint32
			self.obj,=struct.unpack("I",sock.recv(4))
	def sendTo(self,sock):
		buff=bytearray()
		buff+=(struct.pack("B",self.id.value))
		if self.id==Payload.Id.datapoints:
			buff+=(struct.pack("II",*self.obj.shape))
			buff+=(self.obj.tobytes())
		elif self.id==Payload.Id.labels:
			buff+=(struct.pack("I",self.obj.shape))
			buff+=(self.obj.tobytes())
		elif self.id==Payload.Id.silhouette:
			buff+=(struct.pack("IIf",*self.obj))
		elif self.id in {Payload.Id.k_coeficient,Payload.Id.k_coeficient_inc}:
			buff+=(struct.pack("I",self.obj))
		sock.sendall(buff)