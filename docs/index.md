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

# Home

Welcome, the Gemini Enrichment Project is a python project demonstrating how to simplify
content creation using Gemini while doing so in a parallel friendly manor allowing 
your project to scale horizontally.

> Note, since Gemini is managed by token utilization and quota there is both a cost an limit
> placed on the execution capabilities of your code.

Please see [Project Setup](setup.md) for details on how to run the tests.

## Running Examples
```shell
poetry install

# Google Content Enrichment
gce --help

# Simple XOR crypt your API Key, copy the SALT and put that in your env.toml file
# while the encrypted password is put in your environment specific file.
gce encrypt-password

## Start the API Server
gce api-server

## Open a browser to localhost:8000/docs
open http://localhost:8000/docs
```

Navigate to the "Products" => "/api/v1/products/example" and execute.

> NOTE: Uvicorn and FastAPI are ASGI compliant (vs WSGI). This means they are efficient
> async processors, and every command is implemented as executable on their own thread.


## Testing

```shell
# execute the tests while hiding test stdout
poetry run pytest

# execute the tests and see the test stdout
poetry run pytest -s
```