import os
import sys
try:
	from .streamkm import Streamkm
except ImportError:
	backup=os.getcwd()
	print("compiling StreamKM++")
	os.chdir(os.path.join(os.path.dirname(__file__),"src"))
	os.system("make")
	os.chdir("..")
	try:
		from .streamkm import Streamkm
	except ImportError:
		raise ImportError("Something went wrong in the compilation")
	os.chdir(backup)
