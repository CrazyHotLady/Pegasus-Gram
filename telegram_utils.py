import telegram
import asyncio
import logging

logger = logging.getLogger(__name__)

async def send_telegram_message(bot_token: str, chat_id: str, text: str):
    """Sends a text message to the specified Telegram chat using the bot token."""
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        logger.error("Telegram bot token is missing or not configured in config.py")
        print("Error: Telegram bot token is missing or not configured in config.py")
        return
    if not chat_id or chat_id == "YOUR_CHAT_ID_HERE":
        logger.error("Telegram chat ID is missing or not configured in config.py")
        print("Error: Telegram chat ID is missing or not configured in config.py")
        return

    try:
        bot = telegram.Bot(token=bot_token)
        async with bot:
            await bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"Message sent to Telegram chat ID {chat_id}")
    except telegram.error.InvalidToken:
        logger.error("Invalid Telegram Bot Token.", exc_info=True)
        print("Error: Invalid Telegram Bot Token.")
    except telegram.error.TelegramError as e:
        logger.error(f"Error sending Telegram message: {e}", exc_info=True)
        print(f"Error sending Telegram message: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred while sending Telegram message: {e}")
        print(f"An unexpected error occurred while sending Telegram message: {e}")

async def send_telegram_photo(bot_token: str, chat_id: str, photo_buffer, caption: str = "", filename: str = "image.png"):
    """Sends a photo from a buffer to the specified Telegram chat."""
    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        logger.error("Telegram bot token is missing or not configured for photo sending.")
        print("Error: Telegram bot token is missing or not configured for photo sending.")
        return
    if not chat_id or chat_id == "YOUR_CHAT_ID_HERE":
        logger.error("Telegram chat ID is missing or not configured for photo sending.")
        print("Error: Telegram chat ID is missing or not configured for photo sending.")
        return

    try:
        bot = telegram.Bot(token=bot_token)
        async with bot:
            photo_buffer.seek(0)
            await bot.send_photo(chat_id=chat_id, photo=photo_buffer, caption=caption, filename=filename)
        logger.info(f"Photo '{filename}' sent to Telegram chat ID {chat_id}")
    except telegram.error.InvalidToken:
        logger.error("Invalid Telegram Bot Token for photo sending.", exc_info=True)
        print("Error: Invalid Telegram Bot Token for photo sending.")
    except telegram.error.TelegramError as e:
        logger.error(f"Error sending Telegram photo: {e}", exc_info=True)
        print(f"Error sending Telegram photo: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred while sending Telegram photo: {e}")
        print(f"An unexpected error occurred while sending Telegram photo: {e}") 