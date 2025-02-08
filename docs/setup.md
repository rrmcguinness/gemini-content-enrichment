<!--
 Copyright 2025 Google, LLC
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 
     https://www.apache.org/licenses/LICENSE-2.0
 
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

# Setup

## Prerequisite

* Install PipX
* Install Poetry 2.x
* Install Google Cloud CLI
* Ensure you're logged into a project that has the Gemini services enabled in you CLI
* Get and API Key for that project

## Getting started

### Dependencies

This is a poetry project run the following commands in the terminal at the project root:
```shell

gcloud auth application-default login

cd <PROJECT_ROOT>
poetry install

# Install the poetry shell plugin (changed in v2)
poetry self add poetry-plugin-shell

# Launch your virtual environment
poetry shell

```

### Testing

Before running the pytests, you'll need to configure a test configuration file.

Create a test configuration file `env.test.toml` and add your project_id and api_key:

env.test.toml
```toml
[application]
project_id = ""
api_key = ""
```

> NOTE: The configuration loader will first load "env.toml" and then override values with
> the environment specific toml file.

#### Running the unit tests

```shell
# execute the tests while hiding test stdout
poetry run pytest

# execute the tests and see the test stdout
poetry run pytest -s
```


