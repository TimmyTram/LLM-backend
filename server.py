import LLMCore
import LLMConfig
from dotenv import load_dotenv
from utils.printer import bcolors as bc
import os
import time
import websockets
import asyncio
import functools

async def handler(websocket, LLM):
    try:
        userInput = await websocket.recv()
        # userRequest = await websocket.recv()
        # userInput = userRequest[0]
        # context_id = userRequest[1]

        # print(userInput)
        # print(context_id)
    except websockets.ConnectionClosedOK:
        bc.color_print(bc.OKBLUE, "User closed connection.")
        return

    if len(userInput) == 0:
        await websocket.send("User input cannot be empty.")
        return

    try:
        #llmResponse = LLM.generateOutputChunk(userInput, 'chat_1')
        llmStream = LLM.generateOutputStream(userInput, 'chat_1')
        llmResponse = ''
        for out in llmStream:
            print(bc.OKCYAN + out + bc.ENDC, sep=' ', end='', flush=True)
            llmResponse += out

    except Exception as e:
        bc.color_print(bc.BOLD + bc.WARNING, f"Got Exception: {e}")
        return
    
    await websocket.send(llmResponse)


async def main(HOST_NAME, PORT, LLM):
    bc.color_print(bc.BOLD + bc.UNDERLINE + bc.OKBLUE, f"Listening on ws://{HOST_NAME}:{PORT}")
    llm_handler = functools.partial(handler, LLM=LLM)
    async with websockets.serve(llm_handler, HOST_NAME, PORT):
        await asyncio.Future()
        
if __name__ == "__main__":
    load_dotenv()
    model_path = os.getenv('MODEL_PATH')
    #localLLM = LLMCore.LLM(model_path)

    llmConfig = LLMConfig.LLMConfig()
    llmConfig.loadModelConfig()
    localLLM = LLMCore.LLM(llmConfig)


    start = time.time()
    localLLM.loadModel()
    end = time.time()
    bc.color_print(bc.OKGREEN, f'Time taken to load Model: {end - start:.04f} seconds.')
    
    hostName = os.getenv('HOST_NAME')
    portNumber = os.getenv('PORT')
    asyncio.run(main(hostName, portNumber, localLLM))