#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os

current_path = os.path.dirname(os.path.dirname(__file__))
config_file_path = os.path.join(current_path, "etc", "config.json")
with open(config_file_path, "r") as obj:
    content = obj.read()
config_info = json.loads(content)


config_info.pop("comment")
