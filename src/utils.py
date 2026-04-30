import json
import os
import sys

def load_config():
    if getattr(sys, 'frozen', False):
        config_path = os.path.join(os.path.dirname(sys.executable), "config.json")
    else:
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    
    with open(config_path, 'r') as f:
        return json.load(f)
