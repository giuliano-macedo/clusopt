#!/usr/bin/env python3
import argparse
from math import ceil
from tqdm import tqdm
from pathlib import Path

from utils import CustomZipFile,create_results_dir,choose_zip_fname,get_proc_info,Timer,get_current_commit_hash
from replica.core import Silhouette,DistanceTable
from primary.core import CluStream,Stream
from psutil import virtual_memory

parser=argparse.ArgumentParser()
parser.add_argument(
	"input",
	help="path or url of the comma-separated dataset",
	type=Path
)
parser.add_argument(
	"-c",
	"--chunk-size",
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
	"-o",
	"--output",
	help=".zip output path that contains information experiment (default results/algorithm_uuid.zip)",
	default=None,
	type=Path
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
create_results_dir()

if args.output==None:
	args.output=choose_zip_fname("clustream_static")

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
		batch_counter=i,
		silhouette=sil,
		k=args.k,
		entry_counter=1,
		time_start=chunk_timer.beginning,
		time_end=chunk_timer.end,
		time=chunk_timer.t,
		rss=procinfo.rss,
		data_write=procinfo.data_write,
		data_read=procinfo.data_write
	))
overall_timer.stop()

print(f"saving results '{args.output}'")
with CustomZipFile(args.output) as zf:
	zf.add_json("overall.json",dict(time=overall_timer.t,silhouette=buckets[-1]["silhouette"]))
	zf.add_json("per_batch.json",buckets)
	zf.add_json("cluster_centers.json",cluster_centers)
	
	zf.add_json("config.json",
		dict(
			algorithm="clustream",
			batch_size=args.chunk_size,
			stream_fname=stream.fname.stem,
			total_mem=virtual_memory().total,
			commit_hash=get_current_commit_hash(),
			**{k:(v if not isinstance(v,Path) else v.name) for k,v in vars(args).items()}
		)
		,indent=4
	)
	