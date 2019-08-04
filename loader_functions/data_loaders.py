import os
import shelve
import yaml

def save_game(player, entities, game_map, message_log, game_state):
	with shelve.open('savegame.dat', 'n') as data_file:
		data_file['player_index'] = entities.index(player)
		data_file['entities'] = entities
		data_file['game_map'] = game_map
		data_file['message_log'] = message_log
		data_file['game_state'] = game_state

def load_game():
	if not os.path.isfile('saved_games/savegame.dat'):
		raise FileNotFoundError

	with shelve.open('saved_games/savegame.dat', 'r') as data_file:
		player_index = data_file['player_index']
		entities = data_file['entities']
		game_map = data_file['game_map']
		message_log = data_file['message_log']
		game_state = data_file['game_state']

	player = entities[player_index]

	return player, entities, game_map, message_log, game_state

def loadyaml(filepath):
	with open(filepath, "r") as file_descriptor:
		loaded = yaml.safe_load(file_descriptor)
	return loaded

def dumpyaml(file = None, data = None):
	if data:
		with open(file, "w") as file_descriptor:
			yaml.dump(file, file_descriptor)
