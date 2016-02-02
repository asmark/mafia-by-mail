import asyncio
from aiohttp import web
import functools
import os
import toml

from . import game_holder
from . import handlers
from . import mail


async def init(config, loop, port=8080, host='127.0.0.1'):
    app = web.Application(loop=loop)
    store = game_holder.Store(os.path.join(os.path.dirname(__name__),
                                           'games'))
    app['store'] = store
    app['mail'] = mail.Mailgun(config['mailgun']['domain'],
                               config['mailgun']['api_key'])

    app.router.add_route('POST', '/new_game', handlers.new_game)
    app.router.add_route('POST', '/process_mail', handlers.process_mail)

    srv = await loop.create_server(app.make_handler(), host, port)
    return srv


if __name__ == '__main__':
    with open('config.toml', 'rb') as f:
        config = toml.load(f)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(config, loop))
    loop.run_forever()
