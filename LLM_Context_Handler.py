import os
from utils.printer import bcolors as bc
from pathlib import Path
import json

class ContextHandler():

    CONTEXT_DIR = './context'
    MEMORY_DIR = './memories/'
    SYSTEM_PROMPT_FILENAME = 'system_prompt.txt'

    @staticmethod
    def context_filename(context_id):
        context_filename = os.path.join(ContextHandler.CONTEXT_DIR, str(context_id) + '.json')
        return context_filename

    @staticmethod
    def context_metadata_filename(context_id):
        context_metadata_filename = os.path.join(ContextHandler.CONTEXT_DIR, str(context_id) + '.metadata.json')
        return context_metadata_filename

    @staticmethod
    def get_system_prompt_filepath():
        system_prompt_filepath = os.path.join(ContextHandler.MEMORY_DIR + ContextHandler.SYSTEM_PROMPT_FILENAME)
        return system_prompt_filepath

    @staticmethod
    def load_context(context_id, model, promptHandler):
        
        # If there exists a context file, load it
        if Path(ContextHandler.context_filename(context_id)).is_file():

            bc.color_print(bc.OKGREEN, f"Loading context file: {context_id}...")
            with open(ContextHandler.context_filename(context_id), 'r') as file:
                messages = json.loads(file.read())
            
            return messages, [] # Number of system tokens does not need to be returned
        messages = []

        # check if there exists a system_prompt otherwise give a default assistant system prompt
        if Path(ContextHandler.get_system_prompt_filepath()).is_file():
            
            # Create a 'system' message in the beginning of context
            # Vicuna does not have a proper chat_format so it cannot get the system prompt correctly.
            # Using user as fake system

            systemPrompt = ContextHandler.load_system_prompt(ContextHandler.get_system_prompt_filepath())
            systemTokens = model.tokenize(text=bytes(systemPrompt, 'utf-8')) # get the number of system tokens
            
            messages.append({
                "role": "system",
                "content": promptHandler.createSystemPromptTemplate(systemPrompt),
                "tokens": len(systemTokens)
            })


        else:
            bc.color_print(bc.OKGREEN, "Loading default system prompt...")
            systemPrompt = "You are an AI assistant."
            systemTokens = model.tokenize(text=bytes(systemPrompt))
            
            messages.append({
                "role": "system",
                "content": promptHandler.createSystemPromptTemplate(systemPrompt),
                "tokens": len(systemTokens)
            })
            
        return messages, systemTokens
    
    @staticmethod
    def save_context(context_id, messages):
        with open(ContextHandler.context_filename(context_id), 'w') as file:
            file.write(json.dumps(messages))

    @staticmethod
    def reset_context(context_id):
        try:
            os.remove(ContextHandler.context_filename(context_id))
            os.remove(ContextHandler.context_metadata_filename(context_id))
            return "Context Reset"
        except FileNotFoundError:
            return f"Context files: {context_id} do not exist"

    @staticmethod
    def load_system_prompt(memories_path):
        try:
            with open(memories_path, 'r') as file:
                context = ""
                for line in file:
                    context += line
        except FileNotFoundError:
            bc.color_print(bc.WARNING, "System prompt file could not be found.")
        
        return context
    

    @staticmethod
    def load_metadata(context_id):
        metadata_filename = ContextHandler.context_metadata_filename(context_id)
        if Path(metadata_filename).is_file():
            bc.color_print(bc.OKGREEN, f"Loading context metadata file: {metadata_filename}...")
            with open(metadata_filename, 'r') as file:
                metadata = json.loads(file.read())
            
            return metadata
        else:
            return {"total_tokens": 0}

    @staticmethod
    def save_metadata(context_id, content):
        with open(ContextHandler.context_metadata_filename(context_id), 'w') as file:
            file.write(json.dumps(content))