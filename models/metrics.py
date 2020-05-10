import numpy as np


def onsetLossFunction(detectedOnset, realOnset):
	array = [0]


	for 


	for event in range(1, len(detectedOnset)):

		# chronologically look for smallest dist to realOnset 
		# remove smaller realOnset in order to not double count onsets
		for realEvent in range(1, len(realOnset)):
			array.append(np.subtract(detectedOnset[event], realOnset[realEvent]))
			np.argmin(array)
			print(argmin)





test = [[1], [22], [25]]
test2 = [[11], [42], [65]]


onsetLossFunction(test, test2)