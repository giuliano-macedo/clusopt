"""
core
====================================
algorithms core components
"""

from dataclasses import dataclass
from utils import Timer,ProcInfo
from network import Socket
@dataclass
class BucketEntry:
	sil:int
	k:int
	counter:int
	msock:Socket
	timer:Timer
	proc_info:ProcInfo
from .Clusterer import Clusterer
from .distance_matrix_algorithm import DistanceMatrixAlgorithm
from .Bucket import Bucket
from .streamkm import Streamkm
from .clustream import CluStream
from .cacher import Cacher