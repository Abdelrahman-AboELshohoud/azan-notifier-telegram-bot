import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

TEXTS = {
    "start": {
        "ar": "👋 **مرحباً بك في بوت مواقيت الصلاة!**\n\n📅 {}",
        "en": "👋 **Welcome to the Prayer-Times Bot!**\n\n📅 {}",
    },
    "choose_city": {
        "ar": "🏙️ اختر مدينة أو أدخلها يدوياً:",
        "en": "🏙️ Choose a city or type it manually:",
    },
    "settings": {"ar": "⚙️ الإعدادات", "en": "⚙️ Settings"},
    "choose_lang": {"ar": "اختر لغة:", "en": "Choose language:"},
    "lang_changed": {"ar": "✅ تم تغيير اللغة", "en": "✅ Language changed"},
    "toggle_mute_on": {"ar": "🔕 كتم التنبيهات", "en": "🔕 Mute notifications"},
    "toggle_mute_off": {"ar": "🔔 تفعيل التنبيهات", "en": "🔔 Enable notifications"},
    "close": {"ar": "❌ إغلاق", "en": "❌ Close"},
    "refresh": {"ar": "🔄 تحديث", "en": "🔄 Refresh"},
    "change_city": {"ar": "🔄 تغيير المدينة", "en": "🔄 Change City"},
    "city_saved": {"ar": "✅ تم حفظ **{}**{}\n\n{}", "en": "✅ **{}**{} saved\n\n{}"},
    "no_city": {"ar": "⚠️ حدد مدينة أولاً عبر /start", "en": "⚠️ Please choose a city first via /start"},
    "error_fetch": {"ar": "❌ تعذر جلب البيانات الآن", "en": "❌ Could not fetch data"},
    "enter_city": {"ar": "✏️ أدخل اسم المدينة", "en": "✏️ Enter city name"},
    "choose_from_menu": {"ar": "اختر من القائمة:", "en": "Choose from menu:"},
    "today": {"ar": "📅 مواقيت اليوم", "en": "📅 Today's Times"},
    "azan_now": {"ar": "🔔 **{}** حان الآن في **{}**", "en": "🔔 **{}** time now in **{}**"},
    "back": {"ar": "🔙 رجوع", "en": "🔙 Back"},
}

MAJOR_CITIES = {
    "ar": [
        "مكة المكرمة",
        "المدينة المنورة",
        "الرياض",
        "جدة",
        "القاهرة",
        "الإسكندرية",
        "الجيزة",
        "المنصورة",
        "إسطنبول",
        "أنقرة",
        "إزمير",
        "بورصة",
        "دبي",
        "أبوظبي",
        "الشارقة",
    ],
    "en": [
        "Makkah",
        "Madinah",
        "Riyadh",
        "Jeddah",
        "Cairo",
        "Alexandria",
        "Giza",
        "Mansoura",
        "Istanbul",
        "Ankara",
        "Izmir",
        "Bursa",
        "Dubai",
        "Abu Dhabi",
        "Sharjah",
    ],
}


TYPING_CITY = 1