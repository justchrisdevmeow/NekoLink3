import requests
import sys
import json
import os
from src.utils import load_config

config = load_config()
BOT_TOKEN = config["bot_token"]
ALLOWED_IDS = config["allowed_user_ids"]

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    try:
        r = requests.get(url, params=params, timeout=35)
        return r.json().get("result", [])
    except:
        return []

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": text[:4096]}, timeout=10)
    except:
        pass
