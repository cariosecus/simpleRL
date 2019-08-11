import tcod as libtcod
import tcod.event
from input_handlers import InputHandler
from game_states import GameStates
from game_messages import Message
from render_functions import get_console_offset, get_map_offset
from death_functions import kill_player, kill_npc
from entity import get_blocking_entities_at_location
from fov_functions import initialize_fov


def check_actions(game_state, game_map):
	in_handle = InputHandler()
	in_handle.set_game_state(game_state)
	in_handle.set_game_map(game_map)
	for event in tcod.event.get():
		in_handle.dispatch(event)
	action = in_handle.get_action()

	move = action.get('move')
	wait = action.get('wait')
	doexit = action.get('exit')
	pickup = action.get('pickup')
	fullscreen = action.get('fullscreen')
	show_inventory = action.get('show_inventory')
	drop_inventory = action.get('drop_inventory')
	inventory_index = action.get('inventory_index')
	take_stairs = action.get('take_stairs')
	level_up = action.get('level_up')
	show_character_screen = action.get('show_character_screen')
	in_target = action.get("in_target")
	mousemotion = action.get("mousemotion")
	left_click = action.get('in_target')
	right_click = action.get('cancel_target')

	return move, wait, doexit, pickup, fullscreen, show_inventory, drop_inventory, inventory_index, take_stairs, level_up, show_character_screen, in_target, mousemotion, left_click, right_click


def get_turn_results(player_turn_result):
	message = player_turn_result.get('message')
	dead_entity = player_turn_result.get('dead')
	item_added = player_turn_result.get('item_added')
	item_consumed = player_turn_result.get('consumed')
	item_dropped = player_turn_result.get('item_dropped')
	equip = player_turn_result.get('equip')
	targeting = player_turn_result.get('targeting')
	targeting_cancelled = player_turn_result.get('targeting_cancelled')
	xp = player_turn_result.get('xp')
	return message, dead_entity, item_added, item_consumed, item_dropped, equip, targeting, targeting_cancelled, xp


def action_turn_results(player_turn_results, message_log, player, con, game_map, in_target, entities, game_state, previous_game_state, targeting_item):
	for player_turn_result in player_turn_results:
		message, dead_entity, item_added, item_consumed, item_dropped, equip, targeting, targeting_cancelled, xp = get_turn_results(player_turn_result)

		if message:
			message_log.add_message(message)

		if xp:
			leveled_up = player.level.add_xp(xp)
			message_log.add_message(Message('You gain {0} experience points.'.format(xp)))

			if leveled_up:
				message_log.add_message(Message(
					'Your battle skills grow stronger! You reached level {0}'.format(
						player.level.current_level) + '!', libtcod.yellow))
				previous_game_state = game_state
				game_state = GameStates.LEVEL_UP

		if dead_entity:
			if dead_entity == player:
				message, game_state = kill_player(dead_entity)
			else:
				message = kill_npc(dead_entity)

			message_log.add_message(message)

		game_state, message_log, targeting_item = action_check_items(item_added, item_consumed, item_dropped, in_target, game_state, previous_game_state, equip, targeting, targeting_cancelled, message_log, player, con, game_map, entities, targeting_item)

	return game_state, message_log, targeting_item


def check_movement(game_state, game_map, entitytype='player'):
	if game_map.turn_based is True:
		if game_state == GameStates.PLAYERS_TURN and entitytype == 'player':
			return True
		elif game_state == GameStates.ENEMY_TURN and entitytype == 'npc':
			return True
		else:
			return False
	else:
		if game_state in (GameStates.PLAYERS_TURN, GameStates.ENEMY_TURN):
			return True
		else:
			return False


def action_check_player_actions(game_state, move, player, game_map, entities, player_turn_results, wait, message_log, take_stairs, level_up, previous_game_state, constants, con, fov_recompute, fov_map):
	if move and check_movement(game_state, game_map, 'player') is True:
		if player.wait > 0:
			player.wait -= 1
			return game_state, fov_recompute, fov_map, con, entities
		dx, dy = move
		destination_x = player.x + dx
		destination_y = player.y + dy
		if not game_map.is_blocked(destination_x, destination_y):
			target = get_blocking_entities_at_location(entities, destination_x, destination_y)
			if target:
				attack_results = player.fighter.attack(target, game_map)
				player_turn_results.extend(attack_results)
			else:
				player.move(dx, dy)
				if game_map.turn_based is False:
					player.wait = player.speed
				else:
					player.wait = 0
				fov_recompute = True
		game_state = GameStates.ENEMY_TURN

	elif wait:
		message_log.add_message(Message('You wait.', libtcod.yellow))
		game_state = GameStates.ENEMY_TURN

	if take_stairs and check_movement(game_state, game_map, 'player'):
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
	return game_state, fov_recompute, fov_map, con, entities


def action_check_inventory(pickup, drop_inventory, game_state, entities, player, player_turn_results, message_log, show_inventory, fov_map, inventory_index, previous_game_state, game_map):

	if pickup and check_movement(game_state, game_map, 'player'):
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

	if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
			player.inventory.items):
		item = player.inventory.items[inventory_index]

		if game_state == GameStates.SHOW_INVENTORY:
			player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
		elif game_state == GameStates.DROP_INVENTORY:
			player_turn_results.extend(player.inventory.drop_item(item))
	return player_turn_results, previous_game_state, game_state


def action_check_items(item_added, item_consumed, item_dropped, in_target, game_state, previous_game_state, equip, targeting, targeting_cancelled, message_log, player, con, game_map, entities, targeting_item):
	if targeting:
		previous_game_state = game_state
		game_state = GameStates.TARGETING
		targeting_item = targeting
		if isinstance(targeting_item.item.targeting_message, str):
			message_log.add_message(targeting_item.item.targeting_message)

	if targeting_cancelled:
		game_state = previous_game_state
		message_log.add_message(Message('Targeting cancelled'))

	if item_added:
		entities.remove(item_added)
		game_state = GameStates.ENEMY_TURN

	if item_consumed:
		game_state = GameStates.ENEMY_TURN

	if in_target and game_state == GameStates.TARGETING:
		x, y = in_target
		map_x, map_y = get_map_offset(con, game_map, player)
		con_x, con_y = get_console_offset(con, game_map)
		x_off = map_x - con_x
		y_off = map_y - con_y
		x += x_off
		y += y_off
		targeting_item.item.target_x = x
		targeting_item.item.target_y = y

		message_log.add_message(targeting_item.item.targeting_message)

	if item_dropped:
		entities.append(item_dropped)
		game_state = GameStates.ENEMY_TURN

	if equip:
		equip_results = player.equipment.toggle_equip(equip)

		for equip_result in equip_results:
			equiped = equip_result.get('equiped')
			dequiped = equip_result.get('dequiped')

			if equiped:
				message_log.add_message(Message('You equiped the {0}'.format(equiped.name)))

			if dequiped:
				message_log.add_message(Message('You dequiped the {0}'.format(dequiped.name)))

		game_state = GameStates.ENEMY_TURN
	return game_state, message_log, targeting_item


def action_enemy_turn(game_state, entities, player, fov_map, game_map, message_log):
	if check_movement(game_state, game_map, entitytype='npc'):
		enemy_turn_results = []
		for entity in entities:
			if entity.ai:
				if entity.wait > 0:
					entity.wait -= 1
				else:
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
	return game_state, message_log
