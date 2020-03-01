from enum import IntEnum
import zlib
import numpy as np
import struct
import json
def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data
def read_compressed_float32_matrix(sock):
	#read three uint32
	m,n,len_bytes=struct.unpack("III",sock.recv(12))
	#read compressed data
	data=zlib.decompress(bytearray(recvall(sock,len_bytes)))
	#construct array from dimensions
	return np.frombuffer(data,dtype=np.float32).reshape((m, n))

def write_compressed_float32_matrix(buff,obj):
	ndarray,compressed=obj
	buff+=(struct.pack("III",*ndarray.shape,len(compressed)))
	buff+=(compressed)

def read_compressed_float64_matrix(sock):
	#read three uint32
	m,n,len_bytes=struct.unpack("III",sock.recv(12))
	#read compressed data
	data=zlib.decompress(bytearray(recvall(sock,len_bytes)))
	#construct array from dimensions
	return np.frombuffer(data,dtype=np.float64).reshape((m, n))

def write_compressed_float64_matrix(buff,obj):
	ndarray,compressed=obj
	buff+=(struct.pack("III",*ndarray.shape,len(compressed)))
	buff+=(compressed)

def read_float32_matrix(sock):
	#read two uint32
	m,n=struct.unpack("II",sock.recv(8))
	# read and construct array from dimensions
	return np.frombuffer(recvall(sock,m*n*4),dtype=np.float32).reshape((m, n))

def write_float32_matrix(buff,obj):
	ndarray=obj
	buff+=(struct.pack("II",*ndarray.shape))
	buff+=(ndarray.tobytes())

def read_float64_matrix(sock):
	#read two uint32
	m,n=struct.unpack("II",sock.recv(8))
	# read and construct array from dimensions
	return np.frombuffer(recvall(sock,m*n*8),dtype=np.float64).reshape((m, n))

def write_float64_matrix(buff,obj):
	ndarray=obj
	buff+=(struct.pack("II",*ndarray.shape))
	buff+=(ndarray.tobytes())

def read_uint8_vector(sock):
	#read uint32
	m,=struct.unpack("I",sock.recv(4))
	#read uint8 vector
	data=bytearray(recvall(sock,m))
	return np.frombuffer(data,dtype=np.uint8).reshape((m))

def write_uint8_vector(buff,obj):
	ndarray=obj
	buff+=(struct.pack("I",*ndarray.shape))
	buff+=(ndarray.tobytes())

def read_results_req(sock):
	return struct.unpack("II",sock.recv(8))

def write_results_req(buff,obj):
	buff+=(struct.pack("II",*obj))

def read_silhouette(sock):
	return struct.unpack("IIf",sock.recv(12))

def write_silhouette(buff,obj):
	buff+=(struct.pack("IIf",*obj))

def read_json(sock):
	#read uint32
	n,=struct.unpack("I",sock.recv(4))
	#read string and parse json
	return json.loads(sock.recv(n))

def write_json(buff,obj):
	s=bytes(json.dumps(obj),"ascii")
	buff+= (struct.pack("I",len(s))+s)

class PAYID(IntEnum):
	"""
	Payload's id enum
	"""
	ok=							0
	err=						1
	end=						2
	compressed_float32_matrix=	3
	compressed_float64_matrix=	4
	float32_matrix=				5
	float64_matrix=				6
	uint8_vector=				8
	results_req=				9
	silhouette=					10
	json=						11
class Payload:
	"""
	implements midsc's protocol usings it's ids

	Args:
		id (midsc.network.PAYID) : instance id
		obj (object) : instance data
	Attributes:
		id (midsc.network.PAYID) : instance id
		obj (object) : instance data
	Notes:
		when creating this object you must use the following definitions
			+---------------------------+----------+-------------------------------------------------------------+
			| id                        | obj type | serialized obj                                              |
			+---------------------------+----------+-------------------------------------------------------------+
			| ok                        | None     |                                                             |
			+---------------------------+----------+-------------------------------------------------------------+
			| err                       | None     |                                                             |
			+---------------------------+----------+-------------------------------------------------------------+
			| end                       | None     |                                                             |
			+---------------------------+----------+-------------------------------------------------------------+
			| compressed_float32_matrix | tuple    | (np.uint32 m,np.uint32 n,np.uint32 length , bytes(length) ) |
			+---------------------------+----------+-------------------------------------------------------------+
			| compressed_float64_matrix | tuple    | same as above                                               |
			+---------------------------+----------+-------------------------------------------------------------+
			| float32_matrix            | tuple    | (np.uint32 m,np.uint32 n,bytes(m*n*4) )                     |
			+---------------------------+----------+-------------------------------------------------------------+
			| float64_matrix            | tuple    | (np.uint32 m,np.uint32 n,bytes(m*n*8) )                     |
			+---------------------------+----------+-------------------------------------------------------------+
			| uint8_vector              | tuple    | (np.uint32 n, bytes(n*4))                                   |
			+---------------------------+----------+-------------------------------------------------------------+
			| results_req                | tuple    | (np.uint32 batch_counter,np.uint32 k)                       |
			+---------------------------+----------+-------------------------------------------------------------+
			| silhouette                | tuple    | (np.uint32 batch_counter, np.uint32 k, np.float sil)        |
			+---------------------------+----------+-------------------------------------------------------------+
			| json                      | str      | (np.uint32 n, str(n))                                       |
			+---------------------------+----------+-------------------------------------------------------------+
	"""
	__hooks_read={
		PAYID.compressed_float32_matrix:read_compressed_float32_matrix,
		PAYID.compressed_float64_matrix:read_compressed_float64_matrix,
		PAYID.float32_matrix:read_float32_matrix,
		PAYID.float64_matrix:read_float64_matrix,
		PAYID.uint8_vector:read_uint8_vector,
		PAYID.results_req:read_results_req,
		PAYID.silhouette:read_silhouette,
		PAYID.json:read_json
	}
	__hooks_write={
		PAYID.compressed_float32_matrix:write_compressed_float32_matrix,
		PAYID.compressed_float64_matrix:write_compressed_float64_matrix,
		PAYID.float32_matrix:write_float32_matrix,
		PAYID.float64_matrix:write_float64_matrix,
		PAYID.uint8_vector:write_uint8_vector,
		PAYID.results_req:write_results_req,
		PAYID.silhouette:write_silhouette,
		PAYID.json:write_json
	}
	def __init__(self,payloadid=PAYID.ok,obj=None):
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
			sockid=PAYID(sockid)
		except ValueError:
			raise ValueError("Invalid socket id")
		self.id=sockid
		f=self.__hooks_read.get(self.id,None)
		if f!=None:
			self.obj=f(sock)
	def sendTo(self,sock):
		"""
		send itself to socket
		
		Args:
			sock (midsc.network.Socket): socket to send to
		"""
		buff=bytearray()
		buff+=(struct.pack("B",self.id.value))
		f=self.__hooks_write.get(self.id,None)
		if f!=None:
			f(buff,self.obj)
		sock.sendall(buff)