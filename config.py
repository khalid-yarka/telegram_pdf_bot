# telegram_pdf_bot/config.py

import os

# Bot token from BotFather
TOKEN = "6514233351:AAFMLJY1uEFDl2F5EBn0eBoWlYCnY_mmoJM"

# Admin Telegram user IDs (list of integers)
ADMIN_IDS = [2094426161]  # replace with your ID(s)

# Admin WhatsApp number for support (without + for clickable link)
ADMIN_WHATSAPP = "252906500599"

# Database file path
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "instance", "bot.db")

# No file size limit - set to None or very large
MAX_FILE_SIZE = None  # No size limit for PDF uploads

# Complete Tags definitions - all in one place
TAGS = [
    "Q/A",
    "Book",
    "Assignment",
    "W_Exam",
    "T1_Exam", 
    "T2_Exam",
    "E_Answered",
    "C_Answered",
    "A_Answered",
    "Exam",
    "Notes",
    "Summary",
    "Chapter Reviews"
]

# Tags that require a year selection
TAGS_REQUIRING_YEAR = ["C_Answered"]

# Years for centralized exams (2010–2025)
YEARS = [str(y) for y in range(2010, 2026)]

# Class options
CLASSES = ["Form 3", "Form 4"]

# Flask webhook settings
WEBHOOK_URL = "https://Zabots1.pythonanywhere.com/" + TOKEN
FLASK_PORT = 5000

# Referral link base
BOT_USERNAME = "Ardayda_bot"

# Reporting settings
REPORT_NOTIFY_UPLOADER = True
REPORT_NOTIFY_ADMINS = True

# Legacy channel (for backward compatibility)
REQUIRED_CHANNEL = "Ardayda_channel"

# Debug mode
DEBUG = True