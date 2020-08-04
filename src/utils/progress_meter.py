def bold_str(string):
	return f"\033[1m{string}\033[0m"

class ProgressMeter:
	def __init__(self,total,msg):
		self.total=total
		self.msg=msg
		self.n=0
	
	def update(self,n):
		self.n+=n
		print(bold_str(f"{self.msg} : [{self.n*100/self.total:.2f}%]"))