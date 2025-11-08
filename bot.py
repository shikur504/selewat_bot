import os
import threading
import asyncio
import urllib.request
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask

# ==================== CONFIG ====================
TOKEN = "8229668167:AAFmHYkIfwzTNMa_SzPETJrCJSfE42CPmNA"
DATA_DIR = "./data"           # ← INSIDE PROJECT (ALLOWED)
FILE = os.path.join(DATA_DIR, "total.txt")
WEB_URL = "https://selewat-bot.onrender.com/total"

# LOGGING
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== GLOBAL FILE HANDLING ====================
def ensure_file():
    os.makedirs(DATA_DIR, exist_ok=True)  # ← SAFE: creates ./data
    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            f.write("0")
        logger.info(f"CREATED: {FILE} with 0")
    else:
        logger.info(f"FILE EXISTS: {FILE}")

def load_total():
    try:
        with open(FILE, "r") as f:
            total = int(f.read().strip())
            logger.info(f"LOADED: {total}")
            return total
    except:
        logger.warning("CORRUPTED → STARTING FROM 0")
        save_total(0)
        return 0

def save_total(total):
    try:
        with open(FILE, "w") as f:
            f.write(str(total))
        logger.info(f"SAVED: {total}")
    except Exception as e:
        logger.error(f"SAVE FAILED: {e}")

# ==================== TELEGRAM BOT ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "السلام عليكم ورحمة الله\n\n"
        "SIRULWUJUD SELEWAT BOT\n\n"
        f"**GLOBAL TOTAL**: *{load_total():,}*\n\n"
        "Send any number = counted!\n"
        "Let’s hit 1 billion InshaAllah!",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    if text.startswith('/'):
        return
    try:
        num = int(text)
        if num <= 0:
            return
        name = f"@{update.message.from_user.username}" if update.message.from_user.username else update.message.from_user.full_name
        old = load_total()
        new = old + num
        save_total(new)
        await update.message.reply_text(
            f"{name} added {num:,} Salawat\n"
            f"**GLOBAL TOTAL**: {new:,}"
        )
        logger.info(f"ADDED {num} → {new}")
    except ValueError:
        pass

# ==================== WEB DASHBOARD ====================
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/total')
def total():
    count = load_total()
    return f'''
    <meta http-equiv="refresh" content="10">
    <h1 style="text-align:center; color:#2E8B57;">GLOBAL SELEWAT TOTAL</h1>
    <h2 style="text-align:center; color:#1E90FF; font-size:48px;">{count:,}</h2>
    <p style="text-align:center;">
        <a href="https://t.me/+YOUR_GROUP_LINK">Join Group</a> |
        <a href="https://t.me/sirulwujudselewatbot">@sirulwujudselewatbot</a>
    </p>
    '''

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    flask_app.run(host='0.0.0.0', port=port, use_reloader=False)

# ==================== KEEP-ALIVE ====================
async def keep_alive():
    while True:
        await asyncio.sleep(300)
        try:
            urllib.request.urlopen(WEB_URL, timeout=10)
            logger.info("PING: Keep-alive sent")
        except:
            pass

# ==================== MAIN ====================
if __name__ == "__main__":
    logger.info("SELEWAT BOT STARTING...")
    ensure_file()  # ← Creates ./data/total.txt
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=lambda: asyncio.run(keep_alive()), daemon=True).start()
    
    logger.info("LIVE 24/7 – GLOBAL TOTAL – NO PERMISSION ERRORS!")
    app.run_polling(drop_pending_updates=True)
