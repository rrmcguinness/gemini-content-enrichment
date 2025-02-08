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

import os

DOT_SEPARATOR = '.'

ENV_VAR_GCP_RUNTIME_ENV = 'GCP_RUNTIME_ENV'
ENV_DEFAULT_RUNTIME = 'local'

PREFIX_MD_JSON = "```json"
SUFFIX_MD_CODE= "```"

EMPTY_STRING = ""


def fix_prompt(value: str) -> str:
    value = value.strip()
    value = "\n".join(map(lambda x: x.strip(), value.split("\n")))
    return value

def fix_output(value: str) -> str:
    value = value.replace(PREFIX_MD_JSON, EMPTY_STRING)
    value = value.replace(SUFFIX_MD_CODE, EMPTY_STRING)
    return value

def get_env_file_name(file_name: str) -> str:
    env = os.environ.get(ENV_VAR_GCP_RUNTIME_ENV, ENV_DEFAULT_RUNTIME)

    env_file = None
    parts = file_name.split(DOT_SEPARATOR)
    if len(parts) == 2:
        temp_file = DOT_SEPARATOR.join([parts[0], env, parts[1]])
        if os.path.isfile(temp_file):
            env_file = temp_file

    return env_file