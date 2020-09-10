#!/usr/bin/env python3
import argparse
from math import ceil
from tqdm import tqdm
import pandas as pd
import json

from replica.core import Silhouette,DistanceTable
from primary.core import CluStream,Stream
from utils import get_proc_info,Timer

parser=argparse.ArgumentParser()
parser.add_argument(
	"input",
	help="path or url of the comma-separated dataset"
)
parser.add_argument(
	"-c",
	"--chunk_size",
	type=int,
	help="size of chunks that the dataset will be splitted (default 4000)",
	default=4000,
)
parser.add_argument(
	"k",
	help="number of macro-clusters",
	type=int
)
parser.add_argument(
	"-H",
	"--window-range",
	type=int,
	help="Range of the window (default 100)",
	default=100
)
parser.add_argument(
	"-m",
	"--microclusters",
	type=int,
	default=1000,
	help="Maximum number of micro clusters to use (default 1000)"
)
parser.add_argument(
	"-t",
	"--kernel-radius",
	type=int,
	default=2,
	help="Multiplier for the kernel radius (default 2)"
)
parser.add_argument(
	"--clustream-seed",
	type=int,
	help="clustream Kmeans++ offline initialization and macro-cluster generation random number generator seed (default: 42)",
	default=42
)

args=parser.parse_args()

model=CluStream(
	h=args.window_range,
	m=args.microclusters,
	t=args.kernel_radius
)

stream=Stream(args.input,args.chunk_size)

print("initing clustream")
init_points=stream.pop()
model.init_offline(init_points,args.clustream_seed)

dist_table=DistanceTable(max_size=model.m)
silhouette=Silhouette(args.k)

cluster_centers=[]
buckets=[]

chunk_timer=Timer()
overall_timer=Timer()

total=ceil(stream.lines/stream.chunk_size)-1

print("clustering")
overall_timer.start()
for i,chunk in tqdm(enumerate(stream),total=total):
	
	chunk_timer.start()
	
	model.partial_fit(chunk.values)

	macro_cluster,labels=model.get_macro_clusters(args.k,args.clustream_seed)
	dist_table.compute(model.get_partial_cluster_centers())

	sil=silhouette.get_score(dist_table.table,labels)
	del labels

	chunk_timer.stop()

	cluster_centers.append(macro_cluster.tolist())

	procinfo=get_proc_info()
	buckets.append(dict(
		i=i,
		sil=sil,
		rss=procinfo.rss,
		data_write=procinfo.data_write,
		data_read=procinfo.data_write,
		time=chunk_timer.t
	))
overall_timer.stop()

print("saving results..")
buckets_df=pd.DataFrame(buckets).to_csv("./results/buckets.csv",index=None)
pd.DataFrame([dict(
	t=overall_timer.t,
	sil=buckets[-1]["sil"]
)]).to_csv("./results/overall.csv",index=None)

with open("./results/cluster_centers.json","w") as f:
	json.dump(cluster_centers,f)