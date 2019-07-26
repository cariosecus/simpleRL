import tcod as libtcod
import tcod.event
from input_handlers import InputHandler
from entity import *
from render_functions import clear_all, render_all, RenderOrder
from map_objects.game_map import GameMap
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from components.fighter import Fighter
from death_functions import kill_npc, kill_player

# global vars
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20
MAP_WIDTH = 80
MAP_HEIGHT = 43

# FOV constants
FOV_ALGORITHM = 0
FOV_LIGHT_WALLS = True
FOV_RADIUS = 10

# room constants
MAX_MONSTERS_PER_ROOM = 3
MAX_ROOMS = 30
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6

# UI constants
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT-PANEL_HEIGHT

colors = {
    'dark_wall': libtcod.Color(0, 0, 100),
    'dark_ground': libtcod.Color(50, 50, 150),
    'light_wall': libtcod.Color(130, 110, 50),
    'light_ground': libtcod.Color(200, 180, 50)
}
# main process
def main():
    entities = []
    fighter_component = Fighter(hp=30, defense=2, power=5)
    player = Entity(0, 0, '@', libtcod.white, 'Player', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component)
    entities = [player]
    libtcod.console_set_custom_font('images/arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'simpleRL', False, libtcod.RENDERER_SDL2,'F',True)

    con = libtcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT)
    panel = libtcod.console.Console(SCREEN_WIDTH, PANEL_HEIGHT)

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
        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, SCREEN_WIDTH, SCREEN_HEIGHT, BAR_WIDTH, PANEL_HEIGHT, PANEL_Y, colors)
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
        player_turn_results = []

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
        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            print(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_npc(dead_entity)

                            print(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYERS_TURN
        if doexit:
            return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')

            if message:
                print(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_npc(dead_entity)

                print(message)

if __name__ == '__main__':
    main()
