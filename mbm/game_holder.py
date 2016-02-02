import contextlib
import fasteners
import inspect
import json
import jsonschema
import pickle
import os
import shutil

import mafia.game

from . import roles
from . import string


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

        state = mafia.game.Game([roles.ROLES[player_spec['role']]()
                                 for player_spec in spec['players']])

        return cls({
            'players': [{
                'name': player_spec['name'],
                'email': player_spec['email'],
                'role': player_spec['role'],
                'flavored_role': player_spec.get(
                    'flavored_role', player_spec['role']),
                'flavor_text': player_spec.get(
                    'flavor_text',
                    string.reformat_lines(
                        inspect.getdoc(roles.ROLES[player_spec['role']])))
            } for player_spec in spec['players']],
            'night_duration': spec['night_duration'],
            'day_duration': spec['day_duration'],
            'moderator_email': spec.get('moderator_email'),
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
        return fasteners.InterProcessLock(os.path.join(path,
                                                       cls.LOCK_FILENAME))

    @classmethod
    @contextlib.contextmanager
    def transaction(cls, path):
        with cls.lock(path):
            gh = cls.load(path)
            yield gh
            gh.save(path)

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
