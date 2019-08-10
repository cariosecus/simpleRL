import os
import shelve
import yaml
from components.fighter import Fighter
from components.ai import BasicEnemy
from components.item_functions import get_function_by_name
from components.equipable import Equipable
from equipment_slots import EquipmentSlots
from entity import Entity
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


def dumpyaml(file=None, data=None):
	if data:
		with open(file, "w") as file_descriptor:
			yaml.dump(file, file_descriptor)


loadedmobs = loadyaml('data/mobs.yaml')
loadeditems = loadyaml('data/items.yaml')
loadedequipment = loadyaml('data/equipment.yaml')
loadedchances = loadyaml('data/spawn_chances.yaml')


def load_entity(listed, subtype, x=0, y=0, dungeon_level=1):
	result = random.choice(listed)
	modifier = max((dungeon_level/3), 1)
	if subtype == 'mobs':
		fighter_component = None
		ai_component = None
		if result['fighter_component']:
			fighter_component = Fighter(result['hp']*modifier, result['defense']*modifier, result['power']*modifier, result['xp'])
		if result['ai_component']:
			ai_component = BasicEnemy()
		return Entity(x, y, result['char'], libtcod.Color(result['color_r'], result['color_g'], result['color_b']), result['name'], blocks=result['blocks'], render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component, speed=result['speed'])
	elif subtype == 'items':
		return Entity(x, y, result['char'], libtcod.Color(result['color_r'], result['color_g'], result['color_b']), result['name'], render_order=RenderOrder.ITEM, item=get_function_by_name(result['item_use_function'], result['targeting_message'], result['item_amount'], result['damage_radius'], result['damage'], result['maximum_range']))
	elif subtype == 'equipment':
		if result['equipable_component']:
			eqslot = EquipmentSlots.MAIN_HAND
			if result['equipable_slots'] == 'EquipmentSlots.OFF_HAND':
				eqslot = EquipmentSlots.OFF_HAND
			elif result['equipable_slots'] == 'EquipmentSlots.OFF_HEAD':
				eqslot = EquipmentSlots.OFF_HEAD
			elif result['equipable_slots'] == 'EquipmentSlots.OFF_TORSO':
				eqslot = EquipmentSlots.OFF_TORSO
			elif result['equipable_slots'] == 'EquipmentSlots.OFF_LEGS':
				eqslot = EquipmentSlots.OFF_LEGS
			equipable_component = Equipable(eqslot, power_bonus=result['power_bonus'], defense_bonus=result['defense_bonus'], max_hp_bonus=result['max_hp_bonus'])
			return Entity(x, y, result['char'], libtcod.Color(result['color_r'], result['color_g'], result['color_b']), result['name'], render_order=RenderOrder.ITEM, equipable=equipable_component)


def load_rand_entity(rarity='common', etype='mobs', x=0, y=0, dungeon_level=1):
	listed = []
	if etype == 'mobs':
		subtype = 'mobs'
		loaded = loadedmobs
	elif etype == 'objects':
		if randint(1, 10) <= 8:
			subtype = 'items'
			loaded = loadeditems
		else:
			subtype = 'equipment'
			loaded = loadedequipment
	for v in loaded:
		if loaded[v]['rarity'] == rarity:
			listed.append(loaded[v])
	if not listed:
		for v in loaded:
			if loaded[v]['rarity'] == 'common':
				listed.append(loaded[v])
	return load_entity(listed, subtype, x, y)
