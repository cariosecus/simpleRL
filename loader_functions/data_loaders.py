import os
import shelve
import yaml
from components.fighter import Fighter
from components.ai import BasicEnemy
from components.item_functions import get_function_by_name
from entities.entity import Entity
from render_functions import RenderOrder
import tcod as libtcod
import random
from random import randint

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

loadednpcs = loadyaml('data/npcs.yaml')
loadeditems = loadyaml('data/items.yaml')
loadedequipment = loadyaml('data/equipment.yaml')
loadedchances = loadyaml('data/spawn_chances.yaml')

def LoadEntity(listed, etype='npc',subtype=None, x=0, y=0):
	if etype == 'npc':
		loadednpcs = loadyaml('data/npcs.yaml')
		rand_item = random.choice(listed)
		result = loadednpcs[rand_item]
		fighter_component = None
		ai_component = None
		if result['fighter_component']:
			fighter_component = Fighter(result['hp'], result['defense'], result['power'], result['xp'])
		if result['ai_component']:
			ai_component = BasicEnemy()
		return Entity(x, y, result['char'], libtcod.Color(result['color_r'],result['color_g'],result['color_b']), result['name'], blocks=result['blocks'], render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
	elif etype == 'item':
		if subtype == 'item':
			rand_item = random.choice(listed)
			result = loadeditems[rand_item]
			return Entity(x, y, result['char'], libtcod.Color(result['color_r'],result['color_g'],result['color_b']), result['name'], render_order=RenderOrder.ITEM, item = get_function_by_name(result['item_use_function'], result['targeting_message'],result['item_amount'],result['damage_radius'], result['damage'], result['maximum_range']))
		elif subtype == 'equipment':
			rand_item = random.choice(listed)
			result = loadedequipment[rand_item]
			equipable_component = None
			if result['equipable_component']:
				eqslot = EquipmentSlots.MAIN_HAND
				if equipable_slots == 'EquipmentSlots.OFF_HAND':
					eqslot = EquipmentSlots.OFF_HAND
				elif equipable_slots == 'EquipmentSlots.OFF_HEAD':
					eqslot = EquipmentSlots.OFF_HEAD
				elif equipable_slots == 'EquipmentSlots.OFF_TORSO':
					eqslot = EquipmentSlots.OFF_TORSO
				elif equipable_slots == 'EquipmentSlots.OFF_LEGS':
					eqslot = EquipmentSlots.OFF_LEGS
				equipable_component = Equippable(eqslot, power_bonus=result['power_bonus'], defense_bonus=result['defense_bonus'], max_hp_bonus=result['max_hp_bonus'])

def LoadRandEntity(rarity='common',etype='npc',x=0,y=0):
	listed = []
	subtype = None
	if etype == 'npc':
		for v in loadednpcs:
			if loadednpcs[v]['rarity'] == rarity:
				listed.append(loadednpcs[v]['name'])
		if not listed:
			for v in loadednpcs:
				if loadednpcs[v]['rarity'] == 'common':
					listed.append(loadednpcs[v]['name'])
	elif etype == 'object':
		subtype = 'item'
		if rarity != 'common':
			if randint(1,80):
				subtype = 'item'
				for v in loadeditems:
					if loadeditems[v]['rarity'] == rarity:
						listed.append(loadeditems[v]['name'])
				if not listed:
					for v in loadeditems:
						if loadeditems[v]['rarity'] == 'common':
							listed.append(loadeditems[v]['name'])
			else:
				subtype = 'equipment'
				for v in loadedequipment:
					if loadedequipment[v]['rarity'] == rarity:
						listed.append(loadedequipment[v]['name'])
				if not listed:
					for v in loadedequipment:
						if loadedequipment[v]['rarity'] == 'uncommon':
							listed.append(loadedequipment[v]['name'])
	return LoadEntity(listed, etype, subtype, x, y)
