from subprocess import check_output
from pathlib import Path
from os import urandom

BLOCK_SIZE=4096
def count_flines(fname):
	try:
		#try to use wc -l
		return int(check_output(["wc","-l",str(fname)]).decode().split(" ")[0])
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
RESULTS_DIR=Path("./results")
def create_results_dir():
	RESULTS_DIR.mkdir(exist_ok=True)

def choose_zip_fname(algorithm_name):
	for _ in range(10):
		ans=RESULTS_DIR.joinpath(f"{algorithm_name}_{urandom(4).hex()}.zip")
		if not ans.exists():
			return ans
	raise RuntimeError("Couldnt choose a .zip file")

