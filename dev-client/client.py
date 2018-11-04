#!/usr/bin/env python3

# we should have some util functions for testing websocket stuff

import asyncio
import websockets
from time import sleep
import json

# A shitty function that pings the server on loop

async def infinite_pinger():
    async with websockets.connect(
            'ws://localhost:8080/connect') as websocket:
        data = {"team_id":1,"authenticationKey":"c3f2a2ea7adf31cbd1809c9439408f0141f24cb6","type":"REGISTRATION","message":"",}
        await websocket.send(json.dumps(data))
        sleep(1)
        while(1):
            data = {"team_id":1,"authenticationKey":"c3f2a2ea7adf31cbd1809c9439408f0141f24cb6","type":"MOVE","message":"RIGHT",}
            # the above is valid for my local database, change for yours as needed
            await websocket.send(json.dumps(data))
            msg = await websocket.recv()
            print ('Received: ' + msg)
            sleep(1)


asyncio.get_event_loop().run_until_complete(infinite_pinger())