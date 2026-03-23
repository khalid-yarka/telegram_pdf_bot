# telegram_pdf_bot/utils.py
# Utility functions for bot: timezone, keyboards, formatting, channel check

import pytz
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import texts
from config import DEBUG

# Somalia timezone
SOMALIA_TZ = pytz.timezone('Africa/Mogadishu')

def get_current_time():
    return datetime.now(SOMALIA_TZ)

def format_date(dt):
    """Format datetime to string with timezone handling"""
    if dt is None:
        return "Unknown"
    
    # If dt is a string, convert to datetime
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return dt
        
    # If dt is naive (no timezone), localize it
    if dt.tzinfo is None:
        dt = SOMALIA_TZ.localize(dt)
    
    return dt.strftime("%Y-%m-%d %H:%M")

def is_channel_member(bot, user_id, channel):
    """Check if user is a member of the required channel."""
    try:
        member = bot.get_chat_member(f"@{channel}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        if DEBUG:
            print(f"🔍 Channel check failed for {user_id}: {e}")
        return False

def create_main_menu_keyboard():
    """Create main menu keyboard with upload, search, profile, help buttons"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton(texts.BUTTON_UPLOAD),
               KeyboardButton(texts.BUTTON_SEARCH))
    markup.add(KeyboardButton(texts.BUTTON_PROFILE),
               KeyboardButton(texts.BUTTON_HELP))
    return markup

def create_cancel_keyboard():
    """Create a simple keyboard with only cancel button"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton(texts.BUTTON_CANCEL))
    return markup

def create_pdf_action_buttons(pdf_id, user_id, is_admin=False):
    """Create inline keyboard for PDF actions (download, like, report, share)"""
    import database as db
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    if db.has_liked(pdf_id, user_id):
        like_text = texts.BUTTON_UNLIKE
        like_callback = f"unlike_{pdf_id}"
    else:
        like_text = texts.BUTTON_LIKE
        like_callback = f"like_{pdf_id}"
    
    markup.add(InlineKeyboardButton(like_text, callback_data=like_callback),
               InlineKeyboardButton(texts.BUTTON_DOWNLOAD, callback_data=f"download_{pdf_id}"))
    markup.add(InlineKeyboardButton(texts.BUTTON_REPORT, callback_data=f"report_{pdf_id}"),
               InlineKeyboardButton(texts.BUTTON_SHARE, callback_data=f"share_{pdf_id}"))
    
    if is_admin:
        markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data=f"delete_{pdf_id}"))
    
    return markup

def create_pagination_buttons(page, total_pages, callback_prefix):
    """Create pagination buttons for navigation"""
    markup = InlineKeyboardMarkup()
    if page > 0:
        markup.add(InlineKeyboardButton(texts.BUTTON_PREV, callback_data=f"{callback_prefix}_prev_{page-1}"))
    if page < total_pages - 1:
        markup.add(InlineKeyboardButton(texts.BUTTON_NEXT, callback_data=f"{callback_prefix}_next_{page+1}"))
    return markup

def create_region_keyboard(include_manual=True):
    """Create region selection keyboard with optional manual entry button"""
    markup = InlineKeyboardMarkup(row_width=2)
    for region in texts.form_four_schools_by_region.keys():
        markup.add(InlineKeyboardButton(region, callback_data=f"region_{region}"))
    if include_manual:
        markup.add(InlineKeyboardButton(texts.BUTTON_REGION_NOT_LISTED, callback_data="manual_region_start"))
    return markup