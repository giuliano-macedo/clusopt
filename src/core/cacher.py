import os
import shutil
import tempfile
from queue import Queue
from threading import Lock,Thread

class Filler(Thread):
	#will try to empty diskcache and put into memcache endlessly
	def __init__(self,memcache,diskcache,delete_after):
		super().__init__(name="Filler")
		self.memcache=memcache
		self.diskcache=diskcache
		self.delete_after=delete_after
		self.stop=False
	def run(self):
		while not self.stop:
			data=self.diskcache.get(self.delete_after)
			self.memcache.put(data)

class Cacher:

	"""
		MT-Safe Cacher that will store data in disk if max_mem_length is reached
	"""
	def __init__(self,max_mem_length:int,prefix="DirectoryCacheQueue-",delete_after=False):
		self.max_mem_length=max_mem_length
		self.memcache=Queue(max_mem_length)
		self.diskcache=DirectoryCacherQueue(prefix=prefix)
		self.filler=Filler(self.memcache,self.diskcache,delete_after)
		self.filler.start()

	def put(self,data:bytes):
		if self.memcache.full():
			self.diskcache.put(data)
		else:
			self.memcache.put(data)

	def get(self,delete_after=False)->bytes:
		return self.memcache.get()

	def __len__(self)->int:
		return len(self.diskcache)+self.memcache.qsize()

	def close(self):
		#'kills' filler
		self.filler.stop=True
		self.diskcache.put(b"0") #dummy data
		self.filler.join()


class DirectoryCacherQueue:
	def __init__(self,prefix):
		self.directory=tempfile.mkdtemp(prefix=prefix)
		self.elems=Queue()
		self.nofiles=0
		self.__write_lock=Lock()

	def put(self,data:bytes):
		with self.__write_lock:
			new_elem=os.path.join(self.directory,f"{self.nofiles:010}")
			self.nofiles+=1
			with open(new_elem,"wb") as f:
				f.write(data)
			self.elems.put(new_elem)

	def get(self,delete_after)->bytes:
		#get if available, else wait
		elem=self.elems.get()
		with open(elem,"rb") as f:
			ans:bytes=f.read()
		if delete_after:
			os.remove(elem)
		return ans
	
	def get_disk_usage(self):
		#very slow
		ans=0
		for f in os.listdir(self.directory):
			with open(os.path.join(self.directory,f),"rb") as f:
				ans+=len(f.read()) 
		return ans

	def __len__(self)->int:
		return self.elems.qsize()

	def __del__(self):
		shutil.rmtree(self.directory)

