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

import re
from typing import Callable, Any


from model.config import Config 
VARIABLE_EXPANSION_PATTERN = r"\$\{(.+?)\}"

class Context():
    def __init__(self, config: Config):
        super().__init__()
        self.state: dict[str, Any] = {}
        self.errors: list[Exception] = []
        self.config: Config = config
        
    def get_config(self) -> Config:
        return self.config
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def add_error(self, error: Exception) -> None:
        self.errors.append(error)
        
    def set(self, key: str, value: Any) -> None:
        self.state[key] = value
        
    def get(self, key: str, default=None) -> Any:
        return self.state.get(key, default)

    def expand_variables(self, input: str):
        def replace_match(match):
            key = match.group(1)
            return self.get(key, "")

        return re.sub(VARIABLE_EXPANSION_PATTERN, replace_match, input)


class Command():
    def __init__(self, name: str, func: Callable[[Context], None]):
        super().__init__()
        self.name = name
        self.func = func
    
    def execute(self, context: Context):
        self.func(context)

        
    
class Chain(Command):
    def __init__(self, name: str, *args: Command):
        super().__init__(name=name, func=self.execute)
        self.commands: list[Command] = args
    
    def get_commands(self) -> list[Command]:
        return self.commands
    
    def add_command(self, command: Command):
        self.commands.append(command)
    
    def remove_command(self, command: Command):
        self.commands.remove(command)
        
    def execute(self, context: Context):
        for command in self.commands:
            command.execute(context)
 
            