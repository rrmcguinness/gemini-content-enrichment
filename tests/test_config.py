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

from model.config import Config
    
def test_config(config: Config) -> None:
    assert config is not None
    
    assert config.application is not None
    
    assert config.application.project_id is not None
    
    assert config.generative_ai.generators is not None
    
    assert config.generative_ai.generators["flash"] is not None
    
    assert config.generative_ai.generators["pro"] is not None
    
    assert config.generative_ai.generators["critic"] is not None
    
    assert config.prompts is not None
    
    assert len(config.prompts) == 4
    
    joke = config.generative_ai.generators["flash"].generate_content("Tell me a funny joke.")

    assert joke is not None
    
    print("Joke: ", joke)
    
    
    