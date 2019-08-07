from random import randint
from loader_functions.data_loaders import loadedchances

def from_dungeon_level(table, dungeon_level):
	for (value, level) in reversed(table):
		if dungeon_level >= level:
			return value
	return 0

def random_choice_index(chances):
	random_chance=randint(1, sum(chances))

	running_sum=0
	choice=0
	for w in chances:
		running_sum += w

		if random_chance <= running_sum:
			return choice
		choice += 1

def random_choice_from_dict(choice_dict):
	currentprob=randint(1,100)
	result=loadedchances[choice_dict]
	for i in result:
		if currentprob <= i:
			return result[i]
