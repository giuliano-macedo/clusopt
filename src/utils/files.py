from subprocess import check_output

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