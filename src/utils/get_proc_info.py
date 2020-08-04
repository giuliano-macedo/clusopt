from os import getpid
from psutil import Process as ProcessInfo
from dataclasses import dataclass

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