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

from opentelemetry import trace


from model.config import Config 
VARIABLE_EXPANSION_PATTERN = r"\$\{(.+?)\}"

class Context():
    """
    Context is the async state holder for per-request workflows.
    The context is the only mutable object in any workflow, while
    the commands and chains are immutable. This allows the effective-final
    pattern for realizing high volume parallelism.
    """
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
    
    def has_key(self, key: str) -> bool:
        return key in self.state and self.state[key] is not None
    
    def expand_variables(self, input: str):
        def replace_match(match):
            key = match.group(1)
            return self.get(key, "")

        return re.sub(VARIABLE_EXPANSION_PATTERN, replace_match, input)


class Command():
    """
    Represents a single, testable, unit of work (see Command Pattern). Commands work upon the context,
    and hold little to no state of their own, and never persistent state, meaning
    the state of the command state IS NOT passivated or activated from serialization.
    Or simply put, the command state is renewed every time is is created.
    """
    def __init__(self, name: str, func: Callable[[Context], None]):
        super().__init__()
        self.name = name
        self.func = func
    
    async def execute(self, context: Context):
        trace.get_current_span().set_attribute("command.context_size", len(context.state))
        await self.func(context)

        
    
class Chain(Command):
    """
    Is a collection of commands that are executed according to the execution strategy.
    This simple chain uses serial execution, allowing each command to decide if it should
    be executed or skipped. Since a chain IS-A command, you may create chain-or-chains
    allowing for complex execution over a per-request payload.
    """
    def __init__(self, name: str, *args: Command):
        super().__init__(name=name, func=self.execute)
        self.commands: list[Command] = args
    
    def get_commands(self) -> list[Command]:
        return self.commands
    
    def add_command(self, command: Command):
        self.commands.append(command)
    
    def remove_command(self, command: Command):
        self.commands.remove(command)
        
    async def execute(self, context: Context):
        trace.get_current_span().add_event("chain_start", self.name)
        for command in self.commands:
            trace.get_current_span().add_event("command_start", command.name)
            await command.execute(context)
            trace.get_current_span().add_event("command_finish", command.name)
        trace.get_current_span().add_event("chain_finish", self.name)
 
            