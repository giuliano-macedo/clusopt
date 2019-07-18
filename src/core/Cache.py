import numpy as np
from threading import Lock
# # https://stackoverflow.com/a/16867494/5133524
# class Cache:
#	filename="cache.dat"
# 	def __init__(self,dtype):
# 		self.dtype=dtype
# 		self.lock=Lock()
# 		self.ndarray=None
# 	def add(self,ndarray):
# 		with self.lock:
# 			if type(self.ndarray)==type(None):
# 				self.ndarray=np.memmap(self.filename, dtype=self.dtype, mode='w+', shape=ndarray.shape)
# 				self.ndarray[:]=ndarray[:]
# 				return
# 			tmp= np.memmap(self.filename+".tmp", dtype=self.dtype, mode='w+', shape=ndarray.shape)
# 			tmp[:]=ndarray[:]

# 			newshape=(
# 				self.ndarray.shape[0]+ndarray.shape[0],
# 				self.ndarray.shape[1]
# 			)
# 			self.ndarray = np.memmap(self.filename, dtype=self.dtype, mode='r+', shape=newshape, order='C')
# 			self.ndarray[self.ndarray.shape[0]:,:] = tmp
class Cache:
	def __init__(self,dtype):
		self.ndarray=np.empty(0)
		self.lock=Lock()
		self.size=0
	def is_empty(self):
		with self.lock:
			return not self.ndarray.any()
	def add(self,ndarray):
		with self.lock:
			self.size+=len(ndarray)
			if not self.ndarray.any():
				self.ndarray=ndarray.copy()
				return
			n=self.ndarray.shape[0]
			newshape=(
				n+ndarray.shape[0],
				self.ndarray.shape[1]
			)
			self.ndarray.resize(newshape)
			self.ndarray[n:]=ndarray
