# telegram_pdf_bot/config.py

import os

# Bot token from BotFather
TOKEN = "6514233351:AAFMLJY1uEFDl2F5EBn0eBoWlYCnY_mmoJM"

# Admin Telegram user IDs (list of integers)
ADMIN_IDS = [2094426161]

# Admin WhatsApp number for support (without + for clickable link)
ADMIN_WHATSAPP = "252906500599"

# Database file path
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "instance", "bot.db")

# No file size limit - set to None or very large
MAX_FILE_SIZE = None

# ==================== TAG SYSTEM ====================
# Complete Tags definitions - Clean and organized

TAGS = [
    "Book",
    "Exam/Assignment",
    "Question/Answer",
    "Chapters",
    "Notes",
    "Summary",
    "Chapter Reviews",
    "Centerlized",
    "Unclassified"
]

# Tags that require a year selection (only Centerlized)
TAGS_REQUIRING_YEAR = ["Centerlized"]

# Years for centralized exams (2010–2025)
YEARS = [str(y) for y in range(2010, 2026)]

# ==================== CLASS SYSTEM ====================
# Class options for PDFs and user registration

CLASSES = ["Form 3", "Form 4", "Both", "Unclassified"]

# ==================== SUBJECTS ====================
# Subjects for Regular/Unclassified materials

SUBJECTS = [
    "Math",
    "Physics",
    "Chemistry",
    "Biology",
    "ICT",
    "Arabic",
    "Islamic",
    "English",
    "Somali",
    "G.P",
    "Geography",
    "History",
    "Agriculture",
    "Business"
]

# ==================== FLASK WEBHOOK SETTINGS ====================
WEBHOOK_URL = "https://Zabots1.pythonanywhere.com/" + TOKEN
FLASK_PORT = 5000

# ==================== BOT USERNAME ====================
BOT_USERNAME = "Ardayda_bot"

# ==================== REPORTING SETTINGS ====================
REPORT_NOTIFY_UPLOADER = True
REPORT_NOTIFY_ADMINS = True

# ==================== LEGACY (for backward compatibility) ====================
REQUIRED_CHANNEL = "Ardayda_channel"

# ==================== DEBUG MODE ====================
DEBUG = True

# ==================== DEFAULT SETTINGS ====================
# These will be inserted into database on first run

DEFAULT_SETTINGS = {
    'auto_approve_pdfs': '0',
    'notify_admin_on_upload': '1',
    'membership_required': '1',
    'whatsapp_required': '1',
    'whatsapp_reminders': '3',
    'broadcast_enabled': '1',
    'show_admin_name_in_broadcast': '1',
    'search_results_per_page': '5',
    'show_uploader_in_search': '1',
    'welcome_message_enabled': '1',
    'channel_leave_alert': '1',
    'allow_user_delete_pdf': '0',
    # New settings
    'notify_users_new_pdfs': '1',
    'pens_per_referral': '1',
    'pdfs_per_pen': '15',
    'enable_browsing': '1'
}