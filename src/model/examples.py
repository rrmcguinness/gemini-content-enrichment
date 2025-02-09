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

"""Using pydantic here to make life easier with JSON serialization"""
from pydantic import BaseModel


class Attribute(BaseModel):
    """
    A simplified attribute object with 'possible' value ranges,
    not to be confused with a product attribute which is a realized value range.
    """
    name: str
    description: str
    value_range: list[str]
    
class Category(BaseModel):
    """
    A simple struct for encapsulating the rules for a category.
    """
    name: str
    attributes: list[Attribute]
    
class ProductAttributeValue(BaseModel):
    """
    Unlike the Attribute above, this holds the value for the product vs a possible range.
    """
    name: str
    value: str

class ProductImage(BaseModel):
    """
    A simple structure for describing an image. The base64 attribute is used for RAW
    API execution which is now wrapped in a PIL Image from the latest API.
    """
    url: str
    base64: str
    type: str
    
class BaseProduct(BaseModel):
    """
    Is the product instance values for a product, allowing the Product to encapsulate
    additional product references without creating circular dependencies.
    """
    language: str
    name: str
    description: str
    seo_html_header: str
    attribute_values: list[ProductAttributeValue]
    
class Product(BaseModel):
    """
    Represents a more complex product hierarchy that may contain additional product relationships.
    """
    base: BaseProduct
    category: Category
    images: list[ProductImage]
    related_products: list["Product"]
    derived_products: list["Product"]
    
    
example_category = Category(name="Clothing > Men's Clothing > Men's Shirts > Dress Shirts", attributes=[
        Attribute(name="Brand", description="The manufacturer of the product.", value_range=["Pronto Uomo"]),
        Attribute(name="Size", description="The size of the garment", value_range=["S", "M", "L", "XL", "XXL"])
    ])

example_product = Product(base=BaseProduct(
        language="US_EN", 
        name="Long Sleeve Dress Shirt",
        description="Experience timeless style and modern comfort with the Pronto Uomo Herringbone Modern Fit Long Sleeve Dress Shirt.", 
        seo_html_header="<html><head><title></title><meta name=\"description\" content=\"\"></head><body></body></html>",
        attribute_values=[
            ProductAttributeValue(name="Brand", value="Pronto Uomo"),
            ProductAttributeValue(name="Size", value="M")
        ]),
        category=example_category,
        images=[], derived_products=[], related_products=[])