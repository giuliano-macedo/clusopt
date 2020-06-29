import os
import shutil
import tempfile
from collections import deque
from enum import IntEnum

class Op(IntEnum):
	disk=0
	mem=1

class Cacher:
	"""
		Cacher that will store data in disk if max_mem_length is reached
	"""
	def __init__(self,max_mem_length:int,prefix="DirectoryCacheQueue-"):
		self.max_mem_length=max_mem_length
		self.memcache=deque()
		self.diskcache=DirectoryCacherQueue(prefix=prefix)
		self.op_list=[]

	def push(self,data:bytes):
		if len(self.memcache)>self.max_mem_length:
			self.diskcache.push(data)
			self.op_list.append(Op.disk)
		else:
			self.memcache.append(data)
			self.op_list.append(Op.mem)

	def pop(self,delete_after=False)->bytes:
		assert(self.op_list)
		if self.op_list.pop(0)==Op.disk:
			return self.diskcache.pop(delete_after)
		else:
			return self.memcache.popleft()

	def __len__(self)->int:
		return len(self.op_list)


class DirectoryCacherQueue:
	def __init__(self,prefix):
		self.directory=tempfile.mkdtemp(prefix=prefix)
		self.elems=[]

	def push(self,data:bytes):
		new_elem=os.path.join(self.directory,f"{len(self.elems):010}")
		self.elems.append(new_elem)
		with open(new_elem,"wb") as f:
			f.write(data)

	def pop(self,delete_after)->bytes:
		assert(self.elems)
		elem=self.elems.pop(0)
		with open(elem,"rb") as f:
			ans:bytes=f.read()
		if delete_after:
			os.remove(elem)
		return ans
	
	def __len__(self)->int:
		return len(self.elems)

	def __del__(self):
		shutil.rmtree(self.directory)

