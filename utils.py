import datetime
import pytz
import requests
from config import API_URL, TEXTS

def _(key: str, lang: str = "ar", *args, **kwargs) -> str:
    """Get localized text"""
    return TEXTS[key][lang].format(*args, **kwargs)

def user_lang(ctx) -> str:
    """Get user's preferred language"""
    if getattr(ctx, "user_data", None):
        return ctx.user_data.get("lang", "ar")
    return "ar"

def today_str(lang: str) -> str:
    """Get today's date string in the specified language"""
    ar_days = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
    en_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    now = datetime.datetime.now(pytz.timezone("Africa/Cairo"))
    day = ar_days[now.weekday()] if lang == "ar" else en_days[now.weekday()]
    return f"{day}, {now.strftime('%d-%m-%Y')}"

def format_timings(times: dict, lang: str) -> str:
    """Format prayer times for display"""
    if lang == "en":
        return (
            f"🌅 **Fajr**: {times['Fajr']}\n"
            f"☀️ **Dhuhr**: {times['Dhuhr']}\n"
            f"🌇 **Asr**: {times['Asr']}\n"
            f"🌆 **Maghrib**: {times['Maghrib']}\n"
            f"🌙 **Isha**: {times['Isha']}"
        )
    return (
        f"🌅 **الفجر**: {times['Fajr']}\n"
        f"☀️ **الظهر**: {times['Dhuhr']}\n"
        f"🌇 **العصر**: {times['Asr']}\n"
        f"🌆 **المغرب**: {times['Maghrib']}\n"
        f"🌙 **العشاء**: {times['Isha']}"
    )

def get_prayer_times(city: str, country: str = "") -> dict | None:
    """Fetch prayer times from API"""
    try:
        r = requests.get(API_URL, params={"city": city, "country": country, "method": 5}, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data["data"]["timings"] if data.get("code") == 200 else None
    except Exception:
        return None