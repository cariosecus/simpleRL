import tcod as libtcod
import tcod.event
from action_handlers import check_actions, action_turn_results
from entity import get_blocking_entities_at_location
from render_functions import clear_all, render_all
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from death_functions import kill_npc, kill_player
from game_messages import Message
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

		if move and game_state == GameStates.PLAYERS_TURN:
			dx, dy = move
			destination_x = player.x + dx
			destination_y = player.y + dy
			if not game_map.is_blocked(destination_x, destination_y):
				target = get_blocking_entities_at_location(entities, destination_x, destination_y)

				if target:
					attack_results = player.fighter.attack(target)
					player_turn_results.extend(attack_results)
				else:
					player.move(dx, dy)

					fov_recompute = True
			game_state = GameStates.ENEMY_TURN
		elif wait:
			message_log.add_message(Message('You wait.', libtcod.yellow))
			game_state = GameStates.ENEMY_TURN

		elif pickup and game_state == GameStates.PLAYERS_TURN:
			for entity in entities:
				if entity.item and entity.x == player.x and entity.y == player.y:
					pickup_results = player.inventory.add_item(entity)
					player_turn_results.extend(pickup_results)

					break
			else:
				message_log.add_message(Message('There is nothing here to pick up.', libtcod.yellow))

		if show_inventory:
			previous_game_state = game_state
			game_state = GameStates.SHOW_INVENTORY

		if drop_inventory:
			previous_game_state = game_state
			game_state = GameStates.DROP_INVENTORY

		if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
			item = player.inventory.items[inventory_index]
			if game_state == GameStates.SHOW_INVENTORY:
				player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
			elif game_state == GameStates.DROP_INVENTORY:
				player_turn_results.extend(player.inventory.drop_item(item))

		if take_stairs and game_state == GameStates.PLAYERS_TURN:
			for entity in entities:
				if entity.stairs and entity.x == player.x and entity.y == player.y:
					entities = game_map.next_floor(player, message_log, constants)
					fov_map = initialize_fov(game_map)
					fov_recompute = True
					libtcod.console_clear(con)

					break
			else:
				message_log.add_message(Message('There are no stairs here.', libtcod.yellow))

		if level_up:
			if level_up == 'hp':
				player.fighter.base_max_hp += 20
				player.fighter.hp += 20
			elif level_up == 'str':
				player.fighter.base_power += 1
			elif level_up == 'def':
				player.fighter.base_defense += 1

			game_state = previous_game_state

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
