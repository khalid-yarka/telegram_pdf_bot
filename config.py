# telegram_pdf_bot/config.py

import os

# Bot token from BotFather
TOKEN = "6514233351:AAFMLJY1uEFDl2F5EBn0eBoWlYCnY_mmoJM"

# Admin Telegram user IDs (list of integers)
ADMIN_IDS = [2094426161]  # replace with your ID(s)

# Database file path
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "instance", "bot.db")

# Maximum file size for PDF uploads (in bytes)
MAX_FILE_SIZE = 10000 * 1024 * 1024  # 50 MB

# Tags definitions (short, understandable)
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
]

# Tags that require a year selection
TAGS_REQUIRING_YEAR = ["C_Answered"]

# Years for centralized exams (2010–2025)
YEARS = [str(y) for y in range(2010, 2026)]

# Class options
CLASSES = ["Form 3", "Form 4"]

# Flask webhook settings (for PythonAnywhere)
WEBHOOK_URL = "https://Zabots1.pythonanywhere.com/" + TOKEN
FLASK_PORT = 5000

# Referral link base (your bot's username)
BOT_USERNAME = "Ardeyda_bot"  # without @

# Reporting: whether to notify uploader and admins
REPORT_NOTIFY_UPLOADER = True
REPORT_NOTIFY_ADMINS = True

# Channel that users must join to use the bot (without @)
REQUIRED_CHANNEL = "Ardeyda_channel"

# Debug mode: set to True to enable print messages in terminal, False to disable
DEBUG = True