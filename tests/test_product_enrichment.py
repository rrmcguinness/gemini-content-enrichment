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


from pydantic import BaseModel
import pytest
from model.chain import Context
from model.config import Config
from commands.enrichment import product_enrichment_from_image
from PIL import Image

"""Using pydantic here to make life easier with JSON serialization"""
class Attribute(BaseModel):
    name: str
    description: str
    value_range: list[str]
    
class Category(BaseModel):
    name: str
    attributes: list[Attribute]
    
class ProductAttributeValue(BaseModel):
    name: str
    value: str

class ProductImage(BaseModel):
    url: str
    base64: str
    type: str
    
class BaseProduct(BaseModel):
    language: str
    name: str
    description: str
    seo_html_header: str
    attribute_values: list[ProductAttributeValue]
    
class Product(BaseModel):
    base: BaseProduct
    category: Category
    images: list[ProductImage]


@pytest.fixture(scope="class")
def apparel_image() -> Image:
    yield Image.open("third_party/images/apparel.jpeg")
    

@pytest.fixture(scope="class")
def example_category() -> Category:
    yield Category(name="Clothing > Men's Clothing > Men's Shirts > Dress Shirts", attributes=[
        Attribute(name="Brand", description="The manufacturer of the product.", value_range=["Pronto Uomo"]),
        Attribute(name="Size", description="The size of the garment", value_range=["S", "M", "L", "XL", "XXL"])
    ])

@pytest.fixture(scope="class")
def example_product(example_category: Category) -> Product:
    yield Product(base=BaseProduct(
        language="US_EN", 
        name="Long Sleeve Dress Shirt",
        description="Experience timeless style and modern comfort with the Pronto Uomo Herringbone Modern Fit Long Sleeve Dress Shirt.", 
        seo_html_header="<html><head><title></title><meta name=\"description\" content=\"\"></head><body></body></html>",
        attribute_values=[
            ProductAttributeValue(name="Brand", value="Pronto Uomo"),
            ProductAttributeValue(name="Size", value="M")
        ]),
        category=example_category,
        images=[])


def test_product_enrichment(config: Config,
                            example_category: Category,
                            example_product: Product,
                            apparel_image: Image):
    
    category_model = example_category.model_dump_json()
    product_attribute_value_model = example_product.model_dump_json()
    
    context = Context(config)
    context.set("product_image", apparel_image)
    context.set("category_model", category_model)
    context.set("product_attribute_value_model", product_attribute_value_model)
    
    product_enrichment_from_image.execute(context=context)
    
    assert context.get("product_json") is not None
    
    print(context.get("product_json"))