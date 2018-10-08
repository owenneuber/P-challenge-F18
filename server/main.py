#!/usr/bin/env python3

import asyncio
from aiohttp import web
import logging

GAME_LOOP_INTERVAL_IN_SECONDS = 3

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
    # if game is in progress, close connection (do not accept new conns)
    app = request.app
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    app["sockets"].append(ws)

    while 1:
        msg = await ws.receive()
        if msg.tp == web.MsgType.text:
            logging.debug("Received message %s" % msg.data)
            handle_request(msg.data)
            # Ideally, we send back some sort of response confirming appropriate handling of the request or
            # return some sort of message that indicates a malformed request
            ws.send_str("Echo: {}".format(msg.data))
        elif msg.tp == web.MsgType.close or\
            msg.tp == web.MsgType.error:
                break

    app["sockets"].remove(ws)
    # Maybe some more verbose logging upon disconnect (assuming it's accidental)
    print("Closed connection")
    return ws

# spawn the player on game board
# add their move queue to the dictionary
def add_player():

# handle player moves (assess validity, etc.) if game has started
def handle_request(str):


# should return a JSON-format string containing the game grid along with positions of
# walls and other players
def get_json_serialized_game_state():


# This game loop will run infinitely and will periodically send back a JSON string summarizing game state if game is active
async def game_loop(app):
    while 1:
        logging.info('Game loop iteration')
        for ws in app["sockets"]:
            ws.send_str(get_json_serialized_game_state())
        # iterate through players and check if dead.  If so, report death to corresponding client and perform cleanup.

        # if game is over, persist results somewhere
        await asyncio.sleep(GAME_LOOP_INTERVAL_IN_SECONDS)

app = web.Application()
# a list of all the active socket connections
app["sockets"] = []

asyncio.ensure_future(game_loop(app))

app.router.add_route('GET', '/connect', wshandler)

# probably need some sort of auth (shitty secret-based auth?)
app.router.add_route('POST', '/startGame', start_game)


web.run_app(app)