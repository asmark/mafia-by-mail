import ago
from aiohttp import web
import datetime
import inspect
import jsonschema
import uuid

from . import actions
from . import mail
from . import string
from . import tasks


async def new_game(request):
    id = uuid.uuid4().hex
    try:
        request.app['store'].create(id, await request.json())
    except jsonschema.exceptions.ValidationError as e:
        return web.json_response({'error': e.message}, status=400)

    with request.app['store'].transaction(id) as gh:
        players = dict(zip(gh.state.players, gh.meta['players']))
        mails = []

        for player, player_spec in players.items():
            faction_friends = player.get_faction().get_friends(gh.state)

            text = request.app['mako'].get_template('role.mako').render(
                player_spec=player_spec,
                actions=[{
                    'action': action,
                    'placeholder': string.Template(
                        actions.COMMANDS[action.__class__])
                        .substitute_with_name(lambda name: '_' + name + '_'),
                    'description': string.reformat_lines(
                        inspect.getdoc(action)),
                } for action in player.actions],
                faction_friends=[players[friend]['name']
                                 for friend in faction_friends
                                 if players[friend]['name'] !=
                                     player_spec['name']]
                                 if faction_friends is not None
                                 else None,
                human_night_duration=ago.human(
                    datetime.timedelta(seconds=gh.meta['night_duration']),
                    past_tense='{}'))

            mails.append(text)

            await request.app['mail'].send(
                player_spec['email'],
                mail.make_markdown_email(text, {
                    'From': 'Mafia Game <game-{id}-private@{domain}>'.format(
                        id=id, domain=request.app['mail'].domain),
                    'To': '{name} <{email}>'.format(**player_spec),
                    'Subject': '{name}, Your Mafia Role'.format(**player_spec)
                }, extensions=['markdown.extensions.nl2br']))

        await request.app['mail'].send(
            [player_spec['email'] for player_spec in gh.meta['players']],
            mail.make_markdown_email(
                request.app['mako'].get_template('welcome.mako').render(), {
                'From': 'Mafia Game <game-{id}-public@{domain}>'.format(
                    id=id, domain=request.app['mail'].domain),
                'To': ', '.join('{name} <{email}>'.format(**player_spec)
                                for player_spec in gh.meta['players']),
                'Subject': 'Welcome to Mafia'
            }, extensions=['markdown.extensions.nl2br']))

        if gh.meta['moderator_email'] is not None:
            await request.app['mail'].send(
                gh.meta['moderator_email'],
                mail.make_markdown_email(
                    request.app['mako'].get_template(
                        'moderator_welcome.mako').render(mails=mails), {
                    'From': 'Mafia Game Moderator <game-{id}-mod@{domain}>'.format(
                        id=id, domain=request.app['mail'].domain),
                    'To': '{name} <{email}>'.format(**player_spec),
                    'Subject': 'Mafia Moderator Log'
                }, extensions=['markdown.extensions.nl2br']))

        gh.state.next_turn()
        tasks.end_night.apply_async((id,), countdown=gh.meta['night_duration'])
        return web.json_response(gh.meta)


async def process_mail(request):
    if request.GET.get('webhook_key') != \
        request.app['config']['mailgun']['webhook_key']:
        return web.json_response({'error': 'bad webhook key'}, status=403)
