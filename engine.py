import tcod as libtcod
import tcod.event
from input_handlers import InputHandler
from entities.entity import *
from render_functions import clear_all, render_all
from map_objects.game_map import GameMap
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates

# global vars
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20
MAP_WIDTH = 80
MAP_HEIGHT = 45

# FOV constants
FOV_ALGORITHM = 0
FOV_LIGHT_WALLS = True
FOV_RADIUS = 10

# room constants
MAX_MONSTERS_PER_ROOM = 3
MAX_ROOMS = 30
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
colors = {
    'dark_wall': libtcod.Color(0, 0, 100),
    'dark_ground': libtcod.Color(50, 50, 150),
    'light_wall': libtcod.Color(130, 110, 50),
    'light_ground': libtcod.Color(200, 180, 50)
}
# main process
def main():
    entities = []
    player = Entity(0, 0, '@', libtcod.white, 'Player', blocks=True)
    entities = [player]
    libtcod.console_set_custom_font('images/arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'simpleRL', False, libtcod.RENDERER_SDL2,'F',True)
    con = libtcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT)
    game_map = GameMap(MAP_WIDTH,MAP_HEIGHT)
    game_map.make_map(MAX_ROOMS, ROOM_MIN_SIZE, ROOM_MAX_SIZE, MAP_WIDTH, MAP_HEIGHT, player, entities, MAX_MONSTERS_PER_ROOM)
    fov_recompute = True
    fov_map = initialize_fov(game_map)
    libtcod.sys_set_fps(LIMIT_FPS)
    in_handle = InputHandler()
    game_state = GameStates.PLAYERS_TURN

    #main game loop
    while True:
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, FOV_RADIUS, FOV_LIGHT_WALLS, FOV_ALGORITHM)
        render_all(con, entities, game_map, fov_map, fov_recompute, SCREEN_WIDTH, SCREEN_HEIGHT, colors)
        fov_recompute = False
        libtcod.console_flush()
        clear_all(con, entities)
        # using the event handler instead of the loop from the RL tutorial
        for event in tcod.event.get():
            in_handle.dispatch(event)
        action = in_handle.get_action()
        move = action.get('move')
        doexit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy
            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target:
                    print('You push the ' + target.name + ', trying to move it out of the way!')
                else:
                    player.move(dx, dy)

                    fov_recompute = True
            game_state = GameStates.ENEMY_TURN
        if doexit:
            return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

if __name__ == '__main__':
    main()
