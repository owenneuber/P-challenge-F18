#!/usr/bin/env python3

import asyncio
import websockets
from time import sleep
import json

async def happy_path():
    async with websockets.connect(
            'ws://localhost:8080/connect') as websocket:
        data = {"team_id":2,"authenticationKey":"team2key","type":"REGISTRATION","message":""}
        await websocket.send(json.dumps(data))
        data = {"team_id":2, "authenticationKey": "team2key", "type": "MOVE",
                "message": "LEFT"}
        await websocket.send(json.dumps(data))
        data = {"team_id":2, "authenticationKey": "team2key", "type": "MOVE",
                "message": "LEFT"}
        await websocket.send(json.dumps(data))
        data = {"team_id":2, "authenticationKey": "team2key", "type": "MOVE",
                "message": "DOWN"}
        await websocket.send(json.dumps(data))
        data = {"team_id":2, "authenticationKey": "team2key", "type": "MOVE",
                "message": "LEFT"}
        await websocket.send(json.dumps(data))
        data = {"team_id": 2, "authenticationKey": "team2key", "type": "MOVE",
                "message": "LEFT"}
        await websocket.send(json.dumps(data))
        data = {"team_id": 2, "authenticationKey": "team2key", "type": "MOVE",
                "message": "LEFT"}
        await websocket.send(json.dumps(data))
        while(1):
            msg = await websocket.recv()
            print ('Received: ' + msg)

asyncio.get_event_loop().run_until_complete(happy_path())