import json
import os
import sys
import ctypes
import subprocess

def load_config():
    if getattr(sys, 'frozen', False):
        config_path = os.path.join(os.path.dirname(sys.executable), "config.json")
    else:
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    
    with open(config_path, 'r') as f:
        return json.load(f)

def execute_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return output[:4000] if output.strip() else "[No output]"
    except:
        return "[Command failed]"

def show_popup(title, message):
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, message, title, 0)

def show_notification(title, message):
    try:
        from win10toast import ToastNotifier
        ToastNotifier().show_toast(title, message, duration=3)
    except:
        show_popup(title, message)
