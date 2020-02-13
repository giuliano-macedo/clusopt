from master import Master
class MasterStreamkm(Master):
	def __init__(self,*args,coreset_size):
		super().__init__(*args)
		raise NotImplemented
	def run(self):
		pass