from enum import IntEnum
import zlib
import numpy as np
import struct
def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data
class Payload:
	"""
	implements midsc's protocol usings it's ids

	Args:
		id (midsc.network.Payload.Id) : instance id
		obj (object) : instance data
	Attributes:
		id (midsc.network.Payload.Id) : instance id
		obj (object) : instance data
	Notes:
		when creating this object you must use the following definitions
			+------------------+-----------+---------------------------------------------------------------------------------------------------------------+
			| id               | obj type  | notes                                                                                                         |
			+------------------+-----------+---------------------------------------------------------------------------------------------------------------+
			| ok               | None      | -                                                                                                             |
			+------------------+-----------+---------------------------------------------------------------------------------------------------------------+
			| err              | None      | -                                                                                                             |
			+------------------+-----------+---------------------------------------------------------------------------------------------------------------+
			| end              | None      | -                                                                                                             |
			+------------------+-----------+---------------------------------------------------------------------------------------------------------------+
			| datapoints       | tuple     | the tuple must be of size 4 and have the following content (np.uint32,np.uint32 n,np.uint32,bytes)            |
			+------------------+-----------+---------------------------------------------------------------------------------------------------------------+
			| labels_req       | np.uint32 | represents k                                                                                                  |
			+------------------+-----------+---------------------------------------------------------------------------------------------------------------+
			| labels           | tuple     | tuple must be of size 2 and have the following contents (np.uint32,np.ndarray(shape=(m,n),dtype=np.float32) ) |
			+------------------+-----------+---------------------------------------------------------------------------------------------------------------+
			| k_coeficient     | np.uint32 | represents kc                                                                                                 |
			+------------------+-----------+---------------------------------------------------------------------------------------------------------------+
			| k_coeficient_inc | np.uint32 | kci                                                                                                           |
			+------------------+-----------+---------------------------------------------------------------------------------------------------------------+
			| silhouette       | tuple     | tuple must be of size 3 containing 3 np.uint32                                                                |
			+------------------+-----------+---------------------------------------------------------------------------------------------------------------+
	"""
	class Id(IntEnum):
		"""
		Payload's id enum
		"""
		ok=					0
		#null
		err=				1
		#null
		end=				2
		#null
		datapoints=			3
		#uint32 m,uint32 n,float32 matrix(m,n)
		labels_req=			4
		#uint32 k
		labels=				5
		#uint32 m,uint32 vector(m)
		k_coeficient=		6
		#uint32 kc
		k_coeficient_inc=	7
		#uint32 kci
		silhouette=			8
		#uint32 batch_counter uint32 k float32 sil


	def __init__(self,payloadid=Id.ok,obj=None):
		self.id=payloadid
		self.obj=obj
	def readFrom(self,sock):
		"""
		read itself from socket
		
		Args:
			sock (midsc.network.Socket): socket to read from
		"""
		sockid,=struct.unpack("B",sock.recv(1))
		try:
			sockid=Payload.Id(sockid)
		except ValueError:
			raise ValueError("Invalid socket id")
		self.id=sockid
		if self.id==Payload.Id.datapoints:
			#read three uint32
			m,n,len_bytes=struct.unpack("III",sock.recv(12))
			#read float32 matrix
			data=zlib.decompress(bytearray(recvall(sock,len_bytes)))
			self.obj=np.frombuffer(data,dtype=np.float32).reshape((m, n))
		elif self.id==Payload.Id.labels:
			#read uint32
			m,=struct.unpack("I",sock.recv(4))
			#read uint8 vector
			data=bytearray(recvall(sock,m))
			self.obj=np.frombuffer(data,dtype=np.uint8).reshape((m))
		elif self.id==Payload.Id.silhouette:
			#read uint32 and uint32 and float32
			self.obj=struct.unpack("IIf",sock.recv(12))
		elif self.id in {Payload.Id.k_coeficient,Payload.Id.k_coeficient_inc}:
			#read uint32
			self.obj,=struct.unpack("I",sock.recv(4))
		elif self.id==Payload.Id.labels_req:
			self.obj=struct.unpack("II",sock.recv(8))
	def sendTo(self,sock):
		"""
		send itself to socket
		
		Args:
			sock (midsc.network.Socket): socket to send to
		"""
		buff=bytearray()
		buff+=(struct.pack("B",self.id.value))
		if self.id==Payload.Id.datapoints:
			ndarray,compressed=self.obj
			buff+=(struct.pack("III",*ndarray.shape,len(compressed)))
			buff+=(compressed)
		elif self.id==Payload.Id.labels:
			buff+=(struct.pack("I",*self.obj.shape))
			buff+=(self.obj.tobytes())
		elif self.id==Payload.Id.silhouette:
			buff+=(struct.pack("IIf",*self.obj))
		elif self.id in {Payload.Id.k_coeficient,Payload.Id.k_coeficient_inc}:
			buff+=(struct.pack("I",self.obj))
		elif self.id ==Payload.Id.labels_req:
			buff+=(struct.pack("II",*self.obj))
		sock.sendall(buff)