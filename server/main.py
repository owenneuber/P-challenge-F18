#!/usr/bin/env python3

import asyncio
import aiohttp
from aiohttp import web
import json
import logging

GAME_LOOP_INTERVAL_IN_SECONDS = 3

logging.basicConfig(level=logging.INFO)
game_started = False

# HTTP endpoint to start game (i.e. sets game_started as true)
async def start_game(request):
    global game_started
    game_started = True
    logging.info("Starting game")
    data = {'Result' : 'Game started'}
    return web.json_response(data)

async def stop_game(request):
    global game_started
    game_started = False
    logging.info("Stopping game")
    data = {"Result" : "Game stopped"}
    # TODO: reset everything - close conns, reset game state, etc.
    return web.json_response(data)

# one handler spawned per websocket /connect request
async def wshandler(request):
    app = request.app
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    app["sockets"].append(ws)

    # If game is in progress, close connection (do not accept new conns)
    if game_started == True:
        await ws.send_str("Game in progress, connection rejected")
        app["sockets"].remove(ws)
        logging.debug("Closing connection since game is already in progress")
        return ws

    while 1:
        msg = await ws.receive()
        print(msg)
        if msg.type == aiohttp.WSMsgType.TEXT:
            logging.debug("Received message %s" % msg.data)
            handle_request(msg.data)
            # TODO: Ideally, we send back some sort of response confirming appropriate handling of the request or
            # return some sort of message that indicates a malformed request
            await ws.send_str("Echo: {}".format(msg.data))
        elif msg.type == aiohttp.WSMsgType.CLOSE or\
            msg.type == aiohttp.WSMsgType.ERROR:
                break

    app["sockets"].remove(ws)
    # TODO: Maybe some more verbose logging upon disconnect (assuming it's accidental)
    logging.debug("Closed connection")
    return ws

# TODO: spawn the player on game board
# TODO: add their move queue to the dictionary
def add_player():
    a = 1

# TODO: handle player moves (assess validity, etc.) if game has started
def handle_request(str):
    a = 1

# TODO: should return a JSON-format string containing the game grid along with positions of walls and players

def get_json_serialized_game_state():
    return 'asdf'

# This game loop will run infinitely and will periodically send back a JSON string summarizing game state if game is active
async def game_loop(app):
    while 1:
        for ws in app["sockets"]:
            logging.info('Sending game state')
            await ws.send_str(get_json_serialized_game_state())
        # TODO: iterate through players and check if dead.  If so, report death to corresponding client and perform cleanup.

        # TODO: if game is over, persist results somewhere
        await asyncio.sleep(GAME_LOOP_INTERVAL_IN_SECONDS)

app = web.Application()

# a list of all the active socket connections
app["sockets"] = []

# a dictionary of id - move queue pairs
move_queue_dict = {}

asyncio.ensure_future(game_loop(app))

# TODO: Routes should be authenticated somehow
app.router.add_route('GET', '/connect', wshandler)
app.router.add_route('GET', '/startGame', start_game)
app.router.add_route('GET', '/stopGame', stop_game)


web.run_app(app)