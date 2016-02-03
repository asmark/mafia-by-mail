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
    def __init__(self, maker, *args, **kwargs):
        self.maker = maker
        self.player = maker(*args, **kwargs)

    def describe(self, players):
        return string.reformat_lines(inspect.getdoc(self.maker))


def SR(*args, **kwargs):
    return functools.partial(SimpleRole, *args, **kwargs)


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
    'Cult Leader': SR(roles.cult_leader),
    'Lyncher': Lyncher,
}

for suffix, maker in {
    'Cop': roles.cop,
    'Doctor': roles.doctor,
    'Roleblocker': roles.roleblocker,
    'Bus Driver': roles.bus_driver,
    'Suicidal': roles.suicidal,
    'Vigilante': roles.vigilante,
    'Forensic Investigator': roles.forensic_investigator,
    'Commuter': roles.commuter,
    'Watcher': roles.watcher,
    'Tracker': roles.tracker,
    'Bodyguard': roles.bodyguard,
    'Jester': roles.jester,
    'Double Voter': roles.double_voter,
    'Vote Thief': roles.vote_thief,
    'Redirector': roles.redirector,
    'Deflector': roles.deflector,
    'Hider': roles.hider,
    'Jailkeeper': roles.jailkeeper,
}.items():
    ROLES['Town ' + suffix] = SR(maker)
    ROLES['Mafia ' + suffix] = SR(maker, faction=factions.DEFAULT_MAFIA)
