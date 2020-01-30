"""
This code is adapdated from the source code of moa, that can be found in the following address
https://github.com/Waikato/moa/blob/master/moa/src/main/java/moa/clusterers/clustream/WithKmeans.java
"""
from . import Kernel
import numpy as np
import itertools
class CluStream:
	"""
	CluStream data stream clustering algorithm implementation

	Args:
		h (int): Rang of the window
		m (int): Maximum number of micro kernels to use
		t (int): Multiplier for the kernel radius
	Attributes:
		kernels (list of clustream.Kernel) : microclusters
		time_window (int) : h
		m (int): m
		t (int): t
	"""
	def __init__(self,h=1000,m=100,t=2):
		self.kernels=[]
		self.time_window=h
		self.m=m
		self.t=t

	def offline_fit(self,datapoint,timestamp):
		if len(self.kernels)!=self.m:
			#initialize
			self.kernels.append(Kernel(datapoint,timestamp,self.t,self.m))
			return
		centers=[kernel.get_center() for kernel in self.kernels] #TODO :faster computing with caching
		#1. Determine closest kernel
		closest_kernel_index,min_distance=min(
			((i,np.linalg.norm(center-datapoint)) for i,center in enumerate(centers)),
			key=lambda t:t[1]
			)
		closest_kernel=self.kernels[closest_kernel_index]
		closet_kernel_center=centers[closest_kernel_index]
		# 2. Check whether instance fits into closest_kernel
		if closest_kernel.n==1:
			# Special case: estimate radius by determining the distance to the
			# next closest cluster
			radius=min(( #distance between the 1st closest center and the 2nd
				np.linalg.norm(center-closet_kernel_center) for center in centers if center!=closet_kernel_center
			))
		else:
			radius=closest_kernel.get_radius()
		if min_distance<radius:
			# Date fits, put into kernel and be happy
			closest_kernel.insert(datapoint,timestamp)
			print(f"{timestamp} fits")
			return
		# 3. Date does not fit, we need to free
		# some space to insert a new kernel

		threshold = timestamp - self.time_window; # Kernels before this can be forgotten
		# 3.1 Try to forget old kernels
		oldest_kernel_index=next((
			i for i,kernel in enumerate(self.kernels) if kernel.get_relevance_stamp() < threshold
		),None)
		if oldest_kernel_index!=None:
			print(f"{timestamp} forgot old kernel")
			self.kernels[oldest_kernel_index]=Kernel(datapoint,timestamp,self.t,self.m)
			return

		# 3.2 Merge closest two kernels
		print(f"{timestamp} merge closest kernel")
		closest_a,closest_b,dist=min(
			((i,j,np.linalg.norm(centers[j]-centers[i])) for i,j in itertools.combinations(range(len(centers)),2)),
			key=lambda t:t[-1]
		)

		self.kernels[closest_a].add(self.kernels[closest_b])
		self.kernels[closest_b]=Kernel(datapoint,timestamp,self.t,self.m)