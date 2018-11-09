#!/usr/bin/env python3

import asyncio
import websockets
import json

async def happy_path():
    async with websockets.connect(
            'ws://35.183.103.104:8080/connect') as websocket:
        await websocket.send("DONG")
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
        data = {"team_id": 2, "authenticationKey": "team2key", "type": "MOVE",
                "message": "LEFT"}
        await websocket.send(json.dumps(data))
        data = {"team_id": 2, "authenticationKey": "team2key", "type": "MOVE",
                "message": "LEFT"}
        await websocket.send(json.dumps(data))
        data = {"team_id": 2, "authenticationKey": "team2key", "type": "MOVE",
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