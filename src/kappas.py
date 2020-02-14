import numpy as np

def get_kappas(no_slaves,l):
	"""
	Returns kappas set with gauss's trick for each slave

	Args:
		no_slaves (int): number of slaves
		l (int): lower threshold of the number of columns of the kappa matrix
	Returns:
		list
	"""
	#l must be even and divisble by l
	#adds with the complementary mod of no_slaves, so that l is divisible by no_slaves
	l+=no_slaves-(l%no_slaves)
	#gauss's trick only works with even numbers, so
	if (l//no_slaves)%2==1:
		l+=no_slaves
	#range of k's must be from 2 to l
	unordered_kappas=list(range(2,l+2))
	return np.array(rearange(unordered_kappas)).reshape((no_slaves,(l//no_slaves))).tolist()
def rearange(L): # reorders list of k's to do the gauss's trick
	
	n=len(L)
	first_half=L[0:n//2] #divides list from start to half
	second_half=L[:n//2 -1:-1] #divides list from half to end and inverts it
	
	ans=[]
	while first_half or second_half: #intercalate the lists
		if first_half:
			ans.append(first_half.pop(0))
		if second_half:
			ans.append(second_half.pop(0))
	return ans
def old_get_kappas(no_slaves,l):
	"""
	deprecated
	"""
	kappa=lambda i:[k for k in range(2+i,l+1,no_slaves)]
	return np.array([kappa(i) for i in range(no_slaves)]).tolist()
