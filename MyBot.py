# This version a bit more complex than v8.
# Ships will react on both planets and enemy ships.
# Actions for closes planets are the same as in v8, but not closes enemy ships will be attacked

import time
import hlt
import logging
from hlt.entity import Position, Planet


game = hlt.Game("AM-Random-9")


def dest(a, b):
    x = a.x - b.x
    y = a.y - b.y
    return (x * x) + (y * y)


def navigate_planet(ship, planet, game_map):
    c = ship.navigate(
        ship.closest_point_to(planet),
        game_map,
        speed=int(hlt.constants.MAX_SPEED),
        ignore_ships=False)
    if not c:
        logging.warning("Couldn't navigate planet %s with ship %s" % (planet.id, ship.id))
    return c


def attack_planet(ship, planet, game_map):
    p = Position(planet.x, planet.y)
    c = ship.navigate(
        p,
        game_map,
        speed=int(hlt.constants.MAX_SPEED),
        ignore_ships=False,
        ignore_planets=False)
    if not c:
        logging.warning("Couldn't attack planet %s with ship %s" % (planet.id, ship.id))
    return c


def ship_against_ship(ship, enemy_ship, game_map):
    p = Position(enemy_ship.x, enemy_ship.y)
    c = ship.navigate(
        p,
        game_map,
        speed=int(hlt.constants.MAX_SPEED),
        ignore_ships=False,
        ignore_planets=False)
    if not c:
        logging.warning("Couldn't attack enemy %s with ship %s" % (enemy_ship.id, ship.id))
    return c


def ship_against_planet(ship, planet, me, game_map):
    # try to dock at any own planet immediately
    if planet.owner == me:
        # dock is planet is not full
        if ship.can_dock(planet) and not planet.is_full():
            return ship.dock(planet)

    # settle unowned planets next
    if planet.owner is None:
        # dock unowned planet or navigate to it
        if ship.can_dock(planet):
            return ship.dock(planet)
        logging.info("Trying to navigate planet %s with ship %s" % (planet.id, ship.id))
        action = navigate_planet(ship, planet, game_map)
        if action:
            return action

    # attack enemy planet
    if planet.owner != me:
        action = attack_planet(ship, planet, game_map)
        if action:
            return action


def action_for_ship(ship, entities, me, game_map):

    for entity in entities:
        if isinstance(entity, Planet):
            action = ship_against_planet(ship, entity, me, game_map)
        else:
            action = ship_against_ship(ship, entity, game_map)

        if action:
            return action

    logging.warning("Nothing worked for ship %s" % ship.id)
    return None


def get_enemy_ships(game_map, me):
    all_ships = []
    for player in game_map.all_players():
        if player != me:
            all_ships.extend(player.all_ships())
    return all_ships


def iterate_world():
    start_time = time.time()

    game_map = game.update_map()
    cmd = []

    planets = list((game_map.all_planets()))
    me = game_map.get_me()
    ships = filter(lambda x: x.docking_status == x.DockingStatus.UNDOCKED,
                   me.all_ships())
    enemy_ships = get_enemy_ships(game_map, me)

    for ship in ships:
        run_time = time.time() - start_time
        # logging.info("Runtime: %s" % run_time)
        # this line prevents timeouts, because it is a big problem for Python bots in general
        if run_time > 1.0:
            break
        _e = sorted(planets + enemy_ships, key=lambda x: dest(ship, x))
        a = action_for_ship(ship, _e, me, game_map)
        if a:
            cmd.append(a)
    return cmd


logging.info("Starting my AM-Random bot!")
while True:
    __w = iterate_world()
    game.send_command_queue(__w)
