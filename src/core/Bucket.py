from threading import Lock
from . import BucketEntry
from utils import save_to_csv,Timer
class Bucket:
	"""
	Manages each bucket entry to caclulate best silhouette for each batch index

	Args:
		batch_size (int): size of each chunk of the dataset
	"""
	def __init__(self,max_size):
		self.lock=Lock()
		self.data={} #t -> Bucket.Entry
		self.max_size=max_size

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
			isfull=entry.counter==self.max_size
			if isfull:
				entry.timer.stop()
			if entry.counter>self.max_size:
				raise RuntimeError("Unexpected error: bucket already full")
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