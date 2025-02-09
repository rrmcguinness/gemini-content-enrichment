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

from fastapi import status, APIRouter, FastAPI

def register(app: FastAPI) -> APIRouter:
    router = APIRouter()
        
    @router.get("/readiness_check", status_code=status.HTTP_200_OK, tags=["Status Checks"])
    async def readiness_check():
        return {"status": "ok"}

    @router.get("/liveness_check", status_code=status.HTTP_200_OK, tags=["Status Checks"])
    async def liveness_check():
        return {"status": "ok"}
    
    return router