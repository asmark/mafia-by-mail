import uuid


async def new_game(request):
    id = uuid.uuid4().hex
    store.create(id, await request.json())
    with request.app['store'].transaction(id) as gh:
        for player_spec in gh.meta['players']:
            pass

        return web.json_response(gh.meta)


async def process_mail(store, request):
    pass
