import time
from subprocess import check_output
from os import getpid
from psutil import Process as ProcessInfo
from dataclasses import dataclass

def save_to_csv(filename,fmt,data,header=None):
	crlf="\r\n"
	fmt+=crlf
	with open(filename,"w") as f:
		if header is not None:
			f.write(header+crlf)
		for row in data:
			f.write(fmt%tuple(row))

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
		self.t=0
	def start(self):
		self.t=time.time()
	def stop(self):
		end=time.time()
		self.t=int((end-self.t)*1e9)
		return self.t
	def __str__(self):
		return "Timer()"
	def __repr__(self):
		return str(self)

@dataclass(frozen=True)
class SystemPerfInfo:
	rss:int
	data_write:int
	data_read:int

def get_proc_info(pid=None)->SystemPerfInfo:
	"""
		get SystemPerfInfo if pid is provided, else from its own process
		
		Args:
			pid (int): process id to analyze. defaults to None.
	"""
	p=get_proc_info.p if pid==None else ProcessInfo(pid)
	meminfo=p.memory_info()
	ioinfo=p.io_counters()
	return SystemPerfInfo(
		rss=		meminfo.rss,
		data_write=	ioinfo.write_bytes,
		data_read=	ioinfo.read_bytes
	)
get_proc_info.p=ProcessInfo(getpid())