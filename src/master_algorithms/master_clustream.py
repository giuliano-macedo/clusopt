from master import Master
class MasterCluStream(Master):
	def __init__(self,*args,window_range,microkernels,kernel_radius,**kwargs):
		super().__init__(*args,**kwargs)
		raise NotImplementedError
	def run(self):
		pass