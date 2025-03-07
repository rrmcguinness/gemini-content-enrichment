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
import string
import random

# A simple utility for not storing passwords or keys in plain text.

DEFAULT_ENCODING = 'utf-8'
ENC_PREFIX = "ENC:"

def generate_random_string(length):
    letters = string.ascii_letters + string.digits  # Alphanumeric characters
    return ''.join(random.choice(letters) for i in range(length))

def string_to_hex(string):
    return ''.join([hex(ord(char))[2:] for char in string])

def hex_to_string(hex_string):
    return bytes.fromhex(hex_string).decode(DEFAULT_ENCODING)

def __xor_encrypt_decrypt(text, key):
    text_bytes = text.encode(DEFAULT_ENCODING)
    key_bytes = key.encode(DEFAULT_ENCODING)
    result_bytes = bytes([b ^ k for b, k in zip(text_bytes, key_bytes)])
    return result_bytes

def encrypt(text, key):
    if isinstance(text, str):
        return f"{ENC_PREFIX}{(__xor_encrypt_decrypt(text, key)).hex()}"
    else:
        to_enc = "" + text
        return f"{ENC_PREFIX}{(__xor_encrypt_decrypt(to_enc, key)).hex()}"

def decrypt(text, key):
    if isinstance(text, str) and text.startswith(ENC_PREFIX):
        to_dec = text[len(ENC_PREFIX):]
        converted = hex_to_string(to_dec)
        return (__xor_encrypt_decrypt(converted, key)).decode(DEFAULT_ENCODING)
    return text