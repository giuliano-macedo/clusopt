from sklearn.cluster import MiniBatchKMeans as mkmeans
from sklearn.metrics import silhouette_score
import pandas as pd
import numpy as np
from math import sqrt,ceil

stream_speed=50
clusterer=mkmeans(n_clusters=4,batch_size=stream_speed)
url="http://localhost/gauss.csv"
labels=None
# for batch in pd.read_csv(url,chunksize=stream_speed):
# 	clusterer.partial_fit(batch)
# 	if type(labels)==type(None):
# 		labels=clusterer.labels_
# 	else:
# 		labels=np.append(labels,clusterer.labels_)
candidates=[]
X=pd.read_csv(url)
for k in range(2,ceil(sqrt(len(X)))):
	labels=mkmeans(n_clusters=k).fit(X).labels_
	s=silhouette_score(X,labels)
	print(len(labels),len(X))
	if k==4:
		breakpoint()
	candidates.append((k,s))
print(max(candidates,key=lambda t:t[1]))

	
# print(labels==mkmeans(n_clusters=4,batch_size=stream_speed).fit(pd.read_csv(url).labels_))
	