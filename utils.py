import datetime
import pytz
import requests
import json
import logging
from config import TEXTS

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

def get_prayer_times(city, country=None):
    """Get prayer times for a city using the working HTTPS API"""
    
    # Use HTTPS API with both city and country
    url = "https://api.aladhan.com/v1/timingsByCity"
    
    # Default country if not provided
    if not country:
        # Try to guess country based on common cities
        city_lower = city.lower()
        if city_lower in ['medina', 'madinah', 'makkah', 'mecca', 'riyadh', 'jeddah']:
            country = "Saudi Arabia"
        elif city_lower in ['cairo', 'alexandria']:
            country = "Egypt"
        elif city_lower in ['istanbul', 'ankara']:
            country = "Turkey"
        elif city_lower in ['dubai', 'abu dhabi']:
            country = "UAE"
        elif city_lower in ['doha']:
            country = "Qatar"
        elif city_lower in ['kuwait']:
            country = "Kuwait"
        else:
            country = "Saudi Arabia"  # Default fallback
    
    params = {
        "city": city,
        "country": country,
        "method": 5  # University of Islamic Sciences, Karachi
    }
    
    try:
        logging.info(f"Fetching prayer times for {city}, {country}")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == 200 and "data" in data and "timings" in data["data"]:
                timings = data["data"]["timings"]
                
                # Extract the 5 main prayer times
                prayer_times = {
                    "Fajr": timings.get("Fajr", "05:00"),
                    "Dhuhr": timings.get("Dhuhr", "12:00"),
                    "Asr": timings.get("Asr", "15:30"),
                    "Maghrib": timings.get("Maghrib", "18:00"),
                    "Isha": timings.get("Isha", "19:30")
                }
                
                logging.info(f"✅ Successfully fetched prayer times for {city}, {country}")
                return prayer_times
            else:
                logging.error(f"API returned error: {data}")
        else:
            logging.error(f"HTTP error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error fetching prayer times: {e}")
    except Exception as e:
        logging.error(f"Unexpected error fetching prayer times: {e}")
    
    # If all fails, return None (no fake data)
    logging.error(f"❌ Failed to fetch real prayer times for {city}, {country}")
    return None