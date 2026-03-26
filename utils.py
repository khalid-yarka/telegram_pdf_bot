# telegram_pdf_bot/utils.py
# Utility functions for bot: timezone, keyboards, formatting, channel check

import pytz
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import texts
from config import DEBUG, ADMIN_WHATSAPP, BOT_USERNAME

# Somalia timezone
SOMALIA_TZ = pytz.timezone('Africa/Mogadishu')

def get_current_time():
    """Return current time in Somalia timezone (aware datetime)"""
    return datetime.now(SOMALIA_TZ)

def format_date(dt):
    """Format datetime to string with timezone handling (12-hour format)"""
    if dt is None:
        return "Unknown"
    
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return dt
    
    if dt.tzinfo is None:
        dt = SOMALIA_TZ.localize(dt)
    
    return dt.strftime("%Y-%m-%d %I:%M %p")

def format_file_size(bytes_size):
    """Format file size from bytes to human readable format"""
    if bytes_size is None:
        return "Unknown"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def is_telegram_member(bot, user_id, link):
    """Check if user is a member of a Telegram channel/group."""
    try:
        if 't.me/' in link:
            username = link.split('t.me/')[-1]
            if '/' in username:
                username = username.split('/')[0]
        elif link.startswith('@'):
            username = link[1:]
        else:
            username = link
        
        username = username.split('?')[0]
        
        if DEBUG:
            print(f"🔍 Checking membership for user {user_id} in {username}")
        
        member = bot.get_chat_member(f"@{username}", user_id)
        is_member = member.status in ['member', 'administrator', 'creator']
        
        if DEBUG:
            print(f"   Member status: {member.status}, is_member: {is_member}")
        
        return is_member
    except Exception as e:
        if DEBUG:
            print(f"🔍 Channel check failed for {user_id}: {e}")
        return False

def create_main_menu_keyboard(user_id=None):
    """Create main menu keyboard with 2x2 grid layout"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton(texts.BUTTON_UPLOAD),
        KeyboardButton(texts.BUTTON_SEARCH)
    )
    markup.add(
        KeyboardButton(texts.BUTTON_PROFILE),
        KeyboardButton(texts.BUTTON_HELP)
    )
    
    if user_id:
        from database import get_user
        from config import ADMIN_IDS
        user = get_user(user_id)
        is_admin_user = (user and user['is_admin']) or (user_id in ADMIN_IDS)
        if is_admin_user:
            if DEBUG:
                print(f"👑 Adding admin button for user {user_id}")
            markup.add(KeyboardButton(texts.BUTTON_ADMIN))
    
    return markup

def create_cancel_keyboard():
    """Create a simple keyboard with only cancel button"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton(texts.BUTTON_CANCEL))
    return markup

def remove_keyboard():
    """Remove keyboard (hide buttons)"""
    return ReplyKeyboardRemove()
    
def create_subject_keyboard(for_search=False):
    """Create subject selection keyboard with 3 columns for better UI"""
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    
    prefix = "search_subject_" if for_search else "subject_"
    
    for subject in texts.SUBJECTS:
        buttons.append(InlineKeyboardButton(subject, callback_data=f"{prefix}{subject}"))
    
    for i in range(0, len(buttons), 3):
        markup.row(*buttons[i:i+3])
    
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    return markup

def create_tag_keyboard():
    """Create tag selection keyboard with 2 columns for better UI"""
    from config import TAGS
    
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for tag in TAGS:
        buttons.append(InlineKeyboardButton(tag, callback_data=f"tag_{tag}"))
    
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i+2])
    
    markup.row(
        InlineKeyboardButton("⏭️ Skip", callback_data="tag_skip"),
        InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel")
    )
    return markup

def create_search_tag_keyboard():
    """Create tag selection keyboard for search with skip option"""
    from config import TAGS
    
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for tag in TAGS:
        buttons.append(InlineKeyboardButton(tag, callback_data=f"search_tag_{tag}"))
    
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i+2])
    
    markup.row(
        InlineKeyboardButton("⏭️ Skip", callback_data="search_tag_skip"),
        InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel")
    )
    return markup

def create_pdf_action_buttons(pdf_id, user_id, is_admin=False):
    """Create inline keyboard for PDF actions with 2x2 grid layout"""
    import database as db
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    if db.has_liked(pdf_id, user_id):
        like_text = texts.BUTTON_UNLIKE
        like_callback = f"unlike_{pdf_id}"
    else:
        like_text = texts.BUTTON_LIKE
        like_callback = f"like_{pdf_id}"
    
    markup.add(
        InlineKeyboardButton(like_text, callback_data=like_callback),
        InlineKeyboardButton(texts.BUTTON_DOWNLOAD, callback_data=f"download_{pdf_id}")
    )
    
    markup.add(
        InlineKeyboardButton(texts.BUTTON_REPORT, callback_data=f"report_{pdf_id}"),
        InlineKeyboardButton(texts.BUTTON_SHARE, callback_data=f"share_{pdf_id}")
    )
    
    if is_admin:
        markup.add(InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_{pdf_id}"))
    
    return markup

def create_share_buttons(pdf_id, user_id):
    """Create share buttons for Telegram and WhatsApp"""
    share_link = f"https://t.me/{BOT_USERNAME}?start=pdf_{pdf_id}"
    whatsapp_link = f"https://wa.me/?text={share_link.replace('&', '%26')}"
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(texts.BUTTON_SHARE_TELEGRAM, url=f"https://t.me/share/url?url={share_link}&text=📚 Check out this PDF!"),
        InlineKeyboardButton(texts.BUTTON_SHARE_WHATSAPP, url=whatsapp_link)
    )
    markup.add(InlineKeyboardButton(texts.BUTTON_BACK, callback_data=f"view_{pdf_id}"))
    return markup

def create_referral_share_buttons(user_id):
    """Create share buttons for referral link"""
    referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
    whatsapp_link = f"https://wa.me/?text={referral_link.replace('&', '%26')}"
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(texts.BUTTON_SHARE_TELEGRAM, url=f"https://t.me/share/url?url={referral_link}&text=📚 Join Ardayda Educational Bot!"),
        InlineKeyboardButton(texts.BUTTON_SHARE_WHATSAPP, url=whatsapp_link)
    )
    markup.add(
        InlineKeyboardButton("📋 Copy Link", callback_data="copy_referral_link")
    )
    return markup

def create_help_buttons():
    """Create help menu buttons with contact admin"""
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(texts.BUTTON_CONTACT_ADMIN, url=f"https://wa.me/{ADMIN_WHATSAPP}")
    )
    return markup

def create_profile_buttons(user_id):
    """Create profile buttons with share referral option"""
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🔗 Share Referral Link", callback_data="share_referral")
    )
    return markup

def create_pagination_buttons(page, total_pages, callback_prefix, extra_data=None):
    """Create pagination buttons for navigation with better UI"""
    markup = InlineKeyboardMarkup(row_width=3)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"{callback_prefix}_prev_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="ignore"))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"{callback_prefix}_next_{page+1}"))
    
    if nav_buttons:
        markup.row(*nav_buttons)
    
    return markup

def create_region_keyboard(include_manual=True):
    """Create region selection keyboard with 2 columns for better UI"""
    markup = InlineKeyboardMarkup(row_width=2)
    regions = list(texts.form_four_schools_by_region.keys())
    
    for i in range(0, len(regions), 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(regions):
                row_buttons.append(InlineKeyboardButton(regions[i + j], callback_data=f"region_{regions[i + j]}"))
        markup.row(*row_buttons)
    
    if include_manual:
        markup.add(InlineKeyboardButton(texts.BUTTON_REGION_NOT_LISTED, callback_data="manual_region_start"))
    
    return markup

def create_schools_keyboard(schools, region, page=0, page_size=6):
    """Create schools selection keyboard with 2 columns and pagination"""
    total_schools = len(schools)
    total_pages = (total_schools + page_size - 1) // page_size
    start = page * page_size
    end = start + page_size
    page_schools = schools[start:end]
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    for i in range(0, len(page_schools), 2):
        row_buttons = []
        for j in range(2):
            if i + j < len(page_schools):
                row_buttons.append(InlineKeyboardButton(page_schools[i + j], callback_data=f"school_{page_schools[i + j]}"))
        markup.row(*row_buttons)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"schools_page_{region}_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"schools_page_{region}_{page+1}"))
    if nav_buttons:
        markup.row(*nav_buttons)
    
    markup.row(
        InlineKeyboardButton(texts.BUTTON_SCHOOL_NOT_LISTED, callback_data=f"manual_school_{region}"),
        InlineKeyboardButton(texts.BUTTON_BACK, callback_data="back_region")
    )
    
    return markup, total_pages

def create_class_keyboard():
    """Create class selection keyboard with 2 columns"""
    markup = InlineKeyboardMarkup(row_width=2)
    for class_name in texts.CLASSES:
        markup.add(InlineKeyboardButton(class_name, callback_data=f"class_{class_name}"))
    markup.add(InlineKeyboardButton(texts.BUTTON_BACK, callback_data="back_school"))
    return markup

def create_membership_verify_button(requirement_id, req_type):
    """Create verification button for membership"""
    markup = InlineKeyboardMarkup(row_width=1)
    if req_type == 'telegram':
        markup.add(
            InlineKeyboardButton(texts.BUTTON_JOINED, callback_data=f"verify_telegram_{requirement_id}")
        )
    else:
        markup.add(
            InlineKeyboardButton(texts.BUTTON_VERIFY, callback_data=f"verify_whatsapp_{requirement_id}")
        )
    return markup

# ==================== MEMBERSHIP KEYBOARD FUNCTIONS ====================

def create_membership_telegram_button(requirement):
    """Create a join button for Telegram channel/group"""
    link = requirement['link']
    if link.startswith('@'):
        link = f"https://t.me/{link[1:]}"
    elif not link.startswith('http'):
        link = f"https://t.me/{link}"
    
    return InlineKeyboardButton(
        f"📢 Join {requirement['name'][:20]}",
        url=link
    )

def create_membership_whatsapp_buttons(requirement):
    """Create buttons for WhatsApp group (join + confirm)"""
    return [
        InlineKeyboardButton(f"💬 Join {requirement['name'][:15]}", url=requirement['link']),
        InlineKeyboardButton(f"✅ Confirm {requirement['name'][:10]}", callback_data=f"confirm_whatsapp_{requirement['id']}")
    ]

def create_membership_refresh_button():
    """Create refresh status button"""
    return InlineKeyboardButton("🔄 Refresh Status", callback_data="refresh_membership")

def create_membership_continue_button():
    """Create continue to main menu button"""
    return InlineKeyboardButton("🎉 Continue to Main Menu", callback_data="membership_complete")

def create_progress_bar(current, total, length=10):
    """Create a visual progress bar"""
    if total == 0:
        return "░" * length
    
    percent = int((current / total) * 100)
    filled = int(length * percent / 100)
    bar = "█" * filled + "░" * (length - filled)
    return bar

def format_membership_status_text(telegram_reqs, whatsapp_reqs, telegram_joined, whatsapp_joined):
    """Format membership status text for display"""
    total_telegram = len(telegram_reqs)
    total_whatsapp = len(whatsapp_reqs)
    total_joined = telegram_joined + whatsapp_joined
    total_required = total_telegram + total_whatsapp
    
    if total_required == 0:
        return "✅ No membership requirements. You have full access!"
    
    text = "🔐 **MEMBERSHIP REQUIREMENTS**\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    bar = create_progress_bar(total_joined, total_required)
    percent = int((total_joined / total_required) * 100) if total_required > 0 else 0
    text += f"**Progress:** `{bar}` {total_joined}/{total_required} ({percent}%)\n\n"
    
    if telegram_reqs:
        text += "📢 **TELEGRAM CHANNELS/GROUPS** (Auto-detected)\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for req in telegram_reqs:
            if req.get('is_member', False):
                text += f"✅ **{req['name']}** - Joined\n"
            else:
                text += f"❌ **{req['name']}** - Not joined\n"
                text += f"   🔗 `{req['link']}`\n"
        text += "\n"
    
    if whatsapp_reqs:
        text += "💬 **WHATSAPP GROUPS** (Confirm after joining)\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for req in whatsapp_reqs:
            if req.get('is_member', False):
                text += f"✅ **{req['name']}** - Confirmed\n"
            else:
                text += f"❌ **{req['name']}** - Not confirmed\n"
                text += f"   🔗 `{req['link']}`\n"
        text += "\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    if total_joined == total_required:
        text += "🎉 **Congratulations!** You've joined all required communities!\n"
        text += "Click the button below to continue to the main menu.\n\n"
    else:
        text += "⚠️ **Please join all required channels/groups above** to access the bot.\n"
        text += "For WhatsApp groups, click 'Confirm' after joining.\n\n"
    
    return text

def get_pdf_emoji(tag):
    """Get emoji based on PDF tag for better visual"""
    emojis = {
        "Q/A": "❓",
        "Book": "📖",
        "Assignment": "✏️",
        "W_Exam": "📝",
        "T1_Exam": "📝",
        "T2_Exam": "📝",
        "E_Answered": "✅",
        "C_Answered": "✅",
        "A_Answered": "✅",
        "Exam": "📝",
        "Notes": "📘",
        "Summary": "📋",
        "Chapter Reviews": "📚"
    }
    return emojis.get(tag, "📄")