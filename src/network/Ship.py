import docker
from time import sleep
from . import ClientSocket

class Ship:
	def __init__(self,n,timeout=0,tries=15):
		self.n=n
		self.timeout=timeout
		self.tries=tries
		self.client=docker.from_env()
		self.containers=[]
		for i in range(self.n):
			self.containers.append(self.__create_container())
	def __create_container(self):
		name=f"midsc-container{len(self.containers)+1}"
		print(f"creating container {name}")
		return self.client.containers.run(
			"python:3.7.3",
			["python","container.py"],
			working_dir="/midsc/src/",
			detach=True,
			name=name,
			# cpu_period (int) – The length of a CPU period in microseconds.
			# cpu_quota (int) – Microseconds of CPU time that the container can get in a CPU period.
			# cpu_rt_period (int) – Limit CPU real-time period in microseconds.
			# cpu_rt_runtime (int) – Limit CPU real-time runtime in microseconds.
			# cpu_shares (int) – CPU shares (relative weight).
		)
	def get_node_sockets(self):
		for container in self.containers:
			container.reload() # https://github.com/docker/docker-py/issues/1375
			ip=container.attrs["NetworkSettings"]["Networks"]["bridge"]["IPAddress"]
			assert ip!="",f"Error getting container {container.name} ip"
			ans=None
			for i in range(self.tries):
				print(f"trying to connect to {ip} ({i+1})")
				try:
					ans=ClientSocket(ip,3523)
					break
				except Exception as e:
					# print(e)
					sleep(2)
					pass
			assert ans!=None,f"Error connecting to {container.name}"
			yield ans
	def save_logs(self):
		for container in self.containers:
			with open(f"{container.name}.log","wb") as f:
				f.write(container.logs())
	def close(self):
		for container in self.containers:
			try:
				container.kill()
			except Exception: #it can be already killed
				pass
			container.remove()
