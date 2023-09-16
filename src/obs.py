import websockets
import asyncio
import json
import threading

# Interfaces with OBS using obs-websocket
# defined here: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md

host = "localhost"
port = "4455"

def request(req_name):
    # run the request in a thread so execution does not freeze while waiting for it to finish or fail
    t = threading.Thread(target=run_req, args=(req_name,))
    t.daemon = True
    t.start()

def run_req(req_name):
    try:
        asyncio.run(req(req_name))
    except (websockets.exceptions.InvalidURI, OSError, websockets.exceptions.InvalidHandshake, TimeoutError):
        pass

async def req(req_name):
    async with websockets.connect(f"ws://{host}:{port}") as ws:
        reply = await ws.recv()
        identify = {"op": 1,"d": {"rpcVersion": 1}}
        await ws.send(json.dumps(identify))
        reply = await ws.recv()
        request = {"op": 6, "d": {"requestType": req_name, 
                "requestId": "1"}}
        await ws.send(json.dumps(request))
        reply = await ws.recv()
