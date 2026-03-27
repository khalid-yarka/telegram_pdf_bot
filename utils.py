# telegram_pdf_bot/utils.py
# Utility functions for bot: timezone, keyboards, formatting, channel check

import pytz
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import texts
from config import DEBUG, ADMIN_WHATSAPP, BOT_USERNAME, TAGS, CLASSES, SUBJECTS, YEARS

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
        KeyboardButton(texts.BUTTON_BROWSE),
        KeyboardButton(texts.BUTTON_PROFILE)
    )
    markup.add(
        KeyboardButton(texts.BUTTON_SETTINGS),
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

# ==================== UPLOAD KEYBOARDS ====================

def create_class_keyboard():
    """Create class selection keyboard for upload/search"""
    markup = InlineKeyboardMarkup(row_width=2)
    for class_name in CLASSES:
        markup.add(InlineKeyboardButton(class_name, callback_data=f"class_{class_name}"))
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    return markup

def create_subject_keyboard(for_search=False):
    """Create subject selection keyboard with 3 columns"""
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    
    prefix = "search_subject_" if for_search else "subject_"
    
    for subject in SUBJECTS:
        buttons.append(InlineKeyboardButton(subject, callback_data=f"{prefix}{subject}"))
    
    for i in range(0, len(buttons), 3):
        markup.row(*buttons[i:i+3])
    
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    return markup

def create_tag_keyboard():
    """Create tag selection keyboard with 2 columns"""
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    
    for tag in TAGS:
        buttons.append(InlineKeyboardButton(tag, callback_data=f"tag_{tag}"))
    
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i+2])
    
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    return markup

def create_search_tag_keyboard():
    """Create tag selection keyboard for search with skip option"""
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

def create_year_keyboard(for_search=False):
    """Create year selection keyboard (2010-2025) with pagination"""
    markup = InlineKeyboardMarkup(row_width=5)
    prefix = "search_year_" if for_search else "year_"
    
    buttons = []
    for year in YEARS:
        buttons.append(InlineKeyboardButton(year, callback_data=f"{prefix}{year}"))
    
    for i in range(0, len(buttons), 5):
        markup.row(*buttons[i:i+5])
    
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    return markup

# ==================== SEARCH KEYBOARDS ====================

def create_search_class_keyboard():
    """Create class selection keyboard for search with 'All' option"""
    markup = InlineKeyboardMarkup(row_width=2)
    for class_name in CLASSES:
        markup.add(InlineKeyboardButton(class_name, callback_data=f"search_class_{class_name}"))
    markup.add(InlineKeyboardButton("📚 All Classes", callback_data="search_class_all"))
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    return markup

# ==================== PDF ACTION KEYBOARDS ====================

def create_pdf_action_buttons(pdf_id, user_id, is_admin=False, is_approved=False):
    """Create inline keyboard for PDF actions"""
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
        if not is_approved:
            markup.add(InlineKeyboardButton("✅ Approve PDF", callback_data=f"approve_{pdf_id}"))
        markup.add(InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_{pdf_id}"))
    
    return markup

def create_share_buttons(pdf_id, user_id):
    """Create share buttons for Telegram and WhatsApp with embedded referral"""
    share_link = f"https://t.me/{BOT_USERNAME}?start=pdf_{pdf_id}_ref_{user_id}"
    whatsapp_link = f"https://wa.me/?text={share_link.replace('&', '%26')}"
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(texts.BUTTON_SHARE_TELEGRAM, url=f"https://t.me/share/url?url={share_link}&text=📚 Check out this PDF!"),
        InlineKeyboardButton(texts.BUTTON_SHARE_WHATSAPP, url=whatsapp_link)
    )
    markup.add(InlineKeyboardButton(texts.BUTTON_BACK, callback_data=f"view_{pdf_id}"))
    return markup

# ==================== PROFILE & SETTINGS KEYBOARDS ====================

def create_profile_buttons(user_id):
    """Create profile buttons with share referral option"""
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🔗 Share Referral Link", callback_data="share_referral")
    )
    return markup

def create_settings_keyboard(notifications_enabled):
    """Create settings menu keyboard"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    status_text = texts.BUTTON_ON if notifications_enabled else texts.BUTTON_OFF
    markup.add(InlineKeyboardButton(
        f"🔔 New PDF Notifications: {status_text}",
        callback_data="toggle_notifications"
    ))
    markup.add(InlineKeyboardButton(texts.BUTTON_BACK, callback_data="back_to_main"))
    
    return markup

# ==================== BROWSING KEYBOARDS ====================

def create_browsing_keyboard(pdf_id, current_page, total_pages, pens_remaining):
    """Create browsing keyboard with navigation"""
    markup = InlineKeyboardMarkup(row_width=3)
    
    # Navigation buttons
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data="browse_prev"))
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data="browse_next"))
    
    if nav_buttons:
        markup.row(*nav_buttons)
    
    # Action buttons
    markup.row(
        InlineKeyboardButton(texts.BUTTON_DOWNLOAD, callback_data=f"browse_download_{pdf_id}"),
        InlineKeyboardButton(texts.BUTTON_LIKE, callback_data=f"browse_like_{pdf_id}")
    )
    markup.row(
        InlineKeyboardButton(texts.BUTTON_REPORT, callback_data=f"browse_report_{pdf_id}"),
        InlineKeyboardButton("🔄 New Session", callback_data="browse_new")
    )
    markup.add(InlineKeyboardButton(texts.BUTTON_BACK, callback_data="back_to_main"))
    
    return markup

def create_browsing_start_keyboard():
    """Create keyboard for starting browsing session"""
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🎲 Start Browsing", callback_data="browse_start"),
        InlineKeyboardButton(texts.BUTTON_BACK, callback_data="back_to_main")
    )
    return markup

# ==================== NOTIFICATION KEYBOARDS ====================

def create_notification_search_keyboard(subject):
    """Create keyboard for notification search button"""
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(
        texts.NOTIFICATION_SEARCH_BUTTON,
        callback_data=f"notif_search_{subject}"
    ))
    return markup

# ==================== ADMIN KEYBOARDS ====================

def create_admin_back_button(back_callback="admin_back"):
    """Create simple back button for admin panels"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(texts.BUTTON_BACK, callback_data=back_callback))
    return markup

def create_admin_pdf_management_keyboard():
    """Create PDF management menu keyboard"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📊 All PDFs", callback_data="admin_pdfs_all"),
        InlineKeyboardButton("🏷️ By Tag", callback_data="admin_pdfs_by_tag")
    )
    markup.add(
        InlineKeyboardButton("🎓 By Class", callback_data="admin_pdfs_by_class"),
        InlineKeyboardButton("👤 By Uploader", callback_data="admin_pdfs_by_uploader")
    )
    markup.add(
        InlineKeyboardButton("📅 By Date", callback_data="admin_pdfs_by_date"),
        InlineKeyboardButton("⏳ Pending", callback_data="admin_pending")
    )
    markup.add(
        InlineKeyboardButton("🔍 Search by ID", callback_data="admin_pdfs_search"),
        InlineKeyboardButton("📤 Export CSV", callback_data="admin_pdfs_export")
    )
    markup.add(InlineKeyboardButton(texts.BUTTON_BACK, callback_data="admin_back"))
    return markup

def create_admin_pagination_buttons(page, total_pages, callback_prefix, extra_data=None):
    """Create pagination buttons for admin panels with back button"""
    markup = InlineKeyboardMarkup(row_width=3)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"{callback_prefix}_page_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="ignore"))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"{callback_prefix}_page_{page+1}"))
    
    if nav_buttons:
        markup.row(*nav_buttons)
    
    markup.add(InlineKeyboardButton(texts.BUTTON_BACK, callback_data=callback_prefix.replace("_list", "_back")))
    
    return markup

def create_admin_user_list_keyboard(users, page=0, total_pages=1):
    """Create user list keyboard with pagination"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    for user in users:
        status = "🚫" if user['is_banned'] else "✅"
        role = "👑" if user['is_admin'] else "👤"
        name = user['full_name'][:25] if user['full_name'] else f"User_{user['user_id']}"
        markup.add(InlineKeyboardButton(
            f"{status} {role} {name}",
            callback_data=f"admin_user_details_{user['user_id']}"
        ))
    
    # Pagination
    if total_pages > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"admin_users_page_{page-1}"))
        nav_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="ignore"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"admin_users_page_{page+1}"))
        markup.row(*nav_buttons)
    
    markup.add(InlineKeyboardButton(texts.BUTTON_BACK, callback_data="admin_back"))
    return markup

# ==================== REGISTRATION KEYBOARDS ====================

def create_region_keyboard(include_manual=True):
    """Create region selection keyboard with 2 columns"""
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
    
    # Pagination
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

# ==================== HELP KEYBOARDS ====================

def create_help_buttons():
    """Create help menu buttons with contact admin"""
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(texts.BUTTON_CONTACT_ADMIN, url=f"https://wa.me/{ADMIN_WHATSAPP}?text=Hello, I need help with Ardayda Bot. My user ID is:")
    )
    markup.add(InlineKeyboardButton(texts.BUTTON_BACK, callback_data="back_to_main"))
    return markup

# ==================== REFERRAL KEYBOARDS ====================

def create_referral_share_buttons(user_id):
    """Create share buttons for referral link"""
    referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
    whatsapp_link = f"https://wa.me/?text={referral_link.replace('&', '%26')}"
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(texts.BUTTON_SHARE_TELEGRAM, url=f"https://t.me/share/url?url={referral_link}&text=📚 Join Ardayda Educational Bot! Get educational PDFs for free! 🎓"),
        InlineKeyboardButton(texts.BUTTON_SHARE_WHATSAPP, url=whatsapp_link)
    )
    markup.add(
        InlineKeyboardButton("📋 Copy Link", callback_data="copy_referral_link"),
        InlineKeyboardButton(texts.BUTTON_BACK, callback_data="back_to_profile")
    )
    return markup

# ==================== MEMBERSHIP KEYBOARDS ====================

def create_membership_keyboard(status):
    """Create keyboard for membership requirements - sequential flow"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    if not status['all_joined'] and status['next_requirement']:
        req = status['next_requirement']
        
        if req['type'] == 'telegram':
            link = req['link']
            if link.startswith('@'):
                link = f"https://t.me/{link[1:]}"
            elif not link.startswith('http'):
                link = f"https://t.me/{link}"
            
            markup.add(InlineKeyboardButton(
                f"📢 Join {req['name'][:30]}",
                url=link
            ))
        else:  # whatsapp
            markup.add(InlineKeyboardButton(
                f"💬 Join {req['name'][:30]}",
                url=req['link']
            ))
            markup.add(InlineKeyboardButton(
                f"✅ I've Joined - Confirm",
                callback_data=f"confirm_whatsapp_{req['id']}"
            ))
    
    # Always show check status button
    markup.add(InlineKeyboardButton("🔄 Check Status", callback_data="refresh_membership"))
    
    # Continue button if all joined
    if status['all_joined'] and status['total_required'] > 0:
        markup.add(InlineKeyboardButton("🎉 Continue to Main Menu", callback_data="membership_complete"))
    
    # Cancel button to go back
    if status['total_required'] > 0:
        markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel"))
    
    return markup

# ==================== PAGINATION UTILITIES ====================

def create_pagination_buttons(page, total_pages, callback_prefix):
    """Create generic pagination buttons"""
    if total_pages <= 1:
        return None
    
    markup = InlineKeyboardMarkup(row_width=3)
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"{callback_prefix}_prev_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="ignore"))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"{callback_prefix}_next_{page+1}"))
    
    markup.row(*nav_buttons)
    return markup

# ==================== PROGRESS BAR ====================

def create_progress_bar(current, total, length=10):
    """Create a visual progress bar"""
    if total == 0:
        return "░" * length
    
    percent = int((current / total) * 100)
    filled = int(length * percent / 100)
    bar = "█" * filled + "░" * (length - filled)
    return bar

# ==================== EMOJI HELPERS ====================

def get_pdf_emoji(tag):
    """Get emoji based on PDF tag for better visual"""
    emojis = {
        "Book": "📖",
        "Exam/Assignment": "📝",
        "Question/Answer": "❓",
        "Chapters": "📑",
        "Notes": "📘",
        "Summary": "📋",
        "Chapter Reviews": "📚",
        "Centerlized": "🎯",
        "Unclassified": "📄"
    }
    return emojis.get(tag, "📄")

def get_class_emoji(pdf_class):
    """Get emoji based on class"""
    emojis = {
        "Form 3": "🎓",
        "Form 4": "🎓",
        "Both": "🔄",
        "Unclassified": "❓"
    }
    return emojis.get(pdf_class, "📚")