import time
class Timer:
	def __init__(self):
		"""
		store time between start() and end() in nanoseconds.
		Attrs:
			beginning (int): timestamp of start() in nanoseconds
			end (int): timestamp of end() in nanoseconds
			t (int): difference of end and beginning
		"""
		self.t=self.beginning=self.end=float("nan")
	
	def start(self):
		self.beginning=int(time.time()*1e9)
	
	def stop(self):
		self.end=int(time.time()*1e9)
		self.t=self.end-self.beginning
		return self.t
	
	def __str__(self):
		return "Timer()"
	def __repr__(self):
		return str(self)