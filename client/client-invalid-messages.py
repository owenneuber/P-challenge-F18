#!/usr/bin/env python3

# we should have some util functions for testing websocket stuff

import asyncio
import websockets
from time import sleep
import json

async def invalid_messages():
    async with websockets.connect(
            'ws://localhost:8080/connect') as websocket:
        data = {"team_id":2,"authenticationKey":"team2key","type":"REGISTRATION","message":""}
        await websocket.send(json.dumps(data))
        # Missing message
        data = {"team_id": 2, "authenticationKey": "team2key", "type": "MOVE"}
        await websocket.send(json.dumps(data))

        # Invalid type
        data = {"team_id":2, "authenticationKey": "team2key", "type": "INVALID-TYPE",
                "message": "LEFT"}
        await websocket.send(json.dumps(data))

        # Invalid move
        data = {"team_id":2, "authenticationKey": "team2key", "type": "MOVE",
                "message": "INVALID-MOVE"}
        await websocket.send(json.dumps(data))
        while(1):
            msg = await websocket.recv()
            print ('Received: ' + msg)
            sleep(1)


asyncio.get_event_loop().run_until_complete(invalid_messages())