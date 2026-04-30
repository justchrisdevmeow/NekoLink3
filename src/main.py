import time
from .bot import get_updates, send_message, BOT_TOKEN, ALLOWED_IDS
from .commands import handle_exec, handle_info, handle_ps, handle_notify, handle_popup

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
                
                if cmd == "/start":
                    send_message(chat_id, "NekoLink3 Active\nCommands: /exec, /info, /ps, /notify, /popup, /shutdown, /restart")
                elif cmd == "/exec" and len(parts) > 1:
                    handle_exec(chat_id, " ".join(parts[1:]), send_message)
                elif cmd == "/info":
                    handle_info(chat_id, send_message)
                elif cmd == "/ps":
                    handle_ps(chat_id, send_message)
                elif cmd == "/notify" and len(parts) > 1:
                    handle_notify(chat_id, " ".join(parts[1:]), send_message)
                elif cmd == "/popup" and len(parts) > 1:
                    handle_popup(chat_id, " ".join(parts[1:]), send_message)
                elif cmd == "/shutdown":
                    send_message(chat_id, "Shutting down in 10 seconds...")
                    import os
                    os.system("shutdown /s /t 10")
                elif cmd == "/restart":
                    send_message(chat_id, "Restarting in 10 seconds...")
                    import os
                    os.system("shutdown /r /t 10")
                else:
                    send_message(chat_id, "Unknown command")
        
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
