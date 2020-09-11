from pandas import read_csv
from utils import count_flines
from itertools import chain

import numpy as np


class Stream:

	def __init__(self,fname,chunk_size,dtype=np.float64):
		"""
		class to generate a stream from a csv file, providing info about it's shape and 
		peek/pop() functions

		Args:
			fname (str): path to csv file
			chunksize (int): length of chunks to split the dataset
			dtype : datatype for each chunk

		"""
		self.fname=fname
		self.chunk_size=chunk_size
		self.lines=count_flines(self.fname)
		with open(fname) as f:self.columns=next(f).count(",")+1
		self.stream=read_csv(fname,chunksize=chunk_size,header=None,dtype=dtype)
		self.__peek=None

	def peek(self):
		assert(self.__peek==None)
		self.__peek=next(self.stream)
		return self.__peek

	def pop(self):
		return next(self.stream)

	def __iter__(self):
		extra=[] if self.__peek is None else [self.__peek]
		return chain(extra,self.stream)
			
