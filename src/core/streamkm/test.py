from streamkm import Streamkm
import numpy as np
np.random.seed(1)
batch=np.random.rand(10000,2)
while True:
	model=Streamkm(length=10000,coresetsize=100)
	model.batch_online_cluster(batch)
	del model