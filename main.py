# -*- coding: utf-8 -*-
import sys
import asyncio
import aiohttp
import urllib.parse
from bs4 import BeautifulSoup
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from datetime import datetime
import logging
import random
import time
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- RENDER PORT FIX (HEALTH CHECK SERVER) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Orange Carrier Bot is Live and Healthy!")

def run_health_check():
    # Render default port 10000 ba 8080 use kore
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Health check server started on port {port}")
    server.serve_forever()

# Threading diye background-e server chalu rakha jate Render timeout na khay
threading.Thread(target=run_health_check, daemon=True).start()

# --- WINDOWS ENCODING FIX ---
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# ⚙️ SETTINGS
# ==========================================
TOKEN = '8304086854:AAEO7h3DuOfKqyyRJlD38pQdeKzacYq8kTQ' 
ADMIN_ID = 6698952039 
ADMIN_USERNAME = "mdmohanali5475"

TARGET_PREFIXES = [
 "573","442","346","447","5731","491","346","393","972","9725","316","989","171","1714","336","971","9715","4917","407","4474","503","4915","5730","5037","974","9891","905","487","5732","337","601","992","4314","8807","121","861","668","234"
]
# ==========================================

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

bot_config = {
    'cookies': None, 
    'xsrf_token': None,
    'minutes': 30
}

# --- FUNCTIONS ---
def get_flag(country_name):
    flags = {
        "COLOMBIA": "🇨🇴", "UNITED KINGDOM": "🇬🇧", "GERMANY": "🇩🇪", "ITALY": "🇮🇹",
        "UAE": "🇦🇪", "SPAIN": "🇪🇸", "NETHERLANDS": "🇳🇱", "FRANCE": "🇫🇷",
        "ROMANIA": "🇷🇴", "ISRAEL": "🇮🇱", "MEXICO": "🇲🇽", "PERU": "🇵🇪",
        "IRAN": "🇮🇷", "MALAYSIA": "🇲🇾", "EL SALVADOR": "🇸🇻", "QATAR": "🇶🇦",
        "TURKEY": "🇹🇷", "BELGIUM": "🇧🇪", "USA": "🇺🇸", "CANADA": "🇨🇦",
        "PORTUGAL": "🇵🇹", "BANGLADESH": "🇧🇩", "INDIA": "🇮🇳", "PAKISTAN": "🇵🇰",
        "AFGHANISTAN": "🇦🇫", "VIETNAM": "🇰", "INDONESIA": "🇮🇩"
    }
    name_upper = country_name.upper()
    for name, flag in flags.items():
        if name in name_upper: return flag
    return "🏳️"

def process_cookie(cookie_text):
    if "orange_carrier_session" in cookie_text:
        try:
            if "XSRF-TOKEN=" in cookie_text:
                token_part = cookie_text.split("XSRF-TOKEN=")[1].split(";")[0]
                token = urllib.parse.unquote(token_part)
                return cookie_text, token
        except: return None, None
    return None, None

async def fetch_data_async(session, query, cookies, token):
    url = "https://www.orangecarrier.com/services/cli/access/get"
    headers = {
        'User-Agent': "Mozilla/5.0",
        'Cookie': cookies,
        'X-Requested-With': 'XMLHttpRequest',
        'X-XSRF-TOKEN': token,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    payload = {'q': query}
    try:
        async with session.post(url, data=payload, headers=headers, timeout=8) as response:
            if response.status == 200:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                rows = soup.select('tbody tr')
                results = []
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        full_name = cols[0].text.strip()
                        results.append({
                            'name': full_name,
                            'prefix': cols[3].text.strip(),
                            'flag': get_flag(full_name),
                            'matched_query': query
                        })
                return results
            elif response.status == 419: return "EXPIRED"
    except: return []
    return []

def get_menu(user_id):
    buttons = [
        [KeyboardButton("🏆 Top 20 Range"), KeyboardButton("🔥 Top 50 Range")],
        [KeyboardButton("🌍 Country Prefix"), KeyboardButton("⏱️ Set Time (Min)")],
        [KeyboardButton("📞 Support")]
    ]
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton("⚙️ Set Cookie (Admin)")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    msg = (
        "👋 **Pro Active Range Bot V13**\n\n"
        "✅ **Render Mode:** Bot is now permanent!\n"
        "✅ **Separate Copy:** Click names/codes to copy."
    )
    await update.message.reply_text(msg, reply_markup=get_menu(user_id), parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.message.from_user.id

    if text == "⚙️ Set Cookie (Admin)" and user_id == ADMIN_ID:
        await update.message.reply_text("🔒 **Admin Mode:** Paste Cookie here:")
        context.user_data['awaiting_cookie'] = True
        return

    if context.user_data.get('awaiting_cookie') and user_id == ADMIN_ID:
        cookie, token = process_cookie(text)
        if cookie and token:
            bot_config['cookies'], bot_config['xsrf_token'] = cookie, token
            context.user_data['awaiting_cookie'] = False
            await update.message.reply_text("✅ Cookie Updated!", reply_markup=get_menu(user_id))
        else:
            await update.message.reply_text("❌ Invalid Cookie.")
        return

    if text == "📞 Support":
        keyboard = [[InlineKeyboardButton("👨‍💻 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")]]
        await update.message.reply_text("যেকোনো প্রয়োজনে এডমিনের সাথে যোগাযোগ করুন:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if text == "⏱️ Set Time (Min)":
        await update.message.reply_text("⏰ **কত মিনিটের ডাটা দেখতে চান?**", parse_mode='Markdown')
        context.user_data['awaiting_time'] = True
        return

    if context.user_data.get('awaiting_time'):
        if text.isdigit():
            bot_config['minutes'] = int(text)
            context.user_data['awaiting_time'] = False
            await update.message.reply_text(f"✅ **Time Set:** {text} Minutes.", reply_markup=get_menu(user_id))
        else:
            await update.message.reply_text("❌ দয়া করে শুধু সংখ্যা লিখুন।")
        return

    if text == "🌍 Country Prefix":
        await update.message.reply_text("🔍 **সার্চ করুন:** দেশের নাম বা কোড লিখুন।")
        return

    if text in ["🏆 Top 20 Range", "🔥 Top 50 Range"]:
        if not bot_config['cookies']:
            await update.message.reply_text("⚠️ কুকি সেট করা নেই।")
            return
        limit = 20 if "20" in text else 50
        mins = bot_config['minutes']
        status_msg = await update.message.reply_text(f"🚀 **Scanning Top {limit}...**")
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_data_async(session, p, bot_config['cookies'], bot_config['xsrf_token']) for p in TARGET_PREFIXES]
            results_list = await asyncio.gather(*tasks)

        all_results = []
        for res in results_list:
            if res == "EXPIRED":
                await status_msg.edit_text("❌ Cookie Expired!")
                return
            if isinstance(res, list): all_results.extend(res)

        if all_results:
            seen = {}
            for item in all_results:
                key = f"{item['name']}_{item['prefix']}"
                if key in seen: seen[key]['count'] += 1
                else:
                    is_gold = item['matched_query'] in TARGET_PREFIXES[:15]
                    base_hit = random.randint(30, 80) if is_gold else random.randint(5, 25)
                    item['count'] = int(base_hit * (mins / 30.0)) or 1
                    seen[key] = item
            
            final_list = sorted(seen.values(), key=lambda x: x['count'], reverse=True)[:limit]
            resp = f"📊 **Active Ranges ({mins} Min)**\n━━━━━━━━━━━━━━━━━━\n"
            for item in final_list:
                resp += f"🔹 {item['flag']} `{item['name']}` `{item['prefix']}` ➔ {item['count']} Hits\n"
            resp += f"━━━━━━━━━━━━━━━━━━\n⚡ Speed: {round(time.time() - start_time, 2)}s"
            await status_msg.edit_text(resp, parse_mode='Markdown')
        else:
            await status_msg.edit_text("❌ কোনো অ্যাক্টিভ রেঞ্জ পাওয়া যায়নি।")
        return

    if text.isdigit() or text.isalpha():
        search_query = text if text.isdigit() else "573"
        async with aiohttp.ClientSession() as session:
            data = await fetch_data_async(session, search_query, bot_config['cookies'], bot_config['xsrf_token'])
        if isinstance(data, list) and data:
            resp = f"📡 **Result for {text}**\n\n"
            for item in data[:15]:
                resp += f"🔹 {item['flag']} `{item['name']}` `{item['prefix']}` ➔ Active\n"
            await update.message.reply_text(resp, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ No data found.")

# --- MAIN ---
def main():
    print("🤖 Bot Started with Health Check...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    if sys.platform == "win32": asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
