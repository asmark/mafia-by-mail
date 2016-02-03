from aiohttp import web
import hashlib
import hmac
import inspect
import itertools
import jsonschema
import re
import uuid

from . import actions
from . import mail_templates
from . import string
from . import tasks

from mafia import invalidities


async def new_game(request):
    id = uuid.uuid4().hex
    try:
        request.app['store'].create(id, await request.json())
    except jsonschema.exceptions.ValidationError as e:
        return web.json_response({'error': e.message}, status=400)

    async with request.app['store'].transaction(id) as gh:
        players = dict(zip(gh.state.players, gh.meta['players']))
        mails = []

        for player, player_spec in players.items():
            text = request.app['mako'].get_template('role.mako').render(
                player_spec=player_spec, player=player, players=players, gh=gh)

            mails.append(text)
            await mail_templates.send_private(request.app['mail'], gh, id,
                                              player_spec, text)

        await mail_templates.send_public(
            request.app['mail'], gh, id,
            request.app['mako'].get_template('welcome.mako').render(
                gh=gh, players=players))

        if gh.meta['moderator_email'] is not None:
            await mail_templates.send_moderator(
                request.app['mail'], gh, id,
                request.app['mako'].get_template(
                    'moderator_welcome.mako').render(mails=mails))

        gh.state.next_turn()
        tasks.end_night.apply_async((id,), countdown=gh.meta['night_duration'])
        return web.json_response(gh.meta)


async def process_mail(request):
    post = await request.post()

    if hmac.new(request.app['mail'].api_key.encode('utf-8'),
                (post['timestamp'] + post['token']).encode('utf-8'),
                digestmod=hashlib.sha256).hexdigest() != post['signature']:
        return web.json_response({'error': 'bad webhook request'}, status=403)

    id = request.GET['id']
    commands = [re.sub(r'\s+', ' ', line.strip()).lower()
                for line in post['stripped-text'].split('\n')]

    # TODO: votes

    async with request.app['store'].transaction(id) as gh:
        plan = gh.state.turn.get_plan()

        players = dict(zip(gh.state.players, gh.meta['players']))
        lower_player_mapping = dict(
            zip((player_spec['name'].lower()
                 for player_spec in gh.meta['players']), gh.state.players))

        player = next(player for player, player_spec in players.items()
                      if player_spec['email'].lower() == post['sender'])
        player_spec = players[player]

        results = []

        for action, command in itertools.zip_longest(
            player.actions, commands, fillvalue=None):
            if action is None:
                results.append("There aren't that many actions to perform.")
                continue

            if command is None:
                results.append('Missing details for this action; ignoring.')
                continue

            template = actions.COMMANDS[action.__class__]

            if command == 'ignore':
                results.append('Ignoring.')
                continue
            elif command == 'cancel':
                results.append('Cancelling.')
                plan.dequeue(action, player)
                continue

            expr = template.substitute_with_name(
                lambda name: r'(?P<{name}>.+?)'.format(name=name)) + '$'
            match = re.match(expr, command)

            if match is None:
                results.append('Not of the form: {}'.format(
                    template.substitute_with_name(
                        lambda name: '_' + name + '_')))
                continue

            targets = {}
            for slot, name in match.groupdict().items():
                try:
                    targets[slot] = lower_player_mapping[name]
                except KeyError:
                    results.append("Couldn't find a player called '{}'".format(
                        name))
                    continue

            ordering = list(action.TARGET_SELECTORS.keys())
            targets = [target for _, target in sorted(
                targets.items(), key=lambda kv: ordering.index(kv[0]))]

            try:
                plan.queue(action, player, *targets)
            except invalidities.Invalidity as e:
                results.append(string.reformat_lines(inspect.getdoc(e)))

            results.append('Okay, planned.')

        await mail_templates.send_private(
            request.app['mail'], gh, id, player_spec,
            request.app['mako'].get_template('night_action.mako').render(
                gh=gh, player=player, players=players, plan=plan,
                commands=commands, results=results))

        return web.Response()
