import functools

from mafia import infos


@functools.singledispatch
def show(info, players):
    raise TypeError('unknown info type')


@show.register(infos.Investigation)
def show_investigation(info, players):
    return 'Investigation reveals alignment: **{}**.'.format(
        info.alignment.name.lower())


@show.register(infos.Autopsy)
def show_autopsy(info, players):
    return 'Autopsy reveals targeted by: {}.'.format(
        ', '.join('**' + players[targeter]['name'] + '**'
                  for targeter in info.targeters))


@show.register(infos.Watch)
def show_watch(info, players):
    return 'Watch reveals visited by: {}'.format(
        ', '.join('**' + players[visitor]['name'] + '**'
                  for visitor in info.visitors))


@show.register(infos.Trace)
def show_trace(info, players):
    return 'Trace reveals visited: **{}**.'.format(
        players[info.visited]['name'])
