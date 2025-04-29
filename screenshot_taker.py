import asyncio
import io
from PIL import ImageGrab
from datetime import datetime
import logging # Import logging

logger = logging.getLogger(__name__) # Get logger

async def take_screenshots(send_photo_func, bot_token, chat_id, interval=300, send_text_func=None):
    """Periodically takes a screenshot and sends it via the send_photo_func."""
    logger.info(f"Starting screenshot taker (interval: {interval}s)...")
    print(f"Starting screenshot taker (interval: {interval}s)...") # Keep print for console startup info
    while True:
        await asyncio.sleep(interval)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        logger.info(f"Taking screenshot at {timestamp}...")
        # print(f"{timestamp} - Taking screenshot...") # Reduce console noise
        try:
            # Capture the full screen
            screenshot = ImageGrab.grab()

            # Save the screenshot to an in-memory bytes buffer
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            buffer.seek(0) # Reset buffer position to the beginning
            file_size = buffer.getbuffer().nbytes
            logger.info(f"Screenshot captured. Size: {file_size} bytes.")
            # print(f"Screenshot captured. Size: {file_size} bytes. Sending...")

            # Send the screenshot using the provided async function
            caption = f"Screenshot taken at {timestamp}"
            try:
                # Use create_task to avoid blocking the loop while sending
                asyncio.create_task(send_photo_func(bot_token, chat_id, buffer, caption, f"screenshot_{timestamp}.png"))
                logger.info("Task created for sending screenshot.")
            except Exception as send_e:
                 logger.error(f"Failed to create task for sending screenshot: {send_e}", exc_info=True)

        except Exception as e:
            logger.error(f"Error taking screenshot: {e}", exc_info=True)
            print(f"Error taking screenshot: {e}") # Keep console print for immediate error visibility
            # Optionally, send a text message about the error if send_text_func is provided
            if send_text_func:
                try:
                    error_message = f"ERROR: Failed to capture screenshot at {timestamp}: {e}"
                    asyncio.create_task(send_text_func(bot_token, chat_id, error_message))
                    logger.info("Task created for sending screenshot error notification.")
                except Exception as notify_e:
                    logger.error(f"Failed to create task for sending screenshot error notification: {notify_e}", exc_info=True) 