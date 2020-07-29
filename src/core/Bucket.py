from threading import Lock
from . import BucketEntry
from utils import save_to_csv,Timer,get_proc_info
from dataclasses import astuple
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
		def to_tuple(t,entry):
			proc_info=astuple(entry.proc_info)
			return (
				t,
				entry.sil,
				entry.k,
				entry.counter,
				entry.timer.t,
				*proc_info
			)
		print(f"saving {len(self.data)} items")
		header="batch_counter,silhouette,k,entry_counter,time,rss,data_write,data_read"
		save_to_csv(
			filename,
			"%i,%e,%i,%i,%i,%i,%i,%i",
			(to_tuple(t,entry) for t,entry in self.data.items()),
			header=header
		)