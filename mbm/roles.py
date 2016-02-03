import functools
import random
import inspect

from . import string

from mafia import factions
from mafia import roles


class Role(object):
    def finish(self, game):
        pass

    def describe(self, players):
        pass


class SimpleRole(Role):
    def __init__(self, maker):
        self.maker = maker
        self.player = maker()

    def describe(self, players):
        return string.reformat_lines(inspect.getdoc(self.maker))


def SR(maker):
    return functools.partial(SimpleRole, maker)


class Lyncher(Role):
    def __init__(self):
        self.faction = factions.Lyncher(None)
        self.player = roles.with_faction(self.faction, [], [])

    def finish(self, game):
        self.faction.target = random.choice([
            player for player in game.players if player is not self.player])

    def describe(self, players):
        return string.reformat_lines(inspect.getdoc(roles.lyncher)) + \
            ' Your target is **{}**.'.format(
                players[self.faction.target]['name'])



ROLES = {
    'Mafia Goon': SR(roles.goon),
    'Vanilla Townie': SR(roles.vanilla),
    'Mafia Godfather': SR(roles.godfather),
    'Town Cop': SR(roles.cop),
    'Town Doctor': SR(roles.doctor),
    'Town Roleblocker': SR(roles.roleblocker),
    'Town Bus Driver': SR(roles.bus_driver),
    'Town Suicidal': SR(roles.suicidal),
    'Town Vigilante': SR(roles.vigilante),
    'Town Forensic Investigator': SR(roles.forensic_investigator),
    'Town Commuter': SR(roles.commuter),
    'Town Watcher': SR(roles.watcher),
    'Town Tracker': SR(roles.tracker),
    'Town Bodyguard': SR(roles.bodyguard),
    'Town Jester': SR(roles.jester),
    'Town Double Voter': SR(roles.double_voter),
    'Cult Leader': SR(roles.cult_leader),
    'Town Vote Thief': SR(roles.vote_thief),
    'Town Redirector': SR(roles.redirector),
    'Town Deflector': SR(roles.deflector),
    'Town Hider': SR(roles.hider),
    'Town Jailkeeper': SR(roles.jailkeeper),
    'Lyncher': Lyncher,
}
