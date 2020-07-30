from threading import Lock
from . import BucketEntry
from utils import save_to_csv,Timer,get_proc_info
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
			if entry==None:#insert new entry
				entry=BucketEntry(
					sil=sil,
					k=k,
					counter=1,
					msock=msock,
					timer=Timer(),
					proc_info=get_proc_info()
				)
				self.data[t]=entry
				entry.timer.start()
			else:#update entry
				entry.counter+=1
				if sil>entry.sil:
					entry.sil=sil
					entry.k=k
					entry.msock=msock
				elif sil==entry.sil and k<=entry.k: #collision
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
		data=(
			dict(
				batch_counter=t,
				silhouette=entry.sil,
				k=entry.k,
				entry_counter=entry.counter,
				time=entry.timer.t,
				rss=entry.proc_info.rss,
				data_write=entry.proc_info.data_write,
				data_read=entry.proc_info.data_write
			)
			for t,entry in self.data.items()
		)
		save_to_csv(filename,data)