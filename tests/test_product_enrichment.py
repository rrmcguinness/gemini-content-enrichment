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

from model.chain import Context
from model.config import Config
from model.examples import example_category, example_product
from commands.main import product_enrichment_from_image
from PIL import Image
from opentelemetry.sdk.trace import Tracer
import pytest


@pytest.mark.asyncio
async def test_product_enrichment(config: Config, tracer: Tracer):

    # Below represents what would happen for each request and/or message
    # 1) Build the context with the initial values
    # 2) Execute the chain of responsibility allowing it to add values to the context
    # 3) Finally extract the value from the chain.
    
    with tracer.start_span("test_product_enrichment"):
        # Load an image
        apparel_image = Image.open("third_party/images/apparel.jpeg")
        
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
        
        # Verify the content was created
        assert context.get("product_json") is not None
        
        # Print the output
        print(context.get("product_json"))