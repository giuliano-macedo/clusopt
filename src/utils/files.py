from subprocess import check_output
import os

BLOCK_SIZE=4096
def count_flines(fname):
	try:
		#try to use wc -l
		return int(check_output(["wc","-l",fname]).decode().split(" ")[0])
	except FileNotFoundError:
		pass
	ans=0
	block=bytearray(BLOCK_SIZE)
	with open(fname,"rb") as f:
		while True:
			bytes_read=f.readinto(block)
			if bytes_read<len(block):
				ans+=block[:bytes_read].count(b"\n")	
				break
			ans+=block.count(b"\n")
	return ans

def create_results_dir():
	path="./results"
	if os.path.exists(path) and not os.path.isdir(path):
		raise RuntimeError(f"{os.getcwd()}/results is not a directory")
	elif not os.path.exists(path):
		os.mkdir(path)

def choose_zip_fname(algorithm_name,basedir="./results"):
	for _ in range(10):
		ans=os.path.join(basedir,f"{algorithm_name}_{os.urandom(4).hex()}.zip")
		if not os.path.exists(ans):
			return ans
	raise RuntimeError("Couldnt choose a .zip file")

