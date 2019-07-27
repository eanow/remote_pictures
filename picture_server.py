#!/usr/bin/env python3

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets
import os
import base64

logging.basicConfig()


USERS = set()

async def enumerate_images(websocket):
    if USERS:  # asyncio.wait doesn't accept an empty list
        filelist=list()
        for r,d,f in os.walk('images'):
            for file in f:
                filelist.append(file)
        message=json.dumps(filelist)
        print(message)
        await websocket.send(message)


async def change_image(message):
    if USERS:  # asyncio.wait doesn't accept an empty list
        new_pic=message.split('|')[1]
        file=open('images/'+new_pic,'rb')
        file_content=file.read()
        encoded_string=base64.b64encode(file_content)
        #print(encoded_string)
        await asyncio.wait([user.send(encoded_string.decode("utf-8")) for user in USERS])


async def register(websocket):
    USERS.add(websocket)
    #await notify_users()


async def unregister(websocket):
    USERS.remove(websocket)
    #await notify_users()


async def server(websocket, path):

    # register(websocket) sends user_event() to websocket
    #await register(websocket)
    try:
        async for message in websocket:
            print(message)
            if message=='fetch_images':
                print("Calling Fetch")
                #generate list of images and send
                await enumerate_images(websocket)
            elif message=='register_client':
                await register(websocket)
            elif 'change|' in message:
                await change_image(message)

    finally:
        await unregister(websocket)


start_server = websockets.serve(server, "192.168.19.190", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
