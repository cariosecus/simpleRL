import tcod as libtcod
import tcod.event
from action_handlers import check_actions, action_turn_results, action_check_player_actions
from render_functions import clear_all, render_all
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from death_functions import kill_npc, kill_player
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

		move, wait, doexit, pickup, fullscreen, show_inventory, drop_inventory, inventory_index, take_stairs, level_up, show_character_screen, in_target, mousemotion, left_click, right_click = check_actions(game_state)

		player_turn_results = []

		if mousemotion:
			render_update = True

		if render_update:
			render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, constants['screen_width'], constants['screen_height'], constants['bar_width'], constants['panel_height'], constants['panel_y'], constants['colors'], game_state, mouse)
			tcod.console_flush()
			render_update = False

		fov_map, fov_recompute = action_check_player_actions(game_state, move, player, game_map, entities, player_turn_results, wait, pickup, message_log, take_stairs, fov_map, level_up, previous_game_state, constants, con)

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
		action_turn_results(player_turn_results, message_log, player, con, game_map, in_target, entities, game_state, previous_game_state)

		if game_state == GameStates.ENEMY_TURN:
			for entity in entities:
				if entity.ai:
					enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

					for enemy_turn_result in enemy_turn_results:
						message = enemy_turn_result.get('message')
						dead_entity = enemy_turn_result.get('dead')

						if message:
							message_log.add_message(message)

						if dead_entity:
							if dead_entity == player:
								message, game_state = kill_player(dead_entity)
							else:
								message = kill_npc(dead_entity)

							message_log.add_message(message)

							if game_state == GameStates.PLAYER_DEAD:
								break

					if game_state == GameStates.PLAYER_DEAD:
						break

			else:
				game_state = GameStates.PLAYERS_TURN
