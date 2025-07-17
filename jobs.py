import datetime
import pytz
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils import _, user_lang, get_prayer_times
from keyboards import settings_keyboard

async def notify(ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = ctx.job.chat_id
    city, country = ctx.job.data
    lang = user_lang(ctx)
    
    if ctx.application.user_data.get(chat_id, {}).get("muted"):
        return
    
    times = get_prayer_times(city, country)
    if not times:
        return
        
    zone = pytz.timezone("Africa/Cairo")
    now = datetime.datetime.now(zone)
    
    for name, t_str in times.items():
        try:
            athan = datetime.datetime.strptime(t_str, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day, tzinfo=zone
            )
            if 0 < (athan - now).total_seconds() < 60:
                await ctx.bot.send_message(
                    chat_id,
                    _("azan_now", lang, name, city),
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(_("settings", lang), callback_data="settings")]]
                    ),
                )
                return
        except ValueError:
            pass

async def restore_jobs(app):
    for chat_id, data in app.user_data.items():
        city = data.get("city")
        if city:
            app.job_queue.run_repeating(
                notify,
                interval=60,
                first=10,
                chat_id=int(chat_id),
                name=str(chat_id),
                data=(city, data.get("country", "")),
            )