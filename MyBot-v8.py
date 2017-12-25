# Greedy solution for capturing closes planets first.

import time
import hlt
import logging
from hlt.entity import Position


game = hlt.Game("AM-Random-8")


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



def action_for_ship(ship, planets, me, game_map):

    for planet in planets:

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

    logging.warning("Nothing worked for ship %s" % ship.id)
    return None


def iterate_world():
    start_time = time.time()

    game_map = game.update_map()
    cmd = []

    planets = list((game_map.all_planets()))
    me = game_map.get_me()
    ships = filter(lambda x: x.docking_status == x.DockingStatus.UNDOCKED,
                   me.all_ships())

    for ship in ships:
        run_time = time.time() - start_time
        # logging.info("Runtime: %s" % run_time)
        # this line prevents timeouts, because it is a big problem for Python bots in general
        if run_time > 1.0:
            break
        _p = sorted(planets, key=lambda x: dest(ship, x))
        a = action_for_ship(ship, _p, me, game_map)
        if a:
            cmd.append(a)
    return cmd


logging.info("Starting my AM-Random bot!")
while True:
    __w = iterate_world()
    game.send_command_queue(__w)
