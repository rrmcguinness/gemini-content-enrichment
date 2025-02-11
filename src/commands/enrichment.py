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

from model.chain import Chain, Context, Command


def category_detection_from_image(context: Context) -> None:
    """Using the context variables:
    * product_image
    * category_model
    extract the category attributes into the model"""
    generator = context.get_config().get_generator_by_name("flash")
    prompt_template = context.get_config().get_prompt_by_name("category_detection")
    prompt = context.expand_variables(prompt_template.prompt)
    context.set("category_attributes", generator.understand_image(prompt, context.get("product_image")))
    
    
def extract_product_details(context: Context) -> None:
    """ Using the category attributes, create a product detail using:
    IN
    * category_attributes
    * product_attribute_value_model
    OUT
    * product_json
    """
    generator = context.get_config().get_generator_by_name("flash")
    prompt_template = context.get_config().get_prompt_by_name("extract_product_details")
    prompt = context.expand_variables(prompt_template.prompt)
    context.set("product_json", generator.generate_content(prompt))


def extract_languages(context: Context) -> None:
    languages = context.get("languages")
    if languages is not None:
        generator = context.get_config().get_generator_by_name("flash")
        prompt_template = context.get_config().get_prompt_by_name("translate_product_details")
        if isinstance(languages, list):
            for language in languages:
                context.set("target_language", language)
                prompt = context.expand_variables(prompt_template.prompt)
                context.set("language_{language}", generator.generate_content(prompt))  
            