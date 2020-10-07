from .cacher import Cacher
from .files import count_flines,choose_zip_fname,create_results_dir
from .get_proc_info import get_proc_info,ProcInfo
from .timer import Timer
from .progress_meter import ProgressMeter
from .force_json import force_json
from .custom_zipfile import CustomZipFile
from .timeout import timeout
from subprocess import check_output
def get_current_commit_hash():
	try:
		return check_output(["git", "describe","--always"]).strip().decode()
	except Exception:pass
	return None