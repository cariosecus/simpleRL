import tcod as libtcod
import tcod.event
from input_handlers import InputHandler
from game_states import GameStates
from game_messages import Message
from render_functions import get_console_offset, get_map_offset
from death_functions import kill_player, kill_npc


def check_actions(game_state):
	in_handle = InputHandler()
	in_handle.set_game_state(game_state)
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


def action_turn_results(player_turn_results, message_log, player, con, game_map, in_target, entities, game_state, previous_game_state):
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

		action_check_items(item_added, item_consumed, item_dropped, in_target, game_state, previous_game_state, equip, targeting, targeting_cancelled, message_log, player, con, game_map, entities)


def action_check_items(item_added, item_consumed, item_dropped, in_target, game_state, previous_game_state, equip, targeting, targeting_cancelled, message_log, player, con, game_map, entities):
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
