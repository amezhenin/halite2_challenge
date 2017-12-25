
import hlt
import logging
from hlt.entity import Position


game = hlt.Game("AM-Random-4")
logging.info("Starting my AM-Random-4 bot!")


def dest(a, b):
    x = a.x - b.x
    y = a.y - b.y
    return (x * x) + (y * y)


def navigate_planet(ship, planet, game_map):
    c = None
    speed = int(hlt.constants.MAX_SPEED)
    while speed:
        c = ship.navigate(
            ship.closest_point_to(planet),
            game_map,
            speed=speed,
            ignore_ships=False)
        if c:
            logging.info("Navigating to planet %s with ship %s" % (planet.id, ship.id))
            return c
        speed -= 1

    logging.warning("Couldn't navigate planet %s with ship %s" % (planet.id, ship.id))
    return c


def attack_planet(ship, planet, game_map):
    p = Position(planet.x, planet.y)
    c = None
    speed = int(hlt.constants.MAX_SPEED)
    while speed > 0:
        c = ship.navigate(
            p,
            game_map,
            speed=speed,
            ignore_ships=True,
            ignore_planets=True)
        if c:
            return c
        speed -= 1
    logging.warning("Couldn't attack planet %s with ship %s" % (planet.id, ship.id))
    return c



def action_for_ship(ship, planets, me, game_map):

    # try to dock at any own planet immediately
    for planet in planets:
        if planet.owner == me:
            # dock is planet is not full
            if ship.can_dock(planet) and not planet.is_full():
                return ship.dock(planet)

    # settle unowned planets next
    for planet in planets:
        logging.info(planet.owner)
        if planet.owner is None:
            # dock unowned planet or navigate to it
            if ship.can_dock(planet):
                return ship.dock(planet)
            logging.info("Trying to navigate planet %s with ship %s" % (planet.id, ship.id))
            action = navigate_planet(ship, planet, game_map)
            if action:
                return action

    for planet in planets:
        if planet.owner != me:
            action = attack_planet(ship, planet, game_map)
            if action:
                return action
    logging.warning("Nothing worked for ship %s" % ship.id)
    return None


def iterate_world():
    game_map = game.update_map()
    cmd = []

    planets = list((game_map.all_planets()))
    me = game_map.get_me()
    ships = filter(lambda x: x.docking_status == x.DockingStatus.UNDOCKED,
                   me.all_ships())

    for ship in ships:
        _p = sorted(planets, key=lambda x: dest(ship, x))
        # _ids = list(map(lambda x: x.id, _p))
        # logging.warning("IDS <<<<<<<<<: %s" % str(_ids))
        a = action_for_ship(ship, _p, me, game_map)
        if a:
            cmd.append(a)
    return cmd


while True:
    c = iterate_world()
    game.send_command_queue(c)
