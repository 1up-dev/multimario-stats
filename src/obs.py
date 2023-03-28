import websockets
import asyncio
import json

# Interfaces with OBS using obs-websocket
# defined here: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md

host = "localhost"
port = "4455"

def request(req_name):
    asyncio.run(req(req_name))

async def req(req_name):
    async with websockets.connect(f"ws://{host}:{port}") as ws:
        r = await ws.recv()
        # print(r)
        identify = {"op": 1,"d": {"rpcVersion": 1}}
        await ws.send(json.dumps(identify))
        r = await ws.recv()
        # print(r)
        request = {"op": 6, "d": {"requestType": req_name, 
                "requestId": "1"}}
        await ws.send(json.dumps(request))
        r = await ws.recv()
        # print(r)
