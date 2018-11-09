#!/usr/bin/env python3

import asyncio
import websockets
import json

async def happy_path():
    async with websockets.connect(
            'ws://35.183.103.104:8080/connect') as websocket:
        authenticationKey = "team1key"
        data = {"team_id":1,"authenticationKey":authenticationKey,"type":"REGISTRATION","message":""}
        await websocket.send(json.dumps(data))
        count = 0
        while(1):
            msg = await websocket.recv()
            count += 1
            print ('Received: ' + msg)
            if count > 1:
                data = {"team_id": 1, "authenticationKey": authenticationKey, "type": "MOVE",
                    "message": "RIGHT"}
                await websocket.send(json.dumps(data))
                await asyncio.sleep(3)

asyncio.get_event_loop().run_until_complete(happy_path())