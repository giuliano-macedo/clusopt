from subprocess import check_output
from pandas import DataFrame
from collections.abc import Iterable


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