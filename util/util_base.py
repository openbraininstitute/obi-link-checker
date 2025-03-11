# Copyright (c) 2024 Blue Brain Project/EPFL
# Copyright (c) 2025 Open Brain Institute
# SPDX-License-Identifier: Apache-2.0

import os
import json
from pathlib import Path


def load_config():
    try:
        def validate_config(config):
            if not config.get('username') or not config.get('password'):
                raise ValueError("Missing 'username' or 'password' in configuration")
            return config
        if os.getenv('CI'):
            print("Running in CI environment (GitHub Actions)")
            username = os.environ.get("OBI_USERNAME")
            password = os.environ.get("OBI_PASSWORD")
            print(f"Retrieved username: {username}")
            print(f"Retrieved password: {password}")
            if not username or not password:
                raise ValueError("OBI_USERNAME OR OBI_PASSWORD is missing")
            config = {
                'username': username,
                'password': password
            }
        else:
            # Running locally, use config.json file
            base_dir = Path(__file__).resolve().parent
            config_path = base_dir / '..' / 'util' / 'config.json'
            if not config_path.exists():
                raise FileNotFoundError(f"Config file not found: {config_path}")
            with config_path.open('r') as f:
                config = json.load(f)

        return validate_config(config)

    except Exception as e:
        print(f"Error loading config: {e}")
        raise




