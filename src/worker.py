#while true; do ./slave.py [master_ip] ; sleep 1 ; done

import argparse
from subprocess import Popen,CalledProcessError,PIPE,TimeoutExpired
from signal import SIGINT
from zipfile import ZipFile
import time
import json

def runmaster(dataset):
	cmd=["./master.py",dataset]
	with open("log.txt","wb") as f:
		p=Popen(cmd,stdout=f.fileno(),stderr=PIPE)
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
parser.add_argument("dataset",type=str)
parser.add_argument("batch_size",type=int)
parser.add_argument("how_many_times",type=int)
parser.add_argument("output",type=str)
args=parser.parse_args()

config=json.load(open("config.json"))
config["batch_size"]=args.batch_size
with open("config.json","w") as f:json.dump(config,f)

for i in range(1,args.how_many_times+1):
	print("-"*48)
	print(f"try {i}/{args.how_many_times}")
	while True:
		try:
			runmaster(args.dataset)
			break
		except CalledProcessError as e:
			print(f"execution failed with ({e.returncode})")
			print("err:")
			print(e.stderr.read().decode())
		time.sleep(0.5)
	print("command executed successfully")
	with ZipFile(args.output,"a") as zipf:
		zipf.write("buckets.csv",f"{i}/buckets.csv")
		zipf.write("labels.csv",f"{i}/labels.csv")
		zipf.write("overall.csv",f"{i}/overall.csv")
		zipf.write("log.txt",f"{i}/log.txt")

