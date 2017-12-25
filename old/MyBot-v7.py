import hlt
import logging
from hlt.entity import Position


game = hlt.Game("AM-Random-7")


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


def sort_planets(planets, ship):
    _p = sorted(planets, key=lambda x: dest(ship, x))
    return _p



def action_for_ship(ship, planets, game_map):

    # try to dock at any own planet immediately
    for planet in sort_planets(planets["own"], ship):
        # dock is planet is not full
        if ship.can_dock(planet) and not planet.is_full():
            return ship.dock(planet)

    # settle unowned planets next
    for planet in sort_planets(planets["unowned"], ship):
        # dock unowned planet or navigate to it
        if ship.can_dock(planet):
            return ship.dock(planet)
        action = navigate_planet(ship, planet, game_map)
        if action:
            return action

    for planet in sort_planets(planets["enemy"], ship):
        action = attack_planet(ship, planet, game_map)
        if action:
            return action

    logging.warning("Nothing worked for ship %s" % ship.id)
    return None


def tag_plantes(planets, me):
    res = {
        "own": [],
        "unowned": [],
        "enemy": []
    }
    for planet in planets:
        if planet.owner == me:
            res["own"].append(planet)
        elif planet.owner is None:
            res["unowned"].append(planet)
        else:
            res["enemy"].append(planet)

    return res

def iterate_world():
    game_map = game.update_map()
    cmd = []

    planets = list((game_map.all_planets()))
    me = game_map.get_me()
    ships = filter(lambda x: x.docking_status == x.DockingStatus.UNDOCKED,
                   me.all_ships())

    ships = list(ships)[:30]  # hard limit

    for ship in ships:
        tp = tag_plantes(planets, me)
        a = action_for_ship(ship, tp, game_map)
        if a:
            cmd.append(a)
    return cmd


logging.info("Starting my AM-Random bot!")
while True:
    c = iterate_world()
    game.send_command_queue(c)
