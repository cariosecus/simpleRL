import tcod as libtcod
from game_states import GameStates


class InputHandler(libtcod.event.EventDispatch):

	def __init__(self):
		self._actionq = []
		self.state = GameStates.PLAYERS_TURN

	def set_game_state(self, state):
		self.state = state

	def ev_quit(self, event):
		self._actionq.append({"exit": True})

	def ev_keydown(self, event):
		# fullscreen
		if (event.sym == libtcod.event.K_RETURN
				and event.mod & libtcod.event.KMOD_LALT):
			self._actionq.append({"fullscreen": True})

		# exit the game
		if event.sym == libtcod.event.K_ESCAPE:
			self._actionq.append({"exit": True})

		if self.state == GameStates.PLAYERS_TURN:
			if event.sym in keymap_players_turn.keys():
				self._actionq.append(keymap_players_turn[event.sym])
		elif self.state == GameStates.PLAYER_DEAD:
			if event.sym in keymap_player_dead.keys():
				self._actionq.append(keymap_player_dead[event.sym])
		elif self.state == GameStates.LEVEL_UP:
			if event.sym in keymap_level_up.keys():
				self._actionq.append(keymap_level_up[event.sym])
		elif self.state == GameStates.MAIN_MENU:
			if event.sym in keymap_main_menu.keys():
				self._actionq.append(keymap_main_menu[event.sym])

		elif self.state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.TARGETING):
			inv_index = event.sym - ord("a")
			if 0 <= inv_index < 26:
				self._actionq.append({"inventory_index": inv_index})

	def ev_mousemotion(self, event):
		x, y = event.tile
		self._actionq.append({"mousemotion": (x, y)})

	def ev_mousebuttondown(self, event):
		if self.state == GameStates.TARGETING:
			x, y = event.tile
			if event.button == libtcod.event.BUTTON_RIGHT:
				self._actionq.append({"cancel_target": True})
			elif event.button == libtcod.event.BUTTON_LEFT:
				self._actionq.append({"in_target": (x, y)})

	def get_action(self):
		if self._actionq:
			return self._actionq.pop(0)
		else:
			return {}

	def clear_actionq(self):
		self._actionq.clear()


keymap_players_turn = {
		# movement keys
		libtcod.event.K_UP: {"move": (0, -1)},
		libtcod.event.K_DOWN: {"move": (0, 1)},
		libtcod.event.K_LEFT: {"move": (-1, 0)},
		libtcod.event.K_RIGHT: {"move": (1, 0)},
		libtcod.event.K_w: {"move": (0, -1)},
		libtcod.event.K_s: {"move": (0, 1)},
		libtcod.event.K_a: {"move": (-1, 0)},
		libtcod.event.K_d: {"move": (1, 0)},
		libtcod.event.K_q: {"move": (-1, -1)},
		libtcod.event.K_e: {"move": (1, -1)},
		libtcod.event.K_z: {"move": (-1, 1)},
		libtcod.event.K_c: {"move": (1, 1)},
		# pick up
		libtcod.event.K_g: {"pickup": True},
		# inventory
		libtcod.event.K_i: {"show_inventory": True},
		libtcod.event.K_u: {"drop_inventory": True},
		libtcod.event.K_t: {"show_character_screen": True},
		# use
		libtcod.event.K_f: {"take_stairs": True},
		libtcod.event.K_x: {"wait": True},
		}
keymap_player_dead = {
		libtcod.event.K_i: {"show_inventory": True},
		}

keymap_level_up = {
		libtcod.event.K_a: {'level_up': 'hp'},
		libtcod.event.K_b: {'level_up': 'str'},
		libtcod.event.K_c: {'level_up': 'def'},
		}
keymap_main_menu = {
		libtcod.event.K_a: {'new_game': True},
		libtcod.event.K_b: {'load_game': True},
		libtcod.event.K_c: {"exit": True},
		}
