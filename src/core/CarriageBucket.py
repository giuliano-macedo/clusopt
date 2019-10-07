from math import ceil,sqrt
from threading import Lock
from . import BucketEntry
from utils import save_to_csv,Timer
class CarriageBucket:
	def __init__(self,batch_size):
		self.lock=Lock()
		self.batch_size=batch_size
		self.data={} #t -> Bucket.Entry
	def add(self,t,k,sil,msock):
		with self.lock:
			entry=self.data.get(t)
			if entry==None:
				entry=BucketEntry(
					sil=sil,
					k=k,
					counter=1,
					msock=msock,
					timer=Timer()
				)
				self.data[t]=entry
				entry.timer.start()
			else:	
				entry.counter+=1
				if sil>entry.sil:
					#update entry
					entry.sil=sil
					entry.k=k
					entry.msock=msock
			n=(t+1)*self.batch_size
			isfull=(entry.counter==(ceil(sqrt(n))-1))
			if isfull:
				entry.timer.stop()
			return isfull
	def get(self,t):
		with self.lock:
			return self.data.get(t)
	def save_logs(self,filename):
		print(f"saving {len(self.data)} items")
		save_to_csv(
			filename,
			"%i,%e,%i,%i,%i",
			((t,entry.sil,entry.k,entry.counter,entry.timer.t) for t,entry in self.data.items()),
			header="batch_counter,silhouette,k,entry_counter,time"
		)