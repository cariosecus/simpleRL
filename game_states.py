from enum import Enum


class GameStates(Enum):
	PLAYERS_TURN = 1
	ENEMY_TURN = 2
	PLAYER_DEAD = 3
	SHOW_INVENTORY = 4
	DROP_INVENTORY = 5
	TARGETING = 6
	LEVEL_UP = 7
	CHARACTER_SCREEN = 8
	MAIN_MENU = 9


def set_game_state(current, new=GameStates.PLAYERS_TURN):
	previous_game_state = current
	current = new

	return previous_game_state
