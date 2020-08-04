class Slave:
	"""
	Args:
		batch_size (int) : size of the chunks that the dataset will be splitted
		kappa (ndarray) : K's to test
		seed (int): seed to use
		repetitions (int): number of repetitions
		ghost (int or None) : if not None, enable ghost mode when batch index equals itself
		disk_cache (int or None) : enable disk cache with max memory size equal to itself
		distance_matrix_method (str) : distance matrix algorithm to use
		batch_size (int): length of each batch
	Attributes:
		
	"""
	def __init__(self,server,kappa,seed,repetitions,ghost,disk_cache,distance_matrix_method,batch_size):
		self.server=server
		self.kappa=kappa
		self.seed=seed
		self.repetitions=repetitions
		self.ghost=ghost
		self.disk_cache=disk_cache
		self.distance_matrix_method=distance_matrix_method
		self.batch_size=batch_size

	def run(self,server):
		"""
		main method, run slave's node algorithm
		"""
		pass
