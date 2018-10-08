#!/usr/bin/env python3

import asyncio
import aiohttp

async def wshandler(request):
    app = request.app
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    app["sockets"].append(ws)

    while 1:
        msg = await ws.receive()
        if msg.tp == web.MsgType.text:
            print("Got message %s" % msg.data)
            ws.send_str("Pressed key code: {}".format(msg.data))
        elif msg.tp == web.MsgType.close or\
             msg.tp == web.MsgType.error:
            break

    app["sockets"].remove(ws)
    print("Closed connection")
return ws


# This game loop will run infinitely and will send back a JSON string summarizing game state every second
async def game_loop(app):
    while 1:
        for ws in app["sockets"]:
            ws.send_str("game loop says: tick")
        await asyncio.sleep(1)