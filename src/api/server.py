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

import uvicorn
from fastapi import FastAPI

from model.config import Config
from utils.logging import setup_logging, setup_tracer

from api.product import register as products
from api.checks import register as api_checks

config = Config("env.toml")
app = FastAPI(title="Gemini Content Enrichment")
app.include_router(api_checks(config))
app.include_router(products(app, config))

def register_listeners(config: Config):
    print("Dude where's my router")

def start(config: Config, host: str, port: int, reload: bool):
    
    try:
        setup_logging()
        setup_tracer(config)
    except Exception as e:
        print(e)

    register_listeners(config)
    
    
    """Starts the server in dev mode"""
    uvicorn.run("api.server:app", host=host, port=port, reload=reload)
    
if __name__ == "__main__":
    config = Config("env.toml")
    register_listeners(config)
    start(config, "127.0.0.1", 8000, reload=True)