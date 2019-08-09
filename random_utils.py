from random import randint
from loader_functions.data_loaders import loadedchances


def random_choice_from_dict(choice_dict):
	currentprob = randint(1, 100)
	result = loadedchances[choice_dict]
	for i in result:
		if currentprob <= i:
			return result[i]
