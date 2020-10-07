import signal
from contextlib import contextmanager
class TimeOutError(RuntimeError):pass
@contextmanager
def timeout(duration):
	def timeout_handler(signum, frame):
		raise TimeOutError()
	signal.signal(signal.SIGALRM, timeout_handler)
	signal.alarm(duration)
	try:
		yield None
	except TimeOutError:pass
	finally:
		signal.alarm(0)