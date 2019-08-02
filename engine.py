import tcod as libtcod
import tcod.event
from input_handlers import InputHandler
from entities.entity import get_blocking_entities_at_location
from render_functions import clear_all, render_all
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from death_functions import kill_npc, kill_player
from game_messages import Message
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box
# main process
def main():
    constants = get_constants()
    libtcod.console_set_custom_font('images/arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(constants['SCREEN_WIDTH'], constants['SCREEN_HEIGHT'], 'simpleRL', False, libtcod.RENDERER_SDL2,'F',True)
    libtcod.sys_set_fps(LIMIT_FPS)

    con = libtcod.console.Console(constants['SCREEN_WIDTH'], constants['SCREEN_HEIGHT'])
    panel = libtcod.console.Console(constants['SCREEN_WIDTH'], constants['SCREEN_HEIGHT'])

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = libtcod.image_load('images/menu_background1.png')

    game_map = GameMap(constants['SCREEN_WIDTH'], constants['SCREEN_HEIGHT'])
    game_map.make_map(constants['MAX_ROOMS'], constants['ROOM_MIN_SIZE'], constants['ROOM_MAX_SIZE'], constants['SCREEN_WIDTH'], constants['SCREEN_HEIGHT'], player, entities, constants['MAX_MONSTERS_PER_ROOM'], constants['MAX_ITEMS_PER_ROOM'])
    fov_recompute = True
    fov_map = initialize_fov(game_map)
    in_handle = InputHandler()
    previous_game_state = game_state
    targeting_item = None

    #main game loop
    while True:
        if show_main_menu:
            main_menu(con, main_menu_background_image, constants['SCREEN_WIDTH'],
                      constants['SCREEN_HEIGHT'])

            if show_load_error_message:
                message_box(con, 'No save game to load', 50, constants['SCREEN_WIDTH'], constants['SCREEN_HEIGHT'])

            libtcod.console_flush()

            action = handle_main_menu(key)

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
            libtcod.console_clear(con)
            play_game(player, entities, game_map, message_log, game_state, con, panel, constants)

            show_main_menu = True

if __name__ == '__main__':
    main()

def play_game(player, entities, game_map, message_log, game_state, con, panel, constants):
    fov_recompute = True
    fov_map = initialize_fov(game_map)
    in_handle = InputHandler()
    game_state = GameStates.PLAYERS_TURN
    previous_game_state = game_state
    targeting_item = None

    #main game loop
    while True:
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants['FOV_RADIUS'], constants['FOV_LIGHT_WALLS'], constants['FOV_ALGORITHM'])
        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, constants['SCREEN_WIDTH'], constants['SCREEN_HEIGHT'], constants['BAR_WIDTH'], constants['PANEL_HEIGHT'], constants['PANEL_Y'], constants['colors'], game_state)
        fov_recompute = False
        libtcod.console_flush()
        clear_all(con, entities)
        # using the event handler instead of the loop from the RL tutorial
        in_handle.set_game_state(game_state)
        for event in tcod.event.get():
            in_handle.dispatch(event)
        action = in_handle.get_action()
        move = action.get('move')
        doexit = action.get('exit')
        pickup = action.get('pickup')
        fullscreen = action.get('fullscreen')
        mousemotion = action.get("mousemotion")
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        in_target = action.get("in_target")
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

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))
        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})
        if doexit:
            if game_state == GameStates.SHOW_INVENTORY:
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, message_log, game_state)
                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')

            if message:
                message_log.add_message(message)

            if targeting_cancelled:
                game_state = previous_game_state

                message_log.add_message(Message('Targeting cancelled'))
            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_npc(dead_entity)

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if in_target and game_state == GameStates.TARGETING:
                x, y = in_target
                map_x, map_y = get_map_offset(console, game_map, curr_entity)
                con_x, con_y = get_console_offset(console, game_map)
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
