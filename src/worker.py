#while true; do ./slave.py [master_ip] ; sleep 1 ; done

import argparse
import os
from subprocess import Popen,CalledProcessError,PIPE,TimeoutExpired
from signal import SIGINT
from zipfile import ZipFile
import time
import shlex

class AutoKillPopen(Popen):
	def __del__(self):
		self.kill()
		super().__del__()

def runmaster(master_args):
	cmd=["./master.py",*shlex.split(master_args)]
	with open("log.txt","wb") as f:
		p=AutoKillPopen(cmd,stdout=f.fileno(),stderr=PIPE)
		print("running"," ".join(cmd))
		try:
			returncode=p.wait(6)
		except TimeoutExpired:
			p.send_signal(SIGINT)
			returncode=p.wait()
			if returncode!=0:
				raise CalledProcessError(returncode,None,stderr=p.stderr)
			return
		raise CalledProcessError(returncode,None,stderr=p.stderr)

		

parser=argparse.ArgumentParser()
parser.add_argument("master_args",type=str)
parser.add_argument("how_many_times",type=int)
parser.add_argument("output",type=str)
args=parser.parse_args()

for i in range(1,args.how_many_times+1):
	print("-"*48)
	print(f"try {i}/{args.how_many_times}")
	while True:
		try:
			runmaster(args.master_args)
			break
		except CalledProcessError as e:
			print(f"execution failed with ({e.returncode})")
			print("err:")
			print()
		time.sleep(0.5)
	print("command executed successfully")
	with ZipFile(args.output,"a") as zipf:
		zipf.write("results/buckets.csv",f"{i}/buckets.csv")
		zipf.write("results/results.json",f"{i}/results.json")
		zipf.write("results/overall.csv",f"{i}/overall.csv")
		zipf.write("log.txt",f"{i}/log.txt")
os.unlink("log.txt")
