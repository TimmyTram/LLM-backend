import websockets
import websockets.sync.client
import asyncio
from dotenv import load_dotenv
import os
from utils.printer import bcolors as bc
import time

async def clientInput():
    uri = f'ws://{os.getenv('HOST_NAME')}:{os.getenv('PORT')}'
    
    while True:
        prompt = input("User: ")
        if prompt == '!DISCONNECT':
            bc.color_print(bc.BOLD + bc.OKGREEN, "Disconnecting...")
            break

        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send(prompt)
                response = await websocket.recv()
                bc.color_print(bc.BOLD + bc.OKCYAN, f'Origo: {response}')
        except Exception as e:
            bc.color_print(bc.WARNING, f"Exception during Websocket Connection: {e}")
            bc.color_print(bc.OKGREEN, 'Connection to backend was lost retrying in 3 seconds')
            time.sleep(3) 
            continue
   


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(clientInput())  