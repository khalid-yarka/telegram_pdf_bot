# telegram_pdf_bot/app.py
# Entry point for PythonAnywhere web app

from webhook import app
from database import init_db
from config import DEBUG

if DEBUG:
    print("=" * 50)
    print("🚀 Ardayda Bot WSGI Application Starting...")
    print("=" * 50)

# Initialize database on startup
print("📂 Initializing database...")
init_db()

if DEBUG:
    print("✅ Database initialized successfully")
    print("🌐 Webhook mode: Enabled")
    print("=" * 50)

# Application instance for WSGI server (PythonAnywhere)
application = app

if __name__ == "__main__":
    if DEBUG:
        print("🔧 Running in development mode...")
        print("📍 Starting Flask development server...")
    app.run()