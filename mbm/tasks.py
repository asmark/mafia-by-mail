from . import app
from . import celery
from . import mail


services = app.make_services(app.read_config())


@celery.app.task
def end_night(id):
    with services['store'].transaction(id) as gh:
        alive = set(gh.state.get_alive_players())
        gh.state.turn.run_plan()
        deaths = alive - set(gh.state.get_alive_players())

        players = dict(zip(gh.state.players, gh.meta['players']))

        for player, player_spec in players.items():
            messages = list(gh.state.turn.get_messages_for_player(player))
            if not messages:
                continue

            services['mail'].send(player_spec['email'])

        end_day.apply_async((id,), countdown=gh.meta['day_duration'])


@celery.app.task
def end_day(id):
    with services['store'].transaction(id) as gh:
        gh.state.turn.run_ballot()
        gh.state.next_turn()

        end_night.apply_async((id,), countdown=gh.meta['night_duration'])
