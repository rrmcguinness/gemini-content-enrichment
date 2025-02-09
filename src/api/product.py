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


import json
from fastapi import Response, status, FastAPI, APIRouter, Depends
from fastapi_throttle import RateLimiter
from pydantic import ValidationError
from model.examples import Product, example_category, example_product
from commands.enrichment import product_enrichment_from_image
from PIL import Image
from model.chain import Context
from model.config import Config
from opentelemetry import trace
import os


def register(app: FastAPI, config: Config) -> APIRouter:
    """
    Registers the router for /api/v1/products.
    Demonstrates using a throttle on the end-point.
    """
    router = APIRouter(prefix="/api/v1/products")
    
    @router.post("/", 
                 status_code=status.HTTP_200_OK, 
                 tags=["Products"],
                 response_model=Product)
    async def product():
        return {"status": "ok"}

    @router.get("/example", 
                status_code=status.HTTP_200_OK, 
                tags=["Products"], 
                dependencies=[Depends(RateLimiter(times=1, seconds=10))],
                response_model=Product)
    async def product_example(response: Response):
        tracer = trace.get_tracer(__name__)
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        with tracer.start_span("test_product_enrichment"):
            # Load an image
            apparel_image = Image.open(f"{script_dir}/assets/images/apparel.jpeg")
            
            # Load two example objects and get their JSON representations
            category_model = example_category.model_dump_json()
            product_attribute_value_model = example_product.model_dump_json()
            
            # Create the context
            context = Context(config)
            context.set("product_image", apparel_image)
            context.set("category_model", category_model)
            context.set("product_attribute_value_model", product_attribute_value_model)
            
            # Execute the Chain of responsibility
            await product_enrichment_from_image.execute(context=context)
            
            try:
                outProduct = Product.model_validate(json.loads(context.get("product_json")))
                # Verify the content was created
                return outProduct
            except ValidationError:
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return {"status": "error", "message": "validation error, bad response from Gemini"}
                
    return router