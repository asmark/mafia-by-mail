import asyncio
from aiohttp import web
import functools
import mako.lookup
import os
import toml

from . import game_holder
from . import handlers
from . import mail


def read_config():
    with open('config.toml', 'r') as f:
        return toml.load(f)


def make_services(config):
    return {
        'store': game_holder.Store(config['store']['path']),
        'mail': mail.Mailgun(config['mailgun']['domain'],
                             config['mailgun']['api_key']),
        'mako': mako.lookup.TemplateLookup(
            directories=[os.path.join(os.path.dirname(__file__), 'templates')])
    }


async def init(config, loop):
    app = web.Application(loop=loop)
    app.update(make_services(config))
    app['config'] = config

    app.router.add_route('POST', '/new_game', handlers.new_game)
    app.router.add_route('POST', '/process_mail', handlers.process_mail)

    return (await loop.create_server(app.make_handler(),
                                     config['serve']['host'],
                                     config['serve']['port']))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(read_config(), loop))
    loop.run_forever()
