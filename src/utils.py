import json
import os
import sys
import ctypes

def load_config():
    if getattr(sys, 'frozen', False):
        config_path = os.path.join(os.path.dirname(sys.executable), "config.json")
    else:
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    
    with open(config_path, 'r') as f:
        return json.load(f)

def show_popup(title, message):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0)

def show_notification(title, message):
    try:
        from win10toast import ToastNotifier
        ToastNotifier().show_toast(title, message, duration=3)
    except:
        show_popup(title, message)
