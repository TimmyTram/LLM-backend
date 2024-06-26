import json
from utils.printer import bcolors as bc


class LLMConfig:

    CONFIG_DIRECTORY = './config'
    MODEL_CONFIG = 'config.json'

    def __init__(self):
        # Default settings
        self.modelPath = ''                             
        self.temperature = 0.7              
        self.top_k = 40                     
        self.repeat_penalty = 1.1            
        self.min_p = 0.1
        self.top_p = 0.9
        self.max_tokens = 100               
        self.n_ctx = 2048                   
        self.chat_format = 'chatml'
 
    def loadModelConfig(self):
        try:
            with open(f'{self.CONFIG_DIRECTORY}/{self.MODEL_CONFIG}', 'r') as file:
                data = json.load(file)
                for key, value in data.items():
                    setattr(self, key, value)
        except FileNotFoundError:
            bc.color_print(bc.WARNING, 'config.json could not be found')
    

    def saveModelConfig(self):
        pass