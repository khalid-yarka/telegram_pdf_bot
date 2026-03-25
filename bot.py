# telegram_pdf_bot/bot.py
# Main entry point for polling (for local testing)

import telebot
from config import TOKEN, DEBUG, ADMIN_IDS
from handlers import bot
from database import init_db
import admin

if __name__ == "__main__":
    # Initialize database
    if DEBUG:
        print("=" * 50)
        print("🤖 Ardayda Bot Starting (Polling Mode)...")
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
        print("📝 Features:")
        print("   📤 Upload PDFs")
        print("   🔍 Search PDFs")
        print("   👤 Profile with referral")
        print("   🔗 Share PDFs")
        print("   👑 Admin panel")
        print("=" * 50)
        print("Press Ctrl+C to stop")
        print("=" * 50)
        
        bot.polling(none_stop=True, interval=1, timeout=20)
        
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("🛑 Bot stopped by user")
        print("=" * 50)
    except Exception as e:
        print(f"❌ Error: {e}")