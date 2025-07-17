
import logging
import asyncio
from telegram import BotCommand
from telegram.ext import (
    Application,
    PicklePersistence,
)
from handlers import setup_handlers
from jobs import restore_jobs
from config import BOT_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger(__name__)

async def setup_commands(app):
    cmds = [
        BotCommand("start", "ابدأ / Start"),
        BotCommand("today", "مواقيت اليوم / Today's Times"),
        BotCommand("settings", "الإعدادات / Settings"),
        BotCommand("lang", "تغيير اللغة / Change language"),
    ]
    await app.bot.set_my_commands(cmds)

def main():
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
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    main()