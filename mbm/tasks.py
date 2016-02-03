import asyncio
import functools

from . import app
from . import celery
from . import mail_templates


services = app.make_services(app.read_config())


def make_sync(f):
    @functools.wraps(f)
    def _wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(f(*args, **kwargs))
    return _wrapper


@celery.app.task
@make_sync
async def end_night(id):
    async with services['store'].transaction(id) as gh:
        turn_number = gh.state.turn.number

        alive = set(gh.state.get_alive_players())
        gh.state.turn.run_plan()
        deaths = alive - set(gh.state.get_alive_players())

        players = dict(zip(gh.state.players, gh.meta['players']))

        for player, player_spec in players.items():
            await mail_templates.send_private(
                services['mail'], gh, id, player_spec,
                services['mako'].get_template('end_night_private.mako').render(
                    gh=gh, player=player, players=players))

        await mail_templates.send_public(
            services['mail'], gh, id,
            services['mako'].get_template('end_night.mako').render(
                gh=gh, turn_number=turn_number, deaths=deaths,
                players=players))

        if not gh.state.is_over():
            end_day.apply_async((id,), countdown=gh.meta['day_duration'])


@celery.app.task
@make_sync
async def end_day(id):
    async with services['store'].transaction(id) as gh:
        turn_number = gh.state.turn.number

        ballot = gh.state.turn.get_ballot()
        gh.state.turn.run_ballot()
        gh.state.next_turn()

        players = dict(zip(gh.state.players, gh.meta['players']))

        await mail_templates.send_public(
            services['mail'], gh, id,
            services['mako'].get_template('end_day.mako').render(
                gh=gh, turn_number=turn_number,
                players=players, ballot=ballot))

        if not gh.state.is_over():
            end_night.apply_async((id,), countdown=gh.meta['night_duration'])
