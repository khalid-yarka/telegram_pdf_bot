# telegram_pdf_bot/bot.py
# Main entry point for polling (for local testing)

import telebot
from config import TOKEN, DEBUG, ADMIN_IDS
from handlers import bot
from database import init_db

if __name__ == "__main__":
    # Initialize database
    if DEBUG:
        print("=" * 50)
        print("🤖 Ardayda Bot Starting...")
        print("=" * 50)
    
    print("📂 Initializing database...")
    init_db()
    
    if DEBUG:
        print("✅ Database initialized successfully")
        print(f"🔑 Bot token: {TOKEN[:10]}...")
        print(f"👑 Admins: {ADMIN_IDS}")
        print("=" * 50)
    
    try:
        bot_info = bot.get_me()
        print(f"🤖 Bot name: {bot_info.first_name}")
        print(f"📱 Bot username: @{bot_info.username}")
        print(f"🆔 Bot ID: {bot_info.id}")
        print("=" * 50)
        print("🚀 Bot started polling...")
        print("Press Ctrl+C to stop")
        print("=" * 50)
        
        bot.polling(none_stop=True, interval=1, timeout=20)
        
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("🛑 Bot stopped by user")
        print("=" * 50)
    except Exception as e:
        print(f"❌ Error: {e}")