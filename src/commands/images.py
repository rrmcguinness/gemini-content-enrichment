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

import tempfile
from model.chain import Command, Context
from google.cloud import storage
import requests
import os

import urllib.parse

def get_filename_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    file_path = parsed_url.path
    return os.path.basename(file_path)

storage_client = storage.Client()

class ImageDownloadCommand(Command):

    def __init__(self,
                 name: str, 
                 input_variable_name: str, 
                 output_variable_name: str,
                 storage_bucket_name: str, prefix: str, suffix: str):
        super(name, self.do_execute)
        self.input_variable_name  = input_variable_name
        self.output_variable_name = output_variable_name
        self.storage_bucket_name  = storage_bucket_name
        self.prefix               = prefix
        self.suffix               = suffix
        self.bucket_exists = storage_client.bucket_exists(storage_bucket_name)
        
        if not self.bucket_exists:
            try:
                storage_client.create_bucket(storage_bucket_name)
                self.bucket_exists = True
            except Exception as e:
                print(e)
        
    
    def do_execute(self, context: Context):
        """
        Takes a list of URLs, downloads them to a storage bucket and returns a map of:
        {
            "original_file_name": "gcs_path"
        }
        Where:
        * Original file name is the file name minus the URL prefix.
        * gcs_path = bucket + prefix + file_name + suffix
        """
        
        if context.has_key(self.input_variable_name):
            images = context.get(self.input_variable_name)
            out = {}
            if isinstance(images, list):
                for image in images:
                    full_name = get_filename_from_url(image)
                    [fname, ext] = full_name.split('.')
                    
                    if image.startswith('http'):
                        data = requests.get(image).content
                        with tempfile.TemporaryFile(mode="w+") as fp:
                            fp.write(data)
                            fp.seek(0)
                            bucket = storage_client.bucket(self.storage_bucket_name)
                            blob = bucket.blob(f"{self.prefix}{fname}{self.suffix}{ext}")
                            blob.upload_from_string(fp)
                            out[image] = f"{bucket.path}{self.prefix}{fname}{self.suffix}{ext}"
            
            context.set(self.output_variable_name, out)
            
                    