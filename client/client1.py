#!/usr/bin/env python3

import asyncio
import websockets
from time import sleep
import json

async def happy_path():
    async with websockets.connect(
            'ws://localhost:8080/connect') as websocket:
        authenticationKey = "a23c186a29d5b65e6e27dcac9f50c4ad2fb95a1a"
        data = {"team_id":1,"authenticationKey":authenticationKey,"type":"REGISTRATION","message":""}
        await websocket.send(json.dumps(data))
        data = {"team_id":1, "authenticationKey":authenticationKey, "type": "MOVE",
                "message": "RIGHT"}
        await websocket.send(json.dumps(data))
        data = {"team_id":1, "authenticationKey":authenticationKey, "type": "MOVE",
                "message": "RIGHT"}
        await websocket.send(json.dumps(data))
        data = {"team_id":1, "authenticationKey":authenticationKey, "type": "MOVE",
                "message": "Right"}
        await websocket.send(json.dumps(data))
        data = {"team_id":1, "authenticationKey":authenticationKey, "type": "MOVE",
                "message": "right"}
        await websocket.send(json.dumps(data))
        data = {"team_id":1, "authenticationKey":authenticationKey, "type": "MOVE",
                "message": "Right"}
        await websocket.send(json.dumps(data))
        data = {"team_id":1, "authenticationKey":authenticationKey, "type": "MOVE",
                "message": "Right"}
        await websocket.send(json.dumps(data))
        while(1):
            msg = await websocket.recv()
            print ('Received: ' + msg)

asyncio.get_event_loop().run_until_complete(happy_path())