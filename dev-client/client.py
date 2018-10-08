#!/usr/bin/env python3

# we should have some util functions for testing websocket stuff

import asyncio
import websockets
from time import sleep

# A shitty function that pings the server on loop

async def infinite_pinger():
    async with websockets.connect(
            'ws://localhost:8080/connect') as websocket:
        while(1):
            await websocket.send('ping')
            sleep(1)


asyncio.get_event_loop().run_until_complete(infinite_pinger())