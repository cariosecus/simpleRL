import tcod as libtcod
import tcod.event
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
			# movement keys
			if event.sym == libtcod.event.K_UP:
				self._actionq.append({"move": (0, -1)})
			elif event.sym == libtcod.event.K_DOWN:
				self._actionq.append({"move": (0, 1)})
			elif event.sym == libtcod.event.K_LEFT:
				self._actionq.append({"move": (-1, 0)})
			elif event.sym == libtcod.event.K_RIGHT:
				self._actionq.append({"move": (1, 0)})
			elif event.sym == libtcod.event.K_w:
				self._actionq.append({"move": (0, -1)})
			elif event.sym == libtcod.event.K_s:
				self._actionq.append({"move": (0, 1)})
			elif event.sym == libtcod.event.K_a:
				self._actionq.append({"move": (-1, 0)})
			elif event.sym == libtcod.event.K_d:
				self._actionq.append({"move": (1, 0)})
			elif event.sym == libtcod.event.K_q:
				self._actionq.append({"move": (-1, -1)})
			elif event.sym == libtcod.event.K_e:
				self._actionq.append({"move": (1, -1)})
			elif event.sym == libtcod.event.K_z:
				self._actionq.append({"move": (-1, 1)})
			elif event.sym == libtcod.event.K_c:
				self._actionq.append({"move": (1, 1)})
				# pick up
			elif event.sym == libtcod.event.K_g:
				self._actionq.append({"pickup": True})
				# inventory
			elif event.sym == libtcod.event.K_i:
				self._actionq.append({"show_inventory": True})
			elif event.sym == libtcod.event.K_u:
				self._actionq.append({"drop_inventory": True})
			elif event.sym == libtcod.event.K_t:
				self._actionq.append({"show_character_screen": True})
				# use
			elif event.sym == libtcod.event.K_f:
				self._actionq.append({"take_stairs": True})
			elif event.sym == libtcod.event.K_x:
				self._actionq.append({"wait": True})
		elif self.state == GameStates.PLAYER_DEAD:
			if event.sym == libtcod.event.K_i:
				self._actionq.append({"show_inventory": True})

		elif self.state in (GameStates.SHOW_INVENTORY,GameStates.DROP_INVENTORY,GameStates.TARGETING):
			inv_index = event.sym - ord("a")
			if 0 <= inv_index < 26:
				self._actionq.append({"inventory_index": inv_index})

		elif self.state == GameStates.LEVEL_UP:
			if event.sym == libtcod.event.K_a:
				self._actionq.append({'level_up': 'hp'})
			elif event.sym == libtcod.event.K_b:
				self._actionq.append({'level_up': 'str'})
			elif event.sym == libtcod.event.K_c:
				self._actionq.append({'level_up': 'def'})
			return {}

		elif self.state == GameStates.MAIN_MENU:
			if event.sym == libtcod.event.K_a:
				self._actionq.append({'new_game': True})
			elif event.sym == libtcod.event.K_b:
				self._actionq.append({'load_game': True})
			elif event.sym == libtcod.event.K_c:
				self._actionq.append({"exit": True})

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
