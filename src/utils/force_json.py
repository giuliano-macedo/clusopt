import json
def is_jsonable(x):
	try:
		json.dumps(x)
		return True
	except:
		return False
def force_json(obj):
	"""
	Makes a shallow copy of obj if an attribute in obj is json serializable:

	Args:
		obj (object)
	Returns:
		dict
	"""
	return {k:v for k,v in vars(obj).items() if is_jsonable(v)}