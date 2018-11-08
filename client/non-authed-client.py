#!/usr/bin/env python3

import asyncio
import websockets
from time import sleep
import json

# Should automatically disconnect
async def invalid_messages():
    async with websockets.connect(
            'ws://localhost:8080/connect') as websocket:
        data = {"team_id":2,"authenticationKey":"invalidkey","type":"REGISTRATION","message":""}
        await websocket.send(json.dumps(data))
        data = {"team_id":2, "authenticationKey": "invalidkey", "type": "MOVE", "message": "LEFT"}
        await websocket.send(json.dumps(data))
        while(1):
            msg = await websocket.recv()
            print ('Received: %s' % msg)
            sleep(1)


asyncio.get_event_loop().run_until_complete(invalid_messages())