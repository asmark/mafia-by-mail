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

from mafia import game
from mafia import invalidities


async def new_game(request):
    if request.GET.get('key') != request.app['config']['serve']['key']:
        return web.json_response({'error': 'bad new game request'}, status=403)

    id = uuid.uuid4().hex
    print("New game! " + id)
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

    async with request.app['store'].transaction(id) as gh:
        players = dict(zip(gh.state.players, gh.meta['players']))
        lower_player_mapping = dict(
            zip((player_spec['name'].lower()
                 for player_spec in gh.meta['players']), gh.state.players))

        player = next(player for player, player_spec in players.items()
                      if player_spec['email'].lower() == post['sender'])
        player_spec = players[player]


        if gh.state.turn.phase == game.Phase.NIGHT:
            await handle_night(gh, id, request, player, player_spec, players,
                               lower_player_mapping)
        elif gh.state.turn.phase == game.Phase.DAY:
            await handle_day(gh, id, request, player, player_spec, players,
                             lower_player_mapping)

    return web.Response()


async def handle_night(gh, id, request, player, player_spec, players,
                       lower_player_mapping):
    plan = gh.state.turn.get_plan()

    post = await request.post()
    commands = [re.sub(r'\s+', ' ', line.strip()).lower()
                for line in post['stripped-text'].split('\n')]
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
            commands=commands, results=results),
        reply=True)


async def handle_day(gh, id, request, player, player_spec, players,
                     lower_player_mapping):
    ballot = gh.state.turn.get_ballot()

    post = await request.post()
    text = re.sub(r'\s+', ' ', post['stripped-text']).strip().lower()

    if text == 'retract':
        ballot.retract(player)
        votee = None

        await mail_templates.send_private(
            request.app['mail'], gh, id, player_spec,
            "You retracted your vote.", reply=True)
    else:
        match = re.match(r'vote (?P<name>.+?)$', text)
        if match is None:
            await mail_templates.send_private(
                request.app['mail'], gh, id, player_spec,
                "No idea what you wanted."
                "Try **vote _player_** or **retract**?",
                reply=True
            return

        try:
            votee = lower_player_mapping[match.group('name')]
        except KeyError:
            await mail_templates.send_private(
                request.app['mail'], gh, id, player_spec,
                "Couldn't find a player called '{}'.".format(
                    match.group('name')),
                reply=True)
            return

        try:
            ballot.vote(player, votee)
        except invalidities.Invalidity as e:
            await mail_templates.send_private(
                request.app['mail'], gh, id, player_spec,
                "Could not vote for {}: {}".format(players[votee]['name'],
                                                   str(e)),
                reply=True)
            return

        await mail_templates.send_private(
            request.app['mail'], gh, id, player_spec,
            "You cast your vote for **{}**.".format(players[votee]['name']),
            reply=True)

    await mail_templates.send_public(
        request.app['mail'], gh, id,
        request.app['mako'].get_template('vote.mako').render(
            gh=gh, player_spec=player_spec, player=player, players=players,
            ballot=ballot, votee=votee))
