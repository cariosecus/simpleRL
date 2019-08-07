import tcod as libtcod
from enum import Enum
from game_states import GameStates
from menus import inventory_menu, level_up_menu, character_screen


class RenderOrder(Enum):
	STAIRS = 1
	CORPSE = 2
	ITEM = 3
	ACTOR = 4


def get_names_under_mouse(mouse, entities, fov_map):
	(x, y) = (mouse.cx, mouse.cy)

	names = [entity.name for entity in entities
			if entity.x == x and entity.y == y and libtcod.map_is_in_fov(fov_map, entity.x, entity.y)]
	names = ', '.join(names)

	return names.capitalize()


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
	bar_width = int(float(value) / maximum * total_width)

	libtcod.console_set_default_background(panel, back_color)
	libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

	libtcod.console_set_default_background(panel, bar_color)
	if bar_width > 0:
		libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

	libtcod.console_set_default_foreground(panel, libtcod.white)
	libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER, '{0}: {1}/{2}'.format(name, value, maximum))


def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height, bar_width, panel_height, panel_y, colors, game_state, mouse):
	# Draw all the tiles in the game map
	if fov_recompute:
		for y in range(game_map.height):
			for x in range(game_map.width):

				visible = libtcod.map_is_in_fov(fov_map, x, y)
				wall = game_map.tiles[x][y].block_sight

				if visible:
					if wall:
						libtcod.console_set_char_background(con, x, y, colors.get('light_wall'), libtcod.BKGND_SET)
					else:
						libtcod.console_set_char_background(con, x, y, colors.get('light_ground'), libtcod.BKGND_SET)
					game_map.tiles[x][y].explored = True
				elif game_map.tiles[x][y].explored:
					if wall:
						libtcod.console_set_char_background(con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
					else:
						libtcod.console_set_char_background(con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)
	entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

	# Draw all entities in the list
	for entity in entities_in_render_order:
		draw_entity(con, entity, fov_map, game_map)
	libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)
	libtcod.console_set_default_background(panel, libtcod.black)
	libtcod.console_clear(panel)
	# Print the game messages, one line at a time
	y = 1
	for message in message_log.messages:
		libtcod.console_set_default_foreground(panel, message.color)
		libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
		y += 1
	render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)
	libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level: {0}'.format(game_map.dungeon_level))
	# anything we're mousing over
	libtcod.console_set_default_foreground(panel, libtcod.light_gray)
	libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse(mouse, entities, fov_map))
	libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)
	if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
		if game_state == GameStates.SHOW_INVENTORY:
			inventory_title = 'Press the key next to an item to use it, or Esc to cancel.\n'
		else:
			inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'
		inventory_menu(con, inventory_title, player, 50, screen_width, screen_height)

	elif game_state == GameStates.LEVEL_UP:
		level_up_menu(con, 'You have leveled up! Choose a stat to raise:', player, 40, screen_width, screen_height)

	elif game_state == GameStates.CHARACTER_SCREEN:
		character_screen(player, 30, 10, screen_width, screen_height)


def clear_all(con, entities):
	for entity in entities:
		clear_entity(con, entity)


def draw_entity(con, entity, fov_map, game_map):
	if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or (entity.stairs and game_map.tiles[entity.x][entity.y].explored):
		libtcod.console_set_default_foreground(con, entity.color)
		libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)


def clear_entity(con, entity):
	# erase the character that represents this object
	libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)


def get_map_offset(console, game_map, curr_entity):
	# get our map panel's top left corner offset from the actual game map
	map_x = int(curr_entity.x - console.width / 2)
	if map_x < 0:
		map_x = 0
	elif map_x + console.width > game_map.width:
		map_x = game_map.width - console.width
	map_y = int(curr_entity.y - console.height / 2)
	if map_y < 0:
		map_y = 0
	elif map_y + console.height > game_map.height:
		map_y = game_map.height - console.height

	return (map_x, map_y)


def get_console_offset(console, game_map):
	# get our map's display offset from the top left corner of the console
	con_x = int((console.width - game_map.width) / 2)
	con_y = int((console.height - game_map.height) / 2)
	if con_x < 0:
		con_x = 0
	if con_y < 0:
		con_y = 0

	return (con_x, con_y)
