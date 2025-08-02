import logging
from telegram import Update, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler
)
from config import TYPING_CITY, TEXTS, MAJOR_CITIES
from utils import _, user_lang, today_str, format_timings, get_prayer_times
from keyboards import (
    settings_keyboard,
    main_menu_kb,
    city_selection_keyboard,
    language_keyboard,
    after_city_selection_keyboard
)
from jobs import notify


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message and main menu"""
    lang = user_lang(context)
    await update.message.reply_text(
        _("start", lang, today_str(lang)),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(_("settings", lang), callback_data="settings")]
        ])
    )


async def lang_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Language selection command"""
    lang = user_lang(context)
    await update.message.reply_text(
        _("choose_lang", lang),
        reply_markup=language_keyboard(lang)
    )

async def choose_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show city selection keyboard"""
    query = update.callback_query
    await query.answer()
    lang = user_lang(context)
    await query.edit_message_text(
        _("choose_city", lang),
        reply_markup=city_selection_keyboard(lang)
    )

async def city_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle city selection from inline keyboard"""
    query = update.callback_query
    await query.answer()
    city = query.data.removeprefix("city_")
    await _save_city(update, context, city, "")

async def enter_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt user to enter city name manually"""
    query = update.callback_query
    await query.answer()
    lang = user_lang(context)
    await query.edit_message_text(_("enter_city", lang))
    return TYPING_CITY

async def handle_city_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process manually entered city name"""
    city = update.message.text.strip()
    await _save_city(update, context, city, "")
    return ConversationHandler.END

async def _save_city(update: Update, context: ContextTypes.DEFAULT_TYPE, city: str, country: str):
    """Save city and show prayer times"""
    lang = user_lang(context)
    times = get_prayer_times(city, country)
    
    if not times:
        error_msg = _("error_fetch", lang) + f" ({city})"
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(error_msg)
            except Exception as e:
                # If edit fails, answer the callback and send new message
                await update.callback_query.answer()
                await update.callback_query.message.reply_text(error_msg)
        else:
            await update.message.reply_text(error_msg)
        return

    context.user_data["city"] = city
    context.user_data["country"] = country
    context.user_data["muted"] = False
    chat_id = update.effective_chat.id
    for job in context.application.job_queue.get_jobs_by_name(str(chat_id)):
        job.schedule_removal()
    
    context.job_queue.run_repeating(
        notify,
        interval=60,
        first=10,
        chat_id=chat_id,
        name=str(chat_id),
        data=(city, country)
    )

    text = _("city_saved", lang, city, f" ({country})" if country else "", format_timings(times, lang))
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=after_city_selection_keyboard(lang)
            )
        except Exception as e:
            # If edit fails, answer the callback and send new message
            await update.callback_query.answer()
            await update.callback_query.message.reply_text(
                text,
                parse_mode="Markdown",
                reply_markup=after_city_selection_keyboard(lang)
            )
    else:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=after_city_selection_keyboard(lang)
        )
    
    # Message already sent above with prayer times

async def show_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's prayer times"""
    lang = user_lang(context)
    city = context.user_data.get("city")
    
    if not city:
        await update.message.reply_text(_("no_city", lang))
        return
    
    times = get_prayer_times(city, context.user_data.get("country", ""))
    if not times:
        error_msg = _("error_fetch", lang)
        if update.callback_query:
            await update.callback_query.edit_message_text(error_msg)
        else:
            await update.message.reply_text(error_msg)
        return
    
    # Include city name in the message like _save_city does
    country_text = f" ({context.user_data.get('country', '')})" if context.user_data.get('country') else ""
    message_text = _("city_saved", lang, city, country_text, format_timings(times, lang))
    keyboard = after_city_selection_keyboard(lang)
    
    if update.callback_query:
        # Called from refresh button - edit the existing message
        try:
            await update.callback_query.edit_message_text(
                message_text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            # If edit fails, answer the callback and send new message
            await update.callback_query.answer()
            await update.callback_query.message.reply_text(
                message_text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
    else:
        # Called from /today command - send new message
        await update.message.reply_text(
            message_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings menu"""
    query = update.callback_query
    if query:
        await query.answer()
    
    lang = user_lang(context)
    muted = context.user_data.get("muted", False)
    
    if query:
        await query.edit_message_text(
            _("settings", lang),
            reply_markup=settings_keyboard(lang, muted)
        )
    else:
        await update.message.reply_text(
            _("settings", lang),
            reply_markup=settings_keyboard(lang, muted)
        )

async def open_settings_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle settings button from main menu"""
    await settings(update, context)

async def toggle_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle between Arabic and English"""
    query = update.callback_query
    await query.answer()
    lang = "en" if user_lang(context) == "ar" else "ar"
    context.user_data["lang"] = lang
    
    await query.edit_message_text(
        _("settings", lang),
        reply_markup=settings_keyboard(lang, context.user_data.get("muted", False))
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=_("lang_changed", lang),
        reply_markup=main_menu_kb(lang)
    )

async def set_lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection from inline keyboard"""
    query = update.callback_query
    lang = query.data.removeprefix("set_lang_")
    context.user_data["lang"] = lang
    
    await query.edit_message_text(
        _("settings", lang),
        reply_markup=settings_keyboard(lang, context.user_data.get("muted", False))
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=_("lang_changed", lang),
        reply_markup=main_menu_kb(lang)
    )

async def toggle_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle notifications mute status"""
    query = update.callback_query
    await query.answer()
    context.user_data["muted"] = not context.user_data.get("muted", False)
    await settings(update, context)

async def close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Close the current menu"""
    query = update.callback_query
    await query.answer()
    await query.delete_message()

async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Refresh prayer times"""
    query = update.callback_query
    await query.answer()
    await show_today(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    lang = user_lang(context)
    await update.message.reply_text(
        _("operation_cancelled", lang),
        reply_markup=main_menu_kb(lang)
    )
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors that occur during update processing"""
    import traceback
    
    # Log detailed error information
    logger.error(f"❌ EXCEPTION CAUGHT: {context.error}")
    logger.error(f"❌ EXCEPTION TYPE: {type(context.error)}")
    logger.error(f"❌ TRACEBACK: {traceback.format_exc()}")
    
    if update:
        logger.error(f"❌ UPDATE INFO: {update}")
        if update.message:
            logger.error(f"❌ MESSAGE: {update.message.text}")
        if update.callback_query:
            logger.error(f"❌ CALLBACK: {update.callback_query.data}")
    
    # Try to inform the user about the error
    try:
        if update and update.effective_chat:
            lang = user_lang(context) if context.user_data else "ar"
            error_msg = _("error_fetch", lang) if "error_fetch" in TEXTS else "❌ حدث خطأ / An error occurred"
            
            if update.callback_query:
                try:
                    await update.callback_query.answer()
                    await update.callback_query.message.reply_text(error_msg)
                except:
                    pass
            elif update.message:
                try:
                    await update.message.reply_text(error_msg)
                except:
                    pass
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

def setup_handlers(application):
    """Set up all handlers for the bot"""
    
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(enter_city, pattern="enter_city")],
        states={
            TYPING_CITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city_text),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("lang", lang_cmd))
    application.add_handler(CommandHandler("today", show_today))
    application.add_handler(CommandHandler("settings", open_settings_text))
    
    application.add_handler(MessageHandler(filters.Regex("^📅"), show_today))
    application.add_handler(MessageHandler(filters.Regex("^⚙️"), open_settings_text))
    
    application.add_handler(CallbackQueryHandler(toggle_mute, pattern="toggle_mute"))
    application.add_handler(CallbackQueryHandler(toggle_lang, pattern="toggle_lang"))
    application.add_handler(CallbackQueryHandler(set_lang_callback, pattern=r"^set_lang_"))
    application.add_handler(CallbackQueryHandler(city_selected, pattern=r"^city_.*"))
    application.add_handler(CallbackQueryHandler(close, pattern="close"))
    application.add_handler(CallbackQueryHandler(refresh, pattern="refresh"))
    application.add_handler(CallbackQueryHandler(choose_city, pattern="choose_city"))
    application.add_handler(CallbackQueryHandler(settings, pattern="settings"))
    
    application.add_handler(conv_handler)
    
    # Add error handler
    application.add_error_handler(error_handler)