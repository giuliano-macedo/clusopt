import time
from subprocess import check_output
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