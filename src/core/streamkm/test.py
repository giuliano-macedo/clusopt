from streamkm import Streamkm
import numpy as np
np.random.seed(1)
model=Streamkm(length=10000,coresetsize=2)
while True:
	batch=np.random.rand(10000,2)
	model.batch_online_cluster(batch)
	# del model