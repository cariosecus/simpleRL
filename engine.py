import tcod as libtcod
import tcod.event
from play_game import play_game
from input_handlers import InputHandler
from game_states import GameStates
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game
from menus import main_menu, message_box


# main process
def main():
	constants = get_constants()
	libtcod.console_set_custom_font('images/simplerl_12x12.png',
									libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GREYSCALE)
	libtcod.console_init_root(constants['screen_width'], constants['screen_height'],
							constants['window_title'], False, libtcod.RENDERER_SDL2, 'F', True)

	con = libtcod.console.Console(constants['screen_width'], constants['screen_height'])
	panel = libtcod.console.Console(constants['screen_width'], constants['panel_height'])

	player = None
	entities = []
	game_map = None
	message_log = None
	game_state = None
	show_main_menu = True
	show_load_error_message = False

	main_menu_background_image = libtcod.image_load('images/menu_background1.png')

	in_handle = InputHandler()
# main game loop
	while True:
		if show_main_menu:
			main_menu(con, main_menu_background_image,
					constants['screen_width'], constants['screen_height'])

			if show_load_error_message:
				message_box(con, 'No save game to load', 50,
							constants['screen_width'], constants['screen_height'])

			libtcod.console_flush()
			game_state = GameStates.MAIN_MENU
			in_handle.set_game_state(game_state)
			for event in tcod.event.get():
				in_handle.dispatch(event)
			action = in_handle.get_action()
			new_game = action.get('new_game')
			load_saved_game = action.get('load_game')
			exit_game = action.get('exit')

			if show_load_error_message and (new_game or load_saved_game or exit_game):
				show_load_error_message = False

			elif new_game:
				player, entities, game_map, message_log, game_state = get_game_variables(constants)
				game_state = GameStates.PLAYERS_TURN

				show_main_menu = False
			elif load_saved_game:
				try:
					player, entities, game_map, message_log, game_state = load_game()
					show_main_menu = False
				except FileNotFoundError:
					show_load_error_message = True
			elif exit_game:
				break

		else:
			con.clear(fg=[63, 127, 63])
			play_game(player, entities, game_map, message_log, game_state, con, panel, constants)

			show_main_menu = True


if __name__ == '__main__':
	main()
