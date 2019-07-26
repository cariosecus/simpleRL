import tcod as libtcod
import tcod.event
from input_handlers import InputHandler
from entity import Entity
from render_functions import clear_all, render_all
from map_objects.game_map import GameMap

# global vars
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20
MAP_WIDTH = 80
MAP_HEIGHT = 45

colors = {
    'dark_wall': libtcod.Color(0, 0, 100),
    'dark_ground': libtcod.Color(50, 50, 150)
}
# main process
def main():
    entities = []
    player = Entity(int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2), '@', libtcod.white)
    npc = Entity(int(SCREEN_WIDTH / 2 - 5), int(SCREEN_HEIGHT / 2), '@', libtcod.yellow)
    entities = [npc, player]
    libtcod.console_set_custom_font('images/arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'simpleRL', False, libtcod.RENDERER_SDL2,'F',True)
    con = libtcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT)
    game_map = GameMap(MAP_WIDTH,MAP_HEIGHT)
    game_map.make_map()
    libtcod.sys_set_fps(LIMIT_FPS)
    in_handle = InputHandler()
#main game loop
    while True:
        render_all(con, entities, game_map, SCREEN_WIDTH, SCREEN_HEIGHT, colors)
        libtcod.console_flush()
        clear_all(con, entities)
        # using the event handler instead of the loop from the RL tutorial
        for event in tcod.event.get():
            in_handle.dispatch(event)
        action = in_handle.get_action()
        move = action.get('move')
        doexit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move:
            dx, dy = move
            if not game_map.is_blocked(player.x + dx, player.y + dy):
                player.move(dx, dy)

        if doexit:
            return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

if __name__ == '__main__':
    main()
