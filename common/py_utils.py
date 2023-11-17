from distutils.util import strtobool
from pathlib import Path
import os
import json
import re


def get_userdata_dict(base_url=None, file='userdata.json'):
    test_data_file = Path(__file__).parent.parent.absolute() / 'data' / file
    with open(test_data_file) as json_file:
        user_data = json.load(json_file)
    test_env = get_reg_exp_match('://(.*?)\.', base_url) if base_url else None
    test_env = 'test' if not test_env else test_env
    return user_data[test_env]


def get_selenium_grid_address():
    return os.getenv('SELENIUM_GRID_ADDR', 'http://host.docker.internal:4444')


def get_headless_selenium():
    return bool(strtobool(os.getenv('HEADLESS', 'True')))


def get_selenium_browser():
    return os.getenv('SELENIUM_BROWSER', 'chrome').casefold()


def get_reg_exp_match(pattern, string):
    match = re.search(pattern, string, re.IGNORECASE)
    title = match.group(1) if match else None
    return title
