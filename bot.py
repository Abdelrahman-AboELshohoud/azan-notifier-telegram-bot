
import logging
import asyncio
import sys
import os
import subprocess
from telegram import BotCommand
from telegram.ext import (
    Application,
    PicklePersistence,
)
from telegram.error import TelegramError, NetworkError, TimedOut
from handlers import setup_handlers
from jobs import restore_jobs
from config import BOT_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger(__name__)

async def setup_commands(app):
    """Setup bot commands and validate token"""
    try:
        # Test bot connection
        bot_info = await app.bot.get_me()
        log.info(f"✅ Bot connected successfully: @{bot_info.username}")
        
        # Check if webhook is set and delete it if needed
        webhook_info = await app.bot.get_webhook_info()
        if webhook_info.url:
            log.warning(f"⚠️  Webhook is set: {webhook_info.url}")
            log.warning("Deleting webhook to use polling...")
            await app.bot.delete_webhook()
            log.info("✅ Webhook deleted")
        
        # Set bot commands
        cmds = [
            BotCommand("start", "ابدأ / Start"),
            BotCommand("today", "مواقيت اليوم / Today's Times"),
            BotCommand("settings", "الإعدادات / Settings"),
            BotCommand("lang", "تغيير اللغة / Change language"),
        ]
        await app.bot.set_my_commands(cmds)
        log.info("✅ Bot commands set successfully")
        
    except TelegramError as e:
        log.error(f"❌ Failed to setup bot: {e}")
        if "Unauthorized" in str(e):
            log.error("Bot token is invalid. Please check your BOT_TOKEN in .env")
        raise
    except Exception as e:
        log.error(f"❌ Unexpected error during bot setup: {e}")
        raise

async def validate_bot_token():
    """Validate the bot token before starting"""
    if not BOT_TOKEN:
        log.error("❌ BOT_TOKEN is not set in .env file")
        log.error("Please add your bot token to the .env file: BOT_TOKEN=your_bot_token_here")
        return False
    
    try:
        from telegram import Bot
        bot = Bot(token=BOT_TOKEN)
        bot_info = await bot.get_me()
        log.info(f"✅ Bot connected successfully: @{bot_info.username}")
        
        # Check if webhook is set
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url:
            log.warning(f"⚠️  Webhook is set: {webhook_info.url}")
            log.warning("Deleting webhook to use polling...")
            await bot.delete_webhook()
            log.info("✅ Webhook deleted")
        
        return True
        
    except TelegramError as e:
        log.error(f"❌ Telegram API Error: {e}")
        if "Unauthorized" in str(e):
            log.error("This usually means the bot token is invalid")
        return False
    except Exception as e:
        log.error(f"❌ Unexpected error during token validation: {e}")
        return False

def check_existing_process():
    """Check if another bot instance is already running"""
    try:
        # Get current process ID
        current_pid = os.getpid()
        
        # Find other bot processes
        result = subprocess.run(
            ["pgrep", "-f", "python.*bot.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pids = [int(pid) for pid in result.stdout.strip().split('\n') if pid.strip()]
            other_pids = [pid for pid in pids if pid != current_pid]
            
            if other_pids:
                log.error(f"❌ Another bot instance is running (PID: {other_pids[0]})")
                log.error("Please stop the other instance first:")
                log.error(f"kill {other_pids[0]}")
                return False
        
        return True
    except Exception as e:
        log.warning(f"⚠️  Could not check for existing processes: {e}")
        return True  # Continue anyway

def main():
    """Main function with improved error handling"""
    
    # Check for existing bot processes
    if not check_existing_process():
        sys.exit(1)
    
    # Basic token check without async validation
    if not BOT_TOKEN:
        log.error("❌ BOT_TOKEN is not set in .env file")
        log.error("Please add your bot token to the .env file: BOT_TOKEN=your_bot_token_here")
        sys.exit(1)
    
    log.info("🚀 Starting Azan Time Bot...")
    
    try:
        persistence = PicklePersistence("bot_data.pickle")
        app = (
            Application.builder()
            .token(BOT_TOKEN)
            .persistence(persistence)
            .post_init(setup_commands)
            .build()
        )

        app.job_queue.run_once(
            lambda ctx: asyncio.create_task(restore_jobs(ctx.application)), when=1
        )

        setup_handlers(app)
        
        log.info("✅ Bot setup complete. Starting polling...")
        
        # Run with better error handling and retry logic
        app.run_polling(
            allowed_updates=None,
            drop_pending_updates=True,
            close_loop=False
        )
        
    except KeyboardInterrupt:
        log.info("🛑 Bot stopped by user")
    except NetworkError as e:
        log.error(f"❌ Network error: {e}")
        log.error("Please check your internet connection and try again")
        sys.exit(1)
    except TimedOut as e:
        log.error(f"❌ Request timed out: {e}")
        log.error("This might be a temporary issue. Please try again")
        sys.exit(1)
    except TelegramError as e:
        log.error(f"❌ Telegram API error: {e}")
        if "Unauthorized" in str(e):
            log.error("Bot token is invalid. Please check your BOT_TOKEN in .env")
        elif "Conflict" in str(e):
            log.error("Another instance of the bot is already running or webhook is set")
            log.error("Solutions:")
            log.error("1. Kill other bot instances: pkill -f 'python.*bot.py'")
            log.error("2. Clear webhook: python3 clear_webhook.py")
            log.error("3. Wait a few seconds and try again")
        sys.exit(1)
    except Exception as e:
        log.error(f"❌ Unexpected error: {e}")
        log.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()