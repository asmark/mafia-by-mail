import ago
from aiohttp import web
import datetime
import inspect
import jsonschema
import uuid

from . import actions
from . import mail
from . import string


async def new_game(request):
    id = uuid.uuid4().hex
    try:
        request.app['store'].create(id, await request.json())
    except jsonschema.exceptions.ValidationError as e:
        return web.json_response({'error': e.message}, status=400)

    with request.app['store'].transaction(id) as gh:
        players = dict(zip(gh.state.players, gh.meta['players']))

        for player, player_spec in players.items():
            text = request.app['mako'].get_template('welcome.mako').render(
                player_spec=player_spec,
                player_specs=[other_player_spec
                              for other_player_spec in gh.meta['players']
                              if other_player_spec['name'] !=
                                  player_spec['name']],
                actions=[{
                    'action': action,
                    'placeholder': string.Template(
                        actions.COMMANDS[action.__class__])
                        .substitute_with_name(lambda name: '_' + name + '_'),
                    'description': string.reformat_lines(
                        inspect.getdoc(action)),
                } for action in player.actions],
                faction_friends=[players[friend]['name']
                                 for friend in player.get_faction()
                                 .get_friends(gh.state)
                                 if players[friend]['name'] !=
                                     player_spec['name']],
                human_night_duration=ago.human(
                    datetime.timedelta(seconds=gh.meta['night_duration']),
                    past_tense='{}'))
            await request.app['mail'].send(
                player_spec['email'],
                mail.make_markdown_email(text, {
                    'From': 'Mafia Game <game-{id}@{domain}>'.format(
                        id=id, domain=request.app['mail'].domain),
                    'To': '{name} <{email}>'.format(**player_spec)
                }, extensions=['markdown.extensions.nl2br']))

        return web.json_response(gh.meta)


async def process_mail(store, request):
    pass
