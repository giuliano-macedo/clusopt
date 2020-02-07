import os
import sys
try:
	from .clustream import CluStream
except ImportError:
	backup=os.getcwd()
	print("compiling CluStream")
	os.chdir(os.path.join(os.path.dirname(__file__),"src"))
	os.system("make")
	os.chdir("..")
	try:
		from .clustream import CluStream
	except ImportError:
		raise ImportError("Something went wrong in the compilation")
	os.chdir(backup)
