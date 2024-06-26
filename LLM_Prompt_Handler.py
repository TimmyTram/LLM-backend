from utils.printer import bcolors as bc
import json

class PromptHandler:

    CONFIG_DIRECTORY = './config'
    PROMPT_CONFIG = 'prompt_templates.json'

    def __init__(self):
        self.system_prefix = ''
        self.system_suffix = ''
        self.human_prefix = ''
        self.human_suffix = ''
        self.ai_prefix = ''
        self.ai_suffix = ''
        self.wrapper = []
        self.stop = []

    def loadPromptTemplate(self, chat_format):
        try:
            with open(f'{self.CONFIG_DIRECTORY}/{self.PROMPT_CONFIG}', 'r') as file:
                data = json.load(file)
                for key, value in data[chat_format].items():
                     setattr(self, key, value)
        except FileNotFoundError:
            bc.color_print(bc.WARNING, 'config.json could not be found')
        except KeyError:
            bc.color_print(bc.WARNING, f'{chat_format} is not in the presets.json.')

    def createSystemPromptTemplate(self, system_prompt):
        template = f'{self.system_prefix}{system_prompt}{self.system_suffix}'
        #bc.color_print(bc.OKGREEN, f'System Prompt Template: {template}')
        return template

    def createUserPromptTemplate(self, user_prompt):
        template = f'{self.human_prefix}{user_prompt}{self.human_suffix}{self.ai_prefix}'
        #bc.color_print(bc.OKGREEN, f'User Prompt Template: {template}')
        return template