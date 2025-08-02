#!/usr/bin/env python3
"""
Script to clear any webhook and ensure clean bot startup
"""
import asyncio
import logging
from config import BOT_TOKEN
from telegram import Bot
from telegram.error import TelegramError

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def clear_webhook():
    """Clear any existing webhook"""
    if not BOT_TOKEN:
        log.error("❌ BOT_TOKEN is not set")
        return False
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Get current webhook info
        webhook_info = await bot.get_webhook_info()
        log.info(f"🔍 Current webhook URL: {webhook_info.url or 'None'}")
        log.info(f"🔍 Pending updates: {webhook_info.pending_update_count}")
        
        if webhook_info.url:
            log.info("🗑️  Deleting webhook...")
            await bot.delete_webhook(drop_pending_updates=True)
            log.info("✅ Webhook deleted successfully")
        else:
            log.info("✅ No webhook set")
        
        # Clear any pending updates
        log.info("🧹 Clearing pending updates...")
        updates = await bot.get_updates(offset=-1, limit=1)
        if updates:
            last_update_id = updates[0].update_id
            await bot.get_updates(offset=last_update_id + 1, limit=1)
            log.info("✅ Pending updates cleared")
        else:
            log.info("✅ No pending updates")
        
        # Test bot connection
        bot_info = await bot.get_me()
        log.info(f"✅ Bot is ready: @{bot_info.username}")
        
        return True
        
    except TelegramError as e:
        log.error(f"❌ Telegram error: {e}")
        return False
    except Exception as e:
        log.error(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Clearing webhook and preparing bot...")
    print("=" * 40)
    
    success = asyncio.run(clear_webhook())
    
    print("=" * 40)
    if success:
        print("✅ Bot is ready to start!")
        print("You can now run: python3 bot.py")
    else:
        print("❌ Failed to prepare bot")
