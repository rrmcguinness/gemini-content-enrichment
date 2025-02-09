# Copyright 2025 Google, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
import time
import tomllib
from model.api import TomlClass
from PIL import Image

from google import genai
from google.genai import types

from utils.ezcrypt import decrypt
from utils.strings import get_env_file_name


class Application(TomlClass):
    project_id: str
    location: str
    salt: str
    api_key: str
    thread_pool_size: int

class Embedding(TomlClass):
    client: genai.Client
    model_name: str
    
    def __init__(self, d = None):
        super().__init__(d)
        
    def initialize_client(self, api_key: str) -> None:
         self.client = genai.Client(api_key=api_key)

    def generate_text_embeddings(self, value: str):
        result = self.client.models.embed_content(
            model=self.model_name,
            content=value
        )
        return result.embeddings
    

class ContentGenerator(TomlClass):
    client: genai.Client
    model_name: str
    ground_with_google: bool
    instructions: str
    temperature: float
    top_p: float
    top_k: float
    max_output_tokens: int
    output_format: str
    
    def __init__(self, d = None):
        super().__init__(d)

    def initialize_client(self, api_key: str) -> None:
        if (not hasattr(self, 'client') or self.client is None):
            self.client = genai.Client(api_key=api_key)

    def get_generative_config(self) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=self.instructions,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_output_tokens=self.max_output_tokens,
            response_mime_type=self.output_format,
            safety_settings=[
                {
                    "category": types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    "threshold": types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                },
                {
                    "category": types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    "threshold": types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                },
                {
                    "category": types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    "threshold": types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                },
                {
                    "category": types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    "threshold": types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                },
                {
                    "category": types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,
                    "threshold": types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                },
            ],
            tools = [types.Tool(google_search=types.GoogleSearchRetrieval)] if self.ground_with_google else []
        )
    
    def generate_content(self, prompt: str) -> str:
        response =self.client.models.generate_content(
            model=self.model_name,
            config=self.get_generative_config(),
            contents=[prompt])
        return response.text
    
    def understand_image(self, prompt: str, image: Image):
        response =self.client.models.generate_content(
            model=self.model_name,
            config=self.get_generative_config(),
            contents=[prompt, image])
        return response.text
    
    def understand_video(self, prompt: str, video_path: str):
        video_file = self.client.files.upload(path=video_path)
        while video_file.state.name == "PROCESSING":
            print('.', end='')
            time.sleep(1)
            video_file = self.client.files.get(name=video_file.name)
            
        if video_file.state.name == "FAILED":
            raise ValueError(video_file.state.name)
        
        response = self.client.models.generate_content(
            model=self.model,
            config=self.get_generative_config(),
            contents=[
                video_file,
                prompt
            ])
        return response.text
        

class NamedPrompt(TomlClass):
    name: str
    prompt: str
    
class GenerativeAI(TomlClass):
    embedding: Embedding
    generators: dict[str, ContentGenerator]

class Config():
    application: Application
    generative_ai: GenerativeAI
    prompts: list[NamedPrompt]
    
    def __init__(self, file_name):
        env_file_name = get_env_file_name(file_name)
        
        with open(file_name, "rb") as f:
            print("Loading configuration from file: ", file_name)
            data = tomllib.load(f)
            
            setattr(self, "application", Application(data.get("application")))
            
            prompts = []
            for p in data.get("prompts"):
                prompts.append(NamedPrompt(p))
                
            setattr(self, "prompts", prompts)

            v = GenerativeAI()
            v.embedding = Embedding(data.get("generative_ai")["embedding"])

            v.generators = {}
            generators = data.get("generative_ai")["generators"]
            if isinstance(generators, dict):
                for k, g in generators.items():
                    v.generators[k] = ContentGenerator(g)

            setattr(self, "generative_ai", v)

        if env_file_name is not None:
            with open(env_file_name, "rb") as f:
                print("Loading environment config file: ", env_file_name)
                data = tomllib.load(f)
                
                self.application.updateValues(data.get("application"))
                
                if data.get("prompts") is not None:
                    existing_prompts = copy.deepcopy(self.prompts)
                    override_prompts = []
                
                    for p in data.get("prompts"):
                        override_prompts.append(NamedPrompt(p))
                        
                    for e in existing_prompts:
                        if not any(o.name == e.name for o in override_prompts):
                            override_prompts.append(e)
                
                    setattr(self, "prompts", override_prompts)
                
                if data.get("generative_ai") is not None:
                    if data.get("generative_ai")["embedding"] is not None:
                        self.generative_ai.embedding.updateValues(data.get("generative_ai")["embedding"])
                        
                    if data.get("generative_ai")["generators"] is not None:
                        for k, g in self.generative_ai.generators:
                            if k in data.get("generative_ai")["generators"]:
                                g.updateValues(data.get("generative_ai")["generators"][k])
                                
        if self.generative_ai.embedding is not None:
            self.generative_ai.embedding.initialize_client(decrypt(self.application.api_key, self.application.salt))
            
        for k, g in self.generative_ai.generators.items():
            g.initialize_client(decrypt(self.application.api_key, self.application.salt))
            
    def get_prompt_by_name(self, name: str) -> NamedPrompt:
        for p in self.prompts:
            if p.name == name:
                return p
        return None()
    
    def get_generator_by_name(self, name: str) -> ContentGenerator:
        return self.generative_ai.generators[name]
    
    def get_embedding(self) -> Embedding:
        return self.generative_ai.embedding