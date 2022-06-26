import asyncio
import websockets
import json
from db import User
from util import decode_cookie
import os
from time import time
import db

clients = []
t = 0
async def chat(websocket):
    global all_users, t, clients
    if time() - t >= 300:
        all_users, t = db.get_all_users(), time()
        print('renewing cache')
    clients.append(websocket)
    async for message in websocket:
        msg = json.loads(message)
        msg_content = msg['msg_content']
        msg_author = decode_cookie(msg['msg_author_cookie'])['_user_id']
        decodedid = msg_author
        ids = []
        for i in all_users:
            ids.append(i.id)
        if not int(msg_author) in ids:
            msg_author = '[New User]'
        else:
            for i in all_users:
                if int(i.id) == int(decodedid):
                    msg_author = i.username
        for i in clients:
            try:
                await i.send(json.dumps({"msg_author": msg_author, "msg_content": msg_content}))
            except:
                pass

async def main():
    async with websockets.serve(chat, "0.0.0.0", 8082):
        await asyncio.Future() 
asyncio.run(main())

