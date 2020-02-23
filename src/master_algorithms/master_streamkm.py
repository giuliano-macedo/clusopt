from master import Master
class MasterStreamkm(Master):
	def __init__(self,*args,coreset_size,**kwargs):
		super().__init__(*args,**kwargs)
		raise NotImplementedError
	def run(self):
		pass