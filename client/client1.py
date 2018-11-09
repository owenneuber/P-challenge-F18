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
        for i in range(1,13):
            data = {"team_id":1, "authenticationKey": authenticationKey, "type": "MOVE",
                    "message": "RIGHT"}
            await websocket.send(json.dumps(data))
        await websocket.send(json.dumps(data))
        while(1):
            msg = await websocket.recv()
            print ('Received: ' + msg)

asyncio.get_event_loop().run_until_complete(happy_path())