import tcod as libtcod

class InputHandler(libtcod.event.EventDispatch):

    def __init__(self):
        self._actionq = []

    def ev_quit(self, event):
        self._actionq.append({"exit": True})

    def ev_keydown(self, event):
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
        elif event.sym == libtcod.event.K_f:
            self._actionq.append({"pickup": True})
        # fullscreen
        if (event.sym == libtcod.event.K_RETURN
                and event.mod & libtcod.event.KMOD_LALT):
            self._actionq.append({"fullscreen": True})

        # exit the game
        if event.sym == libtcod.event.K_ESCAPE:
            self._actionq.append({"exit": True})

    def get_action(self):
        if self._actionq:
            return self._actionq.pop(0)
        else:
            return {}

    def clear_actionq(self):
        self._actionq.clear()
