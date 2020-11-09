#!/usr/bin/env python3
from math import ceil
from tqdm import tqdm
from utils import CustomZipFile,get_proc_info,Timer,get_current_commit_hash
from clusopt_core.metrics import Silhouette,DistanceMatrix
from psutil import virtual_memory
from static.args import parse_args
from utils import force_json

args=parse_args()

model=args.algorithm
stream=args.input

# computing silhouette score is time negligible, so for results compatibility reasons 
# compute here
dist_table=DistanceMatrix(max_size=model.batch_size)
silhouette=Silhouette(args.k)

cluster_centers=[]
buckets=[]

chunk_timer=Timer()
overall_timer=Timer()

total=ceil(stream.lines/stream.chunk_size)

print("clustering ...")
overall_timer.start()
for i,chunk in tqdm(enumerate(stream),total=total):
	
	chunk_timer.start()

	model.partial_fit(chunk.values)
	
	macro_cluster,labels=model.get_final_cluster_centers()
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
			algorithm=model.NAME,
			batch_size=model.batch_size,
			stream_fname=stream.fname.stem,
			total_mem=virtual_memory().total,
			commit_hash=get_current_commit_hash(),
			**force_json(args)
		)
		,indent=4
	)
	