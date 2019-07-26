import tcod as libtcod

class BasicEnemy:
    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        npc = self.owner
        if libtcod.map_is_in_fov(fov_map, npc.x, npc.y):

            if npc.distance_to(target) >= 2:
                npc.move_astar(target, entities, game_map)

            elif target.fighter.hp > 0:
                attack_results = npc.fighter.attack(target)
                results.extend(attack_results)
        return results
