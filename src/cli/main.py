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

import logging
import argparse
import getpass

from model.config import Config
import utils.ezcrypt
import api.server as api_server
from utils.logging import setup_logging


setup_logging()
logger = logging.getLogger(__name__)
FORMAT = '[%(asctime)s] (%(filename)s . %(funcName)s :: %(lineno)d) -- %(message)s'

DEFAULT_SALT_LENGTH = 64
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_RELOAD = True

def initialize_parser() -> argparse.ArgumentParser:
    """Initializes the argument parser."""
    parser = argparse.ArgumentParser(
        prog="gemini-content-enrichment",
        description="A python application for demonstrating retail generative pipelines.",
        epilog="\nGoogle Cloud Platform"
    )

    parser.add_argument("-c", "--config", action="store", help="The TOML configuration file.", default="env.toml")
    return parser

def initialize_password_functions(subparsers):
    """Initializes the password functions."""
    # Generate random salt
    subparsers.add_parser('generate-salt', help='Generates a random salt')

    encrypt_password = subparsers.add_parser('encrypt-password',
                                             help='Encrypts password with local salt, not good enough for production environments unless the salt and password are separated.')

    encrypt_password.add_argument("-s", "--salt", help='The salt for the password',
                                  default=utils.ezcrypt.generate_random_string(DEFAULT_SALT_LENGTH))
    

def initialize_api_functions(subparsers):
    """Initializes the API functions."""
    api_server = subparsers.add_parser('api-server', help='Starts the server mode')
    api_server.add_argument("-i", "--ip", help='The ip address to bind the server to.', default=DEFAULT_HOST)
    api_server.add_argument("-p", "--port", help='The port to run the server on', default=DEFAULT_PORT)
    api_server.add_argument("-r", "--reload", help='Reload the server on file changes', default=DEFAULT_RELOAD)
    

def main():
    """The main function of the CLI"""
    logging.basicConfig(filename="gemini-content-enrichment.log", level=logging.INFO, format=FORMAT)
    
    parser = initialize_parser()
    subparsers = parser.add_subparsers(dest="action", help='Command Help')
    initialize_password_functions(subparsers)
    initialize_api_functions(subparsers)
    
    args = parser.parse_args()
    config = Config(args.config)
    
    match args.action:
        case 'encrypt-password':
            password = getpass.getpass(prompt="Enter password: ")
            print("Salt: {}".format(args.salt))
            print("Encrypted Password: {}".format(utils.ezcrypt.encrypt(password, args.salt)))
        case 'generate-salt':
            print("Salt: ", utils.ezcrypt.generate_random_string(DEFAULT_SALT_LENGTH))
        case 'api-server':
            print(f'Starting Server: {args.ip}:{args.port}')
            api_server.start(config, args.ip, args.port, args.reload)

if __name__ == "__main__":
    main()