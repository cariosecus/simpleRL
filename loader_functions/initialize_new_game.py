import tcod as libtcod
from components.equipment import Equipment
from entity import Entity
from components.equipable import Equipable
from components.fighter import Fighter
from components.inventory import Inventory
from game_messages import MessageLog
from game_states import GameStates
from map_objects.game_map import GameMap
from render_functions import RenderOrder
from components.level import Level
from equipment_slots import EquipmentSlots
from loader_functions.data_loaders import loadyaml


def get_constants():
	loadedvars = loadyaml('data/variables.yaml')
	PANEL_Y = loadedvars['SCREEN_HEIGHT']-loadedvars['PANEL_HEIGHT']
	MESSAGE_X = loadedvars['BAR_WIDTH']+2
	MESSAGE_WIDTH = loadedvars['SCREEN_WIDTH']-loadedvars['BAR_WIDTH']-2
	MESSAGE_HEIGHT = loadedvars['PANEL_HEIGHT']-1
	colors = loadyaml('data/turfs.yaml')

	constants = {
		'window_title': loadedvars['WINDOW_TITLE'],
		'screen_width': loadedvars['SCREEN_WIDTH'],
		'screen_height': loadedvars['SCREEN_HEIGHT'],
		'bar_width': loadedvars['BAR_WIDTH'],
		'panel_height': loadedvars['PANEL_HEIGHT'],
		'panel_y': PANEL_Y,
		'message_x': MESSAGE_X,
		'message_width': MESSAGE_WIDTH,
		'message_height': MESSAGE_HEIGHT,
		'map_width': loadedvars['MAP_WIDTH'],
		'map_height': loadedvars['MAP_HEIGHT'],
		'room_max_size': loadedvars['ROOM_MAX_SIZE'],
		'room_min_size': loadedvars['ROOM_MIN_SIZE'],
		'max_rooms': loadedvars['MAX_ROOMS'],
		'fov_algorithm': loadedvars['FOV_ALGORITHM'],
		'fov_light_walls': loadedvars['FOV_LIGHT_WALLS'],
		'fov_radius': loadedvars['FOV_RADIUS'],
		'max_monsters_per_room': loadedvars['MAX_MONSTERS_PER_ROOM'],
		'max_items_per_room': loadedvars['MAX_ITEMS_PER_ROOM'],
		'colors': colors
	}
	return constants


def get_game_variables(constants):
	fighter_component = Fighter(hp=100, defense=1, power=2)
	inventory_component = Inventory(26)
	level_component = Level()
	equipment_component = Equipment()
	player = Entity(0, 0, 208, libtcod.lightest_gray, 'Player', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, inventory=inventory_component, level=level_component, equipment=equipment_component)
	entities = [player]

	equipable_component = Equipable(EquipmentSlots.MAIN_HAND, power_bonus=0.75)
	dagger = Entity(0, 0, '-', libtcod.sky, 'Dagger', equipable=equipable_component)
	player.inventory.add_item(dagger)
	player.equipment.toggle_equip(dagger)

	game_map = GameMap(constants['map_width'], constants['map_height'])
	game_map.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'], constants['map_width'], constants['map_height'], player, entities)
	message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'], 100)

	game_state = GameStates.PLAYERS_TURN

	return player, entities, game_map, message_log, game_state
