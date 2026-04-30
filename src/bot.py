import requests
import sys
import os
import json

def load_config():
    if getattr(sys, 'frozen', False):
        config_path = os.path.join(os.path.dirname(sys.executable), "config.json")
    else:
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    
    with open(config_path, 'r') as f:
        return json.load(f)

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

def send_file(chat_id, file_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            requests.post(url, files={'document': f}, data={'chat_id': chat_id}, timeout=30)
    except Exception as e:
        send_message(chat_id, f"File send failed: {str(e)}")
