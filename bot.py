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
FILE = "/data/total.txt"
WEB_URL = "https://selewat-bot.onrender.com/total"

# LOGGING
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== FILE HANDLING ====================
def ensure_file():
    if not os.path.exists(FILE):
        save_total(0)
        logger.info(f"CREATED {FILE} with 0")

def load_total():
    try:
        with open(FILE, "r") as f:
            total = int(f.read().strip())
            logger.info(f"LOADED: {total}")
            return total
    except:
        logger.warning("NO FILE → STARTING FROM 0")
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
    logger.info(f"/start from {update.message.from_user.full_name}")
    await update.message.reply_text(
        "السلام عليكم\n\n"
        "SIRULWUJUD SELEWAT BOT\n\n"
        f"Current total: *{load_total():,}*\n\n"
        "Send any number = counted!\n"
        "Let’s hit 1 billion tonight InshaAllah!",
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
            f"{name} added *{num:,}* Salawat\n"
            f"Total: *{new:,}*",
            parse_mode='Markdown'
        )
        logger.info(f"COUNTED: +{num} → {new}")
    except ValueError:
        pass

# ==================== WEB & KEEP-ALIVE ====================
flask_app = Flask(__name__)
@flask_app.route('/total')
def total():
    return f"<h1 style='text-align:center; color:#1E90FF;'>{load_total():,}</h1>"

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), use_reloader=False)

async def keep_alive():
    while True:
        await asyncio.sleep(300)
        try:
            urllib.request.urlopen(WEB_URL, timeout=10)
            logger.info("PING SENT")
        except:
            pass

# ==================== MAIN ====================
if __name__ == "__main__":
    logger.info("STARTING CLEAN...")
    ensure_file()  # CREATE FILE IF MISSING
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=lambda: asyncio.run(keep_alive()), daemon=True).start()
    
    logger.info("LIVE 24/7 – NO CONFLICTS – WILL COUNT!")
    app.run_polling(drop_pending_updates=True)
