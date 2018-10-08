#!/usr/bin/env python3

import asyncio
from aiohttp import web
import logging

logging.basicConfig(level=logging.INFO)
game_started = False

# HTTP endpoint to start game (i.e. sets game_started as true)
async def start_game(request):
    global game_started
    game_started = True
    data = {'result' : 'Game started'}
    return web.json_response(data)


# one handler spawned per websocket /connect request
async def wshandler(request):
    app = request.app
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    app["sockets"].append(ws)

    while 1:
        msg = await ws.receive()
        if msg.tp == web.MsgType.text:
            print("Got message %s" % msg.data)
            handle_request(msg.data)
            ws.send_str("Echo: {}".format(msg.data))
        elif msg.tp == web.MsgType.close or\
             msg.tp == web.MsgType.error:
            break

    app["sockets"].remove(ws)
    print("Closed connection")
    return ws

# spawn on game board
# add their move queue to the dictionary
def add_player():

# handle player moves
def handle_request(str):




# This game loop will run infinitely and will send back a JSON string summarizing game state every second if game is active
async def game_loop(app):
    while 1:
        logging.info('Game loop iteration')
        for ws in app["sockets"]:
            ws.send_str("game loop says: tick")
        await asyncio.sleep(1)

app = web.Application()
app["sockets"] = []

asyncio.ensure_future(game_loop(app))

app.router.add_route('GET', '/connect', wshandler)
app.router.add_route('POST', '/startGame', start_game)


web.run_app(app)