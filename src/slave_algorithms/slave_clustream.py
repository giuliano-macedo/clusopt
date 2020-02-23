from slave import Slave
class SlaveCluStream(Slave):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		raise NotImplementedError
	def run(self):
		pass