# telegram_pdf_bot/app.py
from flask import Flask, request
import telebot
from config import TOKEN, DEBUG, WEBHOOK_URL
from database import init_db
from handlers import Handlers
from admin import Admin

app = Flask(__name__)

# Initialize database
init_db()

# Create bot instance
bot = telebot.TeleBot(TOKEN)

# Create handlers and admin instances
handlers = Handlers(bot)
admin = Admin(bot, handlers)
handlers.set_admin(admin)

if DEBUG:
    print("=" * 50)
    print("🌐 Ardayda Bot Webhook Starting...")
    print("=" * 50)
    print(f"🔑 Bot token: {TOKEN[:10]}...")
    print(f"🌐 Webhook URL: {WEBHOOK_URL}")
    print("=" * 50)


@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    """Receive updates from Telegram"""
    try:
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        handlers.bot.process_new_updates([update])
        
        if DEBUG:
            print(f"✅ Update processed")
        
        return 'ok', 200
    except Exception as e:
        if DEBUG:
            print(f"❌ Error: {e}")
        return 'error', 500


@app.route('/', methods=['GET'])
def index():
    return 'Ardayda Bot is running! ✅'


# Set webhook on startup
def set_webhook():
    """Remove existing webhook and set new one"""
    try:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL)
        if DEBUG:
            print(f"✅ Webhook set to: {WEBHOOK_URL}")
        return True
    except Exception as e:
        if DEBUG:
            print(f"❌ Failed to set webhook: {e}")
        return False


# Set webhook when app starts
set_webhook()



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)