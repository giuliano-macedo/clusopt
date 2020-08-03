import time
from subprocess import check_output
from os import getpid
from psutil import Process as ProcessInfo
from dataclasses import dataclass
from pandas import DataFrame
from collections.abc import Iterable

class ProgressMeter:
	def __init__(self,total,msg):
		self.total=total
		self.msg=msg
		self.n=0
	
	def update(self,n):
		self.n+=n
		print(f"{self.msg} [{self.n*100/self.total:.2f}%]")


def save_to_csv(filename,data:Iterable):
	#saves list of dicts as csv
	DataFrame(data).to_csv(filename,index=None)

def count_flines(fname):
	try:
		#try to use wc -l
		return int(check_output(["wc","-l",fname]).decode().split(" ")[0])
	except FileNotFoundError:
		pass
	ans=0
	with open(fname) as f:
		while True:
			block=f.read(4000)
			if not block:
				break
			ans+=block.count("\n")
	return ans
class Timer:
	def __init__(self):
		"""
		store time between start() and end() in nanoseconds.
		Attrs:
			beginning (int): timestamp of start() in nanoseconds
			end (int): timestamp of end() in nanoseconds
			t (int): difference of end and beginning
		"""
		self.t=self.beginning=self.end=float("nan")
	
	def start(self):
		self.beginning=int(time.time()*1e9)
	
	def stop(self):
		self.end=int(time.time()*1e9)
		self.t=self.end-self.beginning
		return self.t
	
	def __str__(self):
		return "Timer()"
	def __repr__(self):
		return str(self)

@dataclass(frozen=True)
class ProcInfo:
	rss:int
	data_write:int
	data_read:int

def get_proc_info(pid=None)->ProcInfo:
	"""
		get ProcInfo if pid is provided, else from its own process
		
		Args:
			pid (int): process id to analyze. defaults to None.
	"""
	p=get_proc_info.p if pid==None else ProcessInfo(pid)
	meminfo=p.memory_info()
	ioinfo=p.io_counters()
	return ProcInfo(
		rss=		meminfo.rss,
		data_write=	ioinfo.write_bytes,
		data_read=	ioinfo.read_bytes
	)
get_proc_info.p=ProcessInfo(getpid())