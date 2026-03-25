# telegram_pdf_bot/bot.py
# Main entry point for polling (for local testing)

from config import TOKEN, DEBUG, ADMIN_IDS
from database import init_db
from handlers import Handlers
from admin import Admin
import telebot
import sys

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
    
    # Create bot instance
    bot = telebot.TeleBot(TOKEN)
    
    # Create handlers and admin instances
    handlers = Handlers(bot)
    admin = Admin(bot, handlers)
    handlers.set_admin(admin)
    
    try:
        # Get bot info
        bot_info = bot.get_me()
        print(f"🤖 Bot name: {bot_info.first_name}")
        print(f"📱 Bot username: @{bot_info.username}")
        print(f"🆔 Bot ID: {bot_info.id}")
        print("=" * 50)
        
        # Check webhook status
        print("\n📡 Checking webhook status...")
        print("-" * 30)
        
        try:
            # Get current webhook info
            webhook_info = bot.get_webhook_info()
            
            if webhook_info and webhook_info.url:
                print(f"⚠️ Existing webhook found:")
                print(f"   📍 URL: {webhook_info.url}")
                if webhook_info.last_error_message:
                    print(f"   ❌ Last error: {webhook_info.last_error_message}")
                if webhook_info.pending_update_count:
                    print(f"   📦 Pending updates: {webhook_info.pending_update_count}")
                
                # Ask user for confirmation (only if webhook exists)
                print("\n" + "=" * 50)
                print("⚠️  WARNING: A webhook is currently active!")
                print("   Polling mode cannot run while webhook is active.")
                print("=" * 50)
                
                response = input("❓ Delete webhook and continue? (y/n): ").strip().lower()
                
                if response == 'y' or response == 'yes':
                    print("\n🗑️ Removing existing webhook...")
                    bot.delete_webhook()
                    print("✅ Webhook removed successfully!")
                    print("-" * 30)
                else:
                    print("\n❌ Webhook deletion cancelled.")
                    print("Exiting...")
                    sys.exit(0)
            else:
                print("✅ No active webhook found.")
                print("-" * 30)
        
        except Exception as e:
            print(f"⚠️ Could not check webhook: {e}")
            print("-" * 30)
        
        # Start polling
        print("\n🚀 Bot started polling...")
        print("📝 Features:")
        print("   📤 Upload PDFs")
        print("   🔍 Search PDFs")
        print("   👤 Profile with referral")
        print("   🔗 Share PDFs")
        print("   👑 Admin panel")
        print("=" * 50)
        print("Press Ctrl+C to stop")
        print("=" * 50)
        
        # Start polling (this will block)
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
        
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("🛑 Bot stopped by user")
        print("=" * 50)
    except Exception as e:
        print(f"❌ Error: {e}")