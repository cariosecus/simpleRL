import tcod as libtcod
import tcod.event
from action_handlers import check_actions, action_turn_results, action_check_player_actions, action_enemy_turn, action_check_inventory
from render_functions import clear_all, render_all
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from loader_functions.data_loaders import save_game


def rendering_proc(player, entities, game_map, message_log, game_state, con, panel, constants, fov_map, mouse, fov_recompute=False):
	if fov_recompute:
		recompute_fov(fov_map, player.x, player.y, constants['fov_radius'], constants['fov_light_walls'], constants['fov_algorithm'])
	render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, constants['screen_width'], constants['screen_height'], constants['bar_width'], constants['panel_height'], constants['panel_y'], constants['colors'], game_state, mouse)
	fov_recompute = False
	libtcod.console_flush()
	clear_all(con, entities)


def play_game(player, entities, game_map, message_log, game_state, con, panel, constants):
	fov_recompute = True
	fov_map = initialize_fov(game_map)
	game_state = GameStates.PLAYERS_TURN
	previous_game_state = game_state
	targeting_item = None
	mouse = libtcod.Mouse()
	key = libtcod.Key()
	render_update = True

# main game loop
	while True:
		libtcod.sys_check_for_event(libtcod.EVENT_MOUSE, key, mouse)

		rendering_proc(player, entities, game_map, message_log, game_state, con, panel, constants, fov_map, mouse, fov_recompute)

		move, wait, doexit, pickup, fullscreen, show_inventory, drop_inventory, inventory_index, take_stairs, level_up, show_character_screen, in_target, mousemotion, left_click, right_click = check_actions(game_state, game_map)

		player_turn_results = []

		if mousemotion:
			render_update = True

		if render_update:
			render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, constants['screen_width'], constants['screen_height'], constants['bar_width'], constants['panel_height'], constants['panel_y'], constants['colors'], game_state, mouse)
			tcod.console_flush()
			render_update = False

		game_state, fov_recompute, fov_map, con, entities = action_check_player_actions(game_state, move, player, game_map, entities, player_turn_results, wait, message_log, take_stairs, level_up, previous_game_state, constants, con, fov_recompute, fov_map)
		player_turn_results, previous_game_state, game_state = action_check_inventory(pickup, drop_inventory, game_state, entities, player, player_turn_results, message_log, show_inventory, fov_map, inventory_index, previous_game_state, game_map)
		if show_character_screen:
			previous_game_state = game_state
			game_state = GameStates.CHARACTER_SCREEN

		if game_state == GameStates.TARGETING:
			if left_click:
				target_x, target_y = left_click

				item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map, target_x=target_x, target_y=target_y)
				player_turn_results.extend(item_use_results)
			elif right_click:
				player_turn_results.append({'targeting_cancelled': True})

		if doexit:
			if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN):
				game_state = previous_game_state
			elif game_state == GameStates.TARGETING:
				player_turn_results.append({'targeting_cancelled': True})
			else:
				save_game(player, entities, game_map, message_log, game_state)
				return True

		if fullscreen:
			libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

		game_state, message_log, targeting_item = action_turn_results(player_turn_results, message_log, player, con, game_map, in_target, entities, game_state, previous_game_state, targeting_item)

		game_state, message_log = action_enemy_turn(game_state, entities, player, fov_map, game_map, message_log)
