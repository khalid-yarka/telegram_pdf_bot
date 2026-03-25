# telegram_pdf_bot/webhook.py
# Flask application for webhook (for PythonAnywhere deployment)

from flask import Flask, request, jsonify
import telebot
from config import TOKEN, DEBUG, WEBHOOK_URL
from handlers import bot
from database import init_db

app = Flask(__name__)

# Initialize database on startup
if DEBUG:
    print("=" * 50)
    print("🌐 Ardayda Bot Webhook Starting...")
    print("=" * 50)

print("📂 Initializing database...")
init_db()

if DEBUG:
    print("✅ Database initialized successfully")
    print(f"🔑 Bot token: {TOKEN[:10]}...")
    print(f"🌐 Webhook URL: {WEBHOOK_URL}")
    print("=" * 50)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates"""
    try:
        # Get update from Telegram
        json_str = request.stream.read().decode('utf-8')
        
        if DEBUG:
            print(f"📨 Received update: {json_str[:200]}...")
        
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        
        if DEBUG:
            print(f"✅ Update processed successfully")
        
        return 'ok', 200
        
    except Exception as e:
        if DEBUG:
            print(f"❌ Error processing update: {e}")
        return 'error', 500

@app.route('/', methods=['GET'])
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'bot': 'Ardayda Bot',
        'version': '2.0',
        'message': 'Bot is running'
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check for monitoring"""
    try:
        # Check database connection
        from database import get_db
        with get_db() as conn:
            conn.execute('SELECT 1')
            db_status = 'connected'
    except Exception as e:
        db_status = f'error: {e}'
    
    return jsonify({
        'status': 'ok',
        'bot': 'Ardayda Bot',
        'token': TOKEN[:10] + '...',
        'webhook_url': WEBHOOK_URL,
        'database': db_status,
        'debug': DEBUG
    }), 200

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    """Set webhook manually"""
    try:
        webhook_url = WEBHOOK_URL
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        
        if DEBUG:
            print(f"🔗 Webhook set to: {webhook_url}")
        
        return jsonify({
            'status': 'success',
            'message': 'Webhook set successfully',
            'url': webhook_url
        }), 200
        
    except Exception as e:
        if DEBUG:
            print(f"❌ Failed to set webhook: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/removewebhook', methods=['GET', 'POST'])
def remove_webhook():
    """Remove webhook manually"""
    try:
        bot.remove_webhook()
        
        if DEBUG:
            print("🔗 Webhook removed")
        
        return jsonify({
            'status': 'success',
            'message': 'Webhook removed successfully'
        }), 200
        
    except Exception as e:
        if DEBUG:
            print(f"❌ Failed to remove webhook: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/getwebhook', methods=['GET'])
def get_webhook():
    """Get current webhook info"""
    try:
        webhook_info = bot.get_webhook_info()
        
        if DEBUG:
            print(f"🔍 Webhook info: {webhook_info}")
        
        return jsonify({
            'status': 'success',
            'url': webhook_info.url,
            'has_custom_certificate': webhook_info.has_custom_certificate,
            'pending_update_count': webhook_info.pending_update_count,
            'last_error_date': webhook_info.last_error_date,
            'last_error_message': webhook_info.last_error_message
        }), 200
        
    except Exception as e:
        if DEBUG:
            print(f"❌ Failed to get webhook info: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def stats():
    """Get bot statistics (for monitoring)"""
    try:
        from database import get_stats
        stats = get_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/info', methods=['GET'])
def info():
    """Get bot info"""
    try:
        bot_info = bot.get_me()
        
        return jsonify({
            'status': 'success',
            'bot': {
                'id': bot_info.id,
                'username': bot_info.username,
                'first_name': bot_info.first_name,
                'is_bot': bot_info.is_bot
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    if DEBUG:
        print("🚀 Starting Flask server...")
        print("📍 Listening on port 5000")
        print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)