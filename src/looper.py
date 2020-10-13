#!/usr/bin/env python
import argparse
from subprocess import Popen,CalledProcessError,PIPE
from pathlib import Path
from utils import Timer
from tempfile import mkdtemp
from zipfile import ZipFile
from time import sleep
import shlex
import shutil

class AutoKillPopen(Popen):
	def __del__(self):
		self.kill()
		super().__del__()

def runprimary(cmd,log_fname):
	with open(log_fname,"wb") as f:
		p=AutoKillPopen(cmd,stdout=f.fileno(),stderr=PIPE)
		print(f"running '{' '.join(cmd)}'")
		returncode=p.wait()
		if returncode!=0:
			raise CalledProcessError(returncode,None,stderr=p.stderr)
		return

def main(tmp_path):
	parser=argparse.ArgumentParser(description="Program to repeat some shell command until it exits successfully, and injects an incremental seed in the arg '--seed' and '--output' based on its prefix")
	parser.add_argument("cmd",type=str)
	parser.add_argument("how_many_times",type=int)
	parser.add_argument("output_prefix",type=str)
	parser.add_argument("-i","--initial-seed",type=int,default=42)
	parser.add_argument("-r","--results-dir",type=Path,default=Path("./results"))
	args=parser.parse_args()

	cmd=shlex.split(args.cmd)

	args.results_dir.mkdir(exist_ok=True)
	final_output_path=args.results_dir/f"{args.output_prefix}.zip"
	log_path=tmp_path/"log.txt"

	print(f"log path : {log_path}")

	for i in range(1,args.how_many_times+1):
		
		output_path=tmp_path/f"{args.output_prefix}-{i}.zip"
		
		cmd_injected=list(cmd)

		first_cmd=cmd_injected.pop(0)

		cmd_injected=[first_cmd]+[
			"--seed",str(args.initial_seed+i-1),
			"--output",str(output_path)
		]+cmd_injected
		while True:
			try:
				print("-"*48)
				print(f"attempt {i}/{args.how_many_times}")
				timer=Timer()
				timer.start()
				runprimary(cmd_injected,log_path)
				timer.stop()
				if not output_path.exists():
					raise FileNotFoundError()
				break
			except CalledProcessError as e:
				print(f"execution failed with ({e.returncode})")
				print("err:")
				print(e.stderr.read().decode("utf-8","ignore"))
			except FileNotFoundError:
				print(f"program didn't produce the executed ouput '{output_path}'")
			sleep(0.5)
		
		#add log to curr zip
		with ZipFile(output_path,"a") as zipf:
			zipf.write(str(log_path),"log.txt")
		
		#group zip in final_output_path
		with ZipFile(final_output_path,"a") as zipf:
			zipf.write(str(output_path),f"{args.output_prefix}-{i}.zip")

		print(f"command executed successfully, finished in {timer.t/1e9:.4f} seconds")

if __name__=="__main__":
	TEMP_DIR=Path(mkdtemp(prefix="looper-"))
	try:
		main(TEMP_DIR)
	finally:
		shutil.rmtree(str(TEMP_DIR))