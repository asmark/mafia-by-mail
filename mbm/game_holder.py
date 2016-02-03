import contextlib
import inspect
import json
import jsonschema
import pickle
import os
import shutil

import mafia.game

from . import async_filelock
from . import roles
from . import string


class Transaction(object):
    def __init__(self, path):
        self.path = path
        self.lock = GameHolder.lock(self.path)
        self.gh = None

    async def __aenter__(self):
        await self.lock.acquire()
        self.gh = GameHolder.load(self.path)
        return self.gh

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        if exc_value is None:
            self.gh.save(self.path)
        await self.lock.release()


class GameHolder(object):
    STATE_FILENAME = 'state'
    META_FILENAME = 'meta'
    LOCK_FILENAME = 'lock'

    SPEC_SCHEMA = {
        'type': 'object',
        'properties': {
            'players': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'email': {'type': 'string'},
                        'role': {'type': 'string'},
                        'flavored_role': {'type': 'string'},
                        'flavor_text': {'type': 'string'},
                    },
                    'required': ['name', 'email', 'role']
                }
            },
            'moderator_email': {'type': 'string'},
            'night_duration': {'type': 'number'},
            'day_duration': {'type': 'number'},
        },
        'required': ['night_duration', 'day_duration']
    }

    def __init__(self, meta, state):
        self.meta = meta
        self.state = state

    @classmethod
    def from_spec(cls, spec):
        jsonschema.validate(spec, cls.SPEC_SCHEMA)

        player_roles = [roles.ROLES[player_spec['role']]()
                        for player_spec in spec['players']]
        state = mafia.game.Game([role.player for role in player_roles])
        for role in player_roles:
            role.finish(state)

        players = dict(zip(state.players, spec['players']))

        return cls({
            'players': [{
                'name': player_spec['name'],
                'email': player_spec['email'],
                'role': player_spec['role'],
                'last_message_id': None,
                'flavored_role': player_spec.get(
                    'flavored_role', player_spec['role']),
                'flavor_text': player_spec.get(
                    'flavor_text', role.describe(players))
            } for role, player_spec in zip(player_roles, spec['players'])],
            'night_duration': spec['night_duration'],
            'day_duration': spec['day_duration'],
            'moderator_email': spec.get('moderator_email'),
            'last_message_id': None,
        }, state)

    @classmethod
    def load(cls, path):
        with open(os.path.join(path, cls.META_FILENAME), 'r') as f:
            meta = json.load(f)

        with open(os.path.join(path, cls.STATE_FILENAME), 'rb') as f:
            state = pickle.load(f)

        return cls(meta, state)

    def save(self, path):
        if not os.path.exists(path):
            os.mkdir(path)

        with open(os.path.join(path, self.META_FILENAME), 'w') as f:
            json.dump(self.meta, f)

        with open(os.path.join(path, self.STATE_FILENAME), 'wb') as f:
            pickle.dump(self.state, f)

    @classmethod
    def lock(cls, path):
        return async_filelock.FileLock(os.path.join(path, cls.LOCK_FILENAME))

    @classmethod
    def transaction(cls, path):
        return Transaction(path)

    @classmethod
    def destroy(cls, path):
        with cls.lock(path):
            shutil.rmtree(path)


class Store(object):
    def __init__(self, root):
        self.root = root

    def _get_path(self, id):
        return os.path.join(self.root, id)

    def create(self, id, spec):
        os.mkdir(os.path.join(self.root, id))

        gh = GameHolder.from_spec(spec)
        gh.save(self._get_path(id))

    def transaction(self, id):
        return GameHolder.transaction(self._get_path(id))

    def list(self):
        return os.listdir(self.root)
