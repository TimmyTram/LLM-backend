from llama_cpp import Llama
import multiprocessing as mp
from utils.printer import bcolors as bc
from LLM_Context_Handler import ContextHandler
from LLM_Prompt_Handler import PromptHandler

class LLM:
    def __init__(self, config):
        self.config = config                # Refer to LLMConfig
        self.model = None                   # Currently we have no model
        self.promptHandler = None           
        self.track_tokens = 0               # Manually tracking tokens to ensure it doesn't surpass n_ctx
        
        # These are important in reducing the latency of responses
        self.threadCount = mp.cpu_count()   # Get the max amount of threads our CPU can handle
        self.gpuLayers = -1                 # -1 Means use all GPU layers

    def loadModel(self):
        if self.config.modelPath is not None:
            try:
                self.model = Llama(
                    model_path=self.config.modelPath, 
                    n_threads= self.threadCount, 
                    n_gpu_layers=self.gpuLayers,
                    seed=-1,
                    n_ctx=self.config.n_ctx,
                    chat_format=self.config.chat_format
                )
                self.promptHandler = PromptHandler()
            except ValueError:
                bc.color_print(bc.FAIL, f"Model File path is not valid: {self.config.modelPath}")
                bc.color_print(bc.BOLD, "Exiting program...")
                exit()

    def updateModelConfig(self):
        # TODO: update
        pass

    def checkContextSpace(self, messages, metadata):
        limit = self.config.n_ctx * (((self.config.n_ctx - self.config.max_tokens) / self.config.n_ctx) - 0.05)
        totalTokens = metadata['total_tokens']
        while totalTokens >= limit:
            # Update total tokens before deletion
            tokensDeleted = messages[1]['tokens'] + messages[2]['tokens']
            metadata['total_tokens'] -= tokensDeleted
            del messages[1 : 3] # Delete a single pair to ensure we do overflow context
            bc.color_print(bc.BOLD + bc.OKGREEN, f"Deleted {tokensDeleted} tokens. | TOTAL TOKENS: {metadata['total_tokens']}")
            totalTokens = metadata['total_tokens']
        return messages, metadata

    def generateOutputChunk(self, prompt, context_id):
        messages, systemTokens = ContextHandler.load_context(context_id, self.model, self.promptHandler)
        metadata = ContextHandler.load_metadata(context_id)
        self.track_tokens = metadata['total_tokens']
        userPrompt = self.promptHandler.createUserPromptTemplate(prompt)
        userTokens = self.model.tokenize(text=bytes(userPrompt, 'utf-8'))

        message = {
            "role": "user",
            "content": userPrompt,
            "tokens": len(userTokens)
        }

        messages.append(message)

        response = self.model.create_chat_completion(
            messages=messages,
            temperature=self.config.temperature,
            top_k=self.config.top_k,
            top_p=self.config.top_p,
            min_p=self.config.min_p,
            repeat_penalty=self.config.repeat_penalty,
            max_tokens=self.config.max_tokens
        )


        response_tokens = response['usage']['completion_tokens']
        self.track_tokens = response['usage']['total_tokens']

        response = response['choices'][0]['message']
        response['tokens'] = response_tokens
        response_message = response['content']
        messages.append(response)
        
        metadata['total_tokens'] = self.track_tokens

        messages, metadata = self.checkContextSpace(messages, metadata)
        ContextHandler.save_context(context_id, messages)
        ContextHandler.save_metadata(context_id, metadata)
        bc.color_print(bc.BOLD + bc.OKGREEN, f'Tokens used: {self.track_tokens}/{self.config.n_ctx}')
        return response_message

    def generateOutputStream(self, prompt, context_id):
        messages, systemTokens = ContextHandler.load_context(context_id, self.model, self.promptHandler)
        metadata = ContextHandler.load_metadata(context_id)
        userPrompt = self.promptHandler.createUserPromptTemplate(prompt)
        self.track_tokens = metadata["total_tokens"]

        # Streamed output doesn't provide prompt tokens
        # So I need to get the number of tokens myself.
        userTokens = self.model.tokenize(text=bytes(userPrompt, 'utf-8'))
        
        self.track_tokens += len(systemTokens)
        self.track_tokens += len(userTokens)

        message = {
            "role": "user",
            "content": userPrompt,
            "tokens": len(userTokens)
        }

        messages.append(message)
    
        response = self.model.create_chat_completion(
            messages=messages,
            temperature=self.config.temperature,
            top_k=self.config.top_k,
            top_p=self.config.top_p,
            min_p=self.config.min_p,
            repeat_penalty=self.config.repeat_penalty,
            max_tokens=self.config.max_tokens,
            stream=True
        )

        # Need to capture all fragments to save to context
        chunkedContent = ''
        role = None
        response_tokens = 0

        # Stream the output to the user
        for out in response:
            out_dict = out['choices'][0]['delta']
            
            if "role" in out_dict:
                role = out['choices'][0]['delta']['role']
                response_tokens += 1
            elif "content" in out_dict:
                content = out['choices'][0]['delta']['content']
                chunkedContent += content # track each fragment
                response_tokens += 1
                yield content # Yield the content to the user
        
        response_msg = {
            "role": role,
            "content": chunkedContent.strip(),
            "tokens": response_tokens
        }

        self.track_tokens += response_tokens
        messages.append(response_msg)
        metadata["total_tokens"] = self.track_tokens

        messages, metadata = self.checkContextSpace(messages, metadata)
        ContextHandler.save_context(context_id, messages)
        ContextHandler.save_metadata(context_id, metadata)
        bc.color_print(bc.BOLD + bc.OKGREEN, f'Tokens used: {metadata["total_tokens"]}/{self.config.n_ctx}')