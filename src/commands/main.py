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

# A collection of command objects that can be reused in multiple chains
from commands.enrichment import category_detection_from_image, extract_languages, extract_product_details
from model.chain import Chain, Command


category_detector = Command('category-detection', category_detection_from_image)
content_enricher = Command('content-enricher)', extract_product_details)
language_extractor = Command('language-extractor', extract_languages)

# A simple chain of responsibility that executes the commands in series
product_enrichment_from_image = Chain("product-enrichment-from-image", category_detector, content_enricher, language_extractor)