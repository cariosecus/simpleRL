import tcod as libtcod
from render_functions import RenderOrder
from game_states import GameStates
from game_messages import Message

def kill_player(player):
    player.char = '%'
    player.color = libtcod.dark_red

    return Message('You died!', libtcod.red), GameStates.PLAYER_DEAD


def kill_npc(npc):
    death_message = Message('{0} is dead!'.format(npc.name.capitalize()), libtcod.orange)

    npc.char = '%'
    npc.color = libtcod.dark_red
    npc.blocks = False
    npc.fighter = None
    npc.ai = None
    npc.name = 'remains of ' + npc.name
    npc.render_order = RenderOrder.CORPSE

    return death_message
