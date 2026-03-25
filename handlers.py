# telegram_pdf_bot/handlers.py
# All message and callback handlers

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from config import TOKEN, ADMIN_IDS, TAGS, TAGS_REQUIRING_YEAR, YEARS, CLASSES, BOT_USERNAME, REQUIRED_CHANNEL, MAX_FILE_SIZE, DEBUG, ADMIN_WHATSAPP
import database as db
import texts
import utils
import admin
import pytz
from datetime import datetime, timedelta


bot = telebot.TeleBot(TOKEN)

if DEBUG:
    print("🤖 Initializing Ardayda Bot handlers...")
    print(f"✅ Bot token loaded: {TOKEN[:10]}...")
    print(f"✅ Admin IDs: {ADMIN_IDS}")
    print(f"✅ Debug mode: ON")

# ==================== Helper Functions ====================

def is_admin(user_id):
    return user_id in ADMIN_IDS or (db.get_user(user_id) and db.get_user(user_id)['is_admin'])


def get_user_or_none(user_id):
    user = db.get_user(user_id)
    if user and user['is_banned']:
        bot.send_message(user_id, texts.ACCOUNT_SUSPENDED)
        return None
    return user 
    
def show_main_menu(user_id):
    """Send the main menu to a registered user."""
    user = db.get_user(user_id)
    if user:
        if DEBUG:
            print(f"📱 Showing main menu to user {user_id} (admin: {user['is_admin']})")
        bot.send_message(
            user_id, 
            texts.HOME_WELCOME.format(name=user['full_name'].split()[0] if user['full_name'] else "User"),
            parse_mode='Markdown', 
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )
    else:
        bot.send_message(
            user_id, 
            texts.HOME_WELCOME.format(name="User"),
            parse_mode='Markdown', 
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )


def check_all_memberships(user_id):
    """Check if user meets all membership requirements"""
    requirements = db.get_requirements(active_only=True)
    
    if not requirements:
        return True, None
    
    for req in requirements:
        if req['type'] == 'telegram':
            if not utils.is_telegram_member(bot, user_id, req['link']):
                return False, req
        else:  # whatsapp
            if not db.is_whatsapp_verified(user_id, req['id']):
                return False, req
    
    return True, None

def require_membership(func):
    """Decorator to check if user is a member of all required channels/groups."""
    def wrapper(message_or_call, *args, **kwargs):
        user_id = message_or_call.from_user.id if hasattr(message_or_call, 'from_user') else message_or_call.message.from_user.id
        
        # Check if user is registered
        user = db.get_user(user_id)
        if not user:
            return func(message_or_call, *args, **kwargs)
        
        # Check all memberships
        all_met, missing = check_all_memberships(user_id)
        
        if not all_met:
            if DEBUG:
                print(f"🔒 User {user_id} missing membership: {missing['name']}")
            admin.send_membership_required_message(bot, user_id, missing)
            return
        
        return func(message_or_call, *args, **kwargs)
    return wrapper

def notify_referrer(referrer_id, new_user_id, new_user_name):
    """Notify the referrer that someone used their link"""
    referrer = db.get_user(referrer_id)
    if not referrer:
        return
    
    stats = db.get_user_referral_stats(referrer_id)
    total = stats['conversions']
    
    try:
        bot.send_message(
            referrer_id,
            texts.USER_REFERRAL_NOTIFICATION.format(
                new_user_name=new_user_name,
                total=total
            ),
            parse_mode='Markdown'
        )
        if DEBUG:
            print(f"📢 Referral notification sent to {referrer_id}")
    except Exception as e:
        if DEBUG:
            print(f"❌ Failed to send referral notification: {e}")
    
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(
                admin_id,
                texts.ADMIN_REFERRAL_NOTIFICATION.format(
                    referrer_name=referrer['full_name'],
                    referrer_id=referrer_id,
                    new_user_name=new_user_name,
                    new_user_id=new_user_id,
                    date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    total=total
                ),
                parse_mode='Markdown'
            )
        except:
            pass

# ==================== Start & Registration ====================

@bot.message_handler(commands=['restore'])
def restore_command(message):
    """Clear user state and return to main menu"""
    user_id = message.from_user.id
    db.clear_user_state(user_id)
    
    if DEBUG:
        print(f"🔄 User {user_id} used /restore - state cleared")
    
    bot.send_message(
        user_id,
        "✅ *State Restored!*\n\nYou've been returned to the main menu.",
        parse_mode='Markdown',
        reply_markup=utils.create_main_menu_keyboard(user_id)
    )

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    args = message.text.split()
    start_param = args[1] if len(args) > 1 else None
    
    if DEBUG:
        print(f"🚀 /start from user {user_id}, param: {start_param}")

    user = db.get_user(user_id)
    
    if user and not user['is_banned']:
        if DEBUG:
            print(f"👤 Existing user {user_id} logged in")
        
        all_met, missing = check_all_memberships(user_id)
        if not all_met:
            admin.send_membership_required_message(bot, user_id, missing)
            return
        
        if start_param and start_param.startswith('pdf_'):
            pdf_id = start_param.split('_')[1]
            handle_pdf_share(user_id, pdf_id)
        elif start_param and start_param.startswith('ref_'):
            bot.send_message(
                user_id, 
                "✅ You are already registered!\n\nUse the menu below to explore.",
                reply_markup=utils.create_main_menu_keyboard(user_id)
            )
        else:
            show_main_menu(user_id)
        return

    # New user registration
    referred_by = None
    if start_param and start_param.startswith('ref_'):
        referrer_id = start_param.split('_')[1]
        referrer = db.get_user(referrer_id)
        if referrer and referrer['user_id'] != user_id:
            referred_by = referrer['user_id']
            bot.send_message(referrer_id,"**🚸 Someone Used Your Referral Link**",parse_mode='Markdown')
            if DEBUG:
                print(f"🔗 New user {user_id} referred by {referrer_id}")

    pending_pdf = None
    if start_param and start_param.startswith('pdf_'):
        pending_pdf = start_param.split('_')[1]

    db.set_user_state(user_id, 'register', {
        'step': 'name',
        'referred_by': referred_by,
        'pending_pdf': pending_pdf
    })
    
    bot.send_message(
        user_id, 
        texts.REG_NAME, 
        parse_mode='Markdown'
    )
    
    if DEBUG:
        print(f"📝 New registration started for user {user_id}")

# ==================== Contact Handler ====================

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = message.from_user.id
    current_state, data = db.get_user_state(user_id)
    
    if current_state == 'register' and data and data.get('step') == 'phone':
        phone = message.contact.phone_number
        data['phone'] = phone
        data['step'] = 'region'
        db.set_user_state(user_id, 'register', data)
        
        if DEBUG:
            print(f"📞 Phone received for user {user_id}: {phone}")
        
        bot.send_message(
            user_id, 
            texts.REG_REGION, 
            parse_mode='Markdown',
            reply_markup=utils.create_region_keyboard()
        )

# ==================== Document Handler ====================

@bot.message_handler(content_types=['document'])
def handle_document(message):
    """Handle PDF document uploads"""
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if user and user['is_banned']:
        bot.send_message(user_id, texts.ACCOUNT_SUSPENDED)
        return
    
    if not user:
        bot.send_message(user_id, "❌ Please register first using /start")
        return
    
    all_met, missing = check_all_memberships(user_id)
    if not all_met:
        admin.send_membership_required_message(bot, user_id, missing)
        return
    
    current_state, data = db.get_user_state(user_id)
    
    if current_state == 'upload' and data and data.get('step') == 'waiting_for_file':
        handle_upload_pdf(message, data)
    else:
        # Check if it's a PDF
        if message.document.mime_type != 'application/pdf':
            bot.send_message(
                user_id,
                "❌ Please send a valid *PDF document*.\n\nSend /cancel to cancel.",
                parse_mode='Markdown'
            )
            return
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ Yes, Upload", callback_data="confirm_upload"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        )
        
        db.set_user_state(user_id, 'pending_upload', {
            'file_id': message.document.file_id,
            'file_name': message.document.file_name,
            'file_size': message.document.file_size
        })
        
        bot.send_message(
            user_id,
            f"📄 *Document Received:* `{message.document.file_name}`\n\n"
            f"Do you want to upload this as a PDF?\n\n"
            f"📦 Size: {utils.format_file_size(message.document.file_size)}",
            parse_mode='Markdown',
            reply_markup=markup
        )

# ==================== Main Message Handler ====================
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if user and user['is_banned']:
        bot.send_message(user_id, texts.ACCOUNT_SUSPENDED)
        return
    
    # Update last active for registered users
    if user and not user['is_banned']:
        db.update_user_activity(user_id)

    current_state, data = db.get_user_state(user_id)
    
    if DEBUG:
        print(f"📨 Message from {user_id}: {message.text if message.text else '[non-text]'}, state={current_state}")
    
    # Handle admin flows
    if current_state == 'add_requirement':
        admin.process_add_requirement(bot, user_id, message)
        return
    
    if current_state == 'edit_requirement':
        admin.process_edit_requirement(bot, user_id, message)
        return
    
    # Handle registration flow
    if current_state == 'register':
        handle_registration(message, data)
        return
    
    # Handle cancel
    if message.text and message.text.lower() == texts.BUTTON_CANCEL.lower():
        db.clear_user_state(user_id)
        bot.send_message(
            user_id, 
            texts.CANCELLED, 
            parse_mode='Markdown',
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )
        return
    
    # For registered users, check membership
    if user and not user['is_banned']:
        all_met, missing = check_all_memberships(user_id)
        if not all_met:
            admin.send_membership_required_message(bot, user_id, missing)
            return
    
    # Handle other states
    if current_state == 'upload':
        if data and data.get('step') == 'waiting_for_file':
            if message.document and message.document.mime_type == 'application/pdf':
                handle_upload_pdf(message, data)
            else:
                bot.send_message(
                    user_id,
                    texts.UPLOAD_INVALID_FILE,
                    parse_mode='Markdown',
                    reply_markup=utils.create_cancel_keyboard()
                )
        else:
            db.clear_user_state(user_id)
            bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard(user_id))
    
    elif current_state == 'search':
        handle_search(message, data)
    
    elif current_state == 'report':
        handle_report(message, data)
    
    elif current_state == 'admin_broadcast':
        handle_admin_broadcast(message, data)
    
    elif current_state == 'admin_sql':
        handle_admin_sql(message, data)
    
    else:
        # Main menu buttons
        if message.text == texts.BUTTON_UPLOAD:
            start_upload(user_id)
        elif message.text == texts.BUTTON_SEARCH:
            start_search(user_id)
        elif message.text == texts.BUTTON_PROFILE:
            show_profile(user_id)
        elif message.text == texts.BUTTON_HELP:
            show_help(user_id)
        elif message.text == texts.BUTTON_ADMIN and is_admin(user_id):
            admin.show_admin_panel(bot, user_id)
        else:
            bot.send_message(
                user_id, 
                texts.UNKNOWN_INPUT, 
                parse_mode='Markdown',
                reply_markup=utils.create_main_menu_keyboard(user_id)
            )


# ==================== Registration Flow ====================

def handle_registration(message, data):
    user_id = message.from_user.id
    step = data.get('step')
    
    if step == 'name':
        full_name = message.text.strip()
        parts = full_name.split()
        if len(parts) < 2:
            bot.send_message(
                user_id, 
                "❌ Please enter your full name (first and last name).\n\nExample: `Mohamed Ahmed`",
                parse_mode='Markdown'
            )
            return
        
        data['name'] = full_name
        data['step'] = 'phone'
        db.set_user_state(user_id, 'register', data)
        
        if DEBUG:
            print(f"📝 Name saved for {user_id}: {full_name}")
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("📱 Share my phone number", request_contact=True))
        markup.add(KeyboardButton(texts.BUTTON_CANCEL))
        
        bot.send_message(
            user_id, 
            texts.REG_PHONE, 
            parse_mode='Markdown',
            reply_markup=markup
        )
    
    elif step == 'manual_region':
        handle_manual_region(message, data)
    
    elif step == 'manual_school':
        handle_manual_school(message, data)
    
    elif step == 'phone':
        phone = message.text.strip()
        if not any(c.isdigit() for c in phone) or len(phone) < 8:
            bot.send_message(
                user_id, 
                "❌ Invalid phone number. Please use the contact button or enter a valid number.",
                reply_markup=utils.create_cancel_keyboard()
            )
            return
        
        data['phone'] = phone
        data['step'] = 'region'
        db.set_user_state(user_id, 'register', data)
        
        bot.send_message(
            user_id, 
            texts.REG_REGION, 
            parse_mode='Markdown',
            reply_markup=utils.create_region_keyboard()
        )

def handle_manual_region(message, data):
    user_id = message.from_user.id
    region = message.text.strip()
    
    if region.lower() == texts.BUTTON_CANCEL.lower():
        db.clear_user_state(user_id)
        bot.send_message(
            user_id, 
            texts.CANCELLED, 
            parse_mode='Markdown',
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )
        return
    
    if DEBUG:
        print(f"✏️ Manual region entered by {user_id}: {region}")
    
    location_info = f"📍 *Region:* `{region}`"
    
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(
                admin_id, 
                texts.ADMIN_MANUAL_ENTRY_NOTIFICATION.format(
                    entry_type="REGION",
                    user_name="New User (not registered)",
                    user_id=user_id,
                    user_phone=data.get('phone', 'Not provided'),
                    location_info=location_info,
                    date=datetime.now().strftime("%Y-%m-%d %H:%M")
                ),
                parse_mode='Markdown'
            )
        except:
            pass
    
    data['region'] = region
    data['step'] = 'school'
    data['schools_page'] = 0
    db.set_user_state(user_id, 'register', data)
    
    show_schools_page(user_id, region, 0)
    
def handle_manual_school(message, data):
    user_id = message.from_user.id
    school = message.text.strip()
    region = data.get('region')
    
    if school.lower() == texts.BUTTON_CANCEL.lower():
        data['step'] = 'school'
        data['schools_page'] = 0
        db.set_user_state(user_id, 'register', data)
        show_schools_page(user_id, region, 0)
        return
    
    if DEBUG:
        print(f"✏️ Manual school entered by {user_id}: {school} in {region}")
    
    location_info = f"📍 *Region:* `{region}`\n\n🏫 *School:* `{school}`"
    
    for admin_id in ADMIN_IDS:
        try:
            # Add user management button to admin notification
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(
                "👤 View User", 
                callback_data=f"admin_user_details_{user_id}"
            ))
            
            bot.send_message(
                admin_id, 
                texts.ADMIN_MANUAL_ENTRY_NOTIFICATION.format(
                    entry_type="SCHOOL",
                    user_name="New User (not registered)",
                    user_id=user_id,
                    user_phone=data.get('phone', 'Not provided'),
                    location_info=location_info,
                    date=datetime.now().strftime("%Y-%m-%d %H:%M")
                ),
                parse_mode='Markdown',
                reply_markup=markup
            )
        except:
            pass
    
    data['school'] = school
    data['step'] = 'class'
    db.set_user_state(user_id, 'register', data)
    
    bot.send_message(
        user_id, 
        texts.REG_CLASS, 
        parse_mode='Markdown',
        reply_markup=utils.create_class_keyboard()
    )


def show_schools_page(user_id, region, page, message_id=None):
    schools = texts.form_four_schools_by_region.get(region, [])
    
    if not schools:
        data = db.get_user_state(user_id)[1]
        data['step'] = 'manual_school'
        data['region'] = region
        db.set_user_state(user_id, 'register', data)
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
        
        bot.send_message(
            user_id,
            texts.MANUAL_SCHOOL_PROMPT.format(region=region),
            parse_mode='Markdown',
            reply_markup=markup
        )
        return
    
    markup, total_pages = utils.create_schools_keyboard(schools, region, page)
    
    if message_id:
        bot.edit_message_text(
            texts.REG_SCHOOL.format(region=region),
            user_id,
            message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
    else:
        bot.send_message(
            user_id,
            texts.REG_SCHOOL.format(region=region),
            parse_mode='Markdown',
            reply_markup=markup
        )

# ==================== Callback Handlers ====================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    user = db.get_user(user_id)
    data = call.data
    
    if DEBUG:
        print(f"📞 Callback from {user_id}: {data}")
    
    # Update last active for registered users
    if user and not user['is_banned']:
        db.update_user_activity(user_id)
    
    if data == "ignore":
        bot.answer_callback_query(call.id)
        return
    
    if data == "cancel":
        db.clear_user_state(user_id)
        bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=None)
        bot.send_message(
            user_id,
            texts.CANCELLED,
            parse_mode='Markdown',
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )
        bot.answer_callback_query(call.id)
        return
    
    # Handle confirm upload
    if data == "confirm_upload":
        current_state, pending_data = db.get_user_state(user_id)
        if current_state == 'pending_upload' and pending_data:
            db.set_user_state(user_id, 'upload', {
                'step': 'subject',
                'file_id': pending_data['file_id'],
                'file_name': pending_data['file_name']
            })
            ask_subject(user_id)
            bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=None)
            bot.answer_callback_query(call.id, "Let's add details for your PDF!")
        else:
            bot.answer_callback_query(call.id, "Session expired. Please start again.")
        return
    
    # Handle share referral
    if data == "share_referral":
        show_referral_share(user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if data == "copy_referral_link":
        referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
        bot.answer_callback_query(call.id, "Link copied! Share it with friends.", show_alert=True)
        bot.send_message(
            user_id,
            f"🔗 *Your Referral Link*\n\n`{referral_link}`\n\nSend this link to your friends!",
            parse_mode='Markdown'
        )
        return
    
    # Handle registration callbacks
    if data.startswith('region_'):
        handle_region_callback(call)
        return
    
    if data.startswith('schools_page_'):
        handle_schools_page_callback(call)
        return
    
    if data.startswith('manual_school_'):
        handle_manual_school_callback(call)
        return
    
    if data.startswith('school_'):
        handle_school_callback(call)
        return
    
    if data.startswith('class_'):
        handle_class_callback(call)
        return
    
    if data.startswith('back_'):
        handle_back_callback(call)
        return
    
    if data.startswith('manual_region_start'):
        handle_manual_region_start(call)
        return
    
    # Handle upload callbacks
    if data.startswith('subject_'):
        handle_subject_callback(call)
        return
    
    if data.startswith('tag_'):
        handle_tag_callback(call)
        return
    
    # Handle search callbacks
    if data.startswith('search_subject_'):
        handle_search_subject_callback(call)
        return
    
    if data.startswith('search_tag_'):
        handle_search_tag_callback(call)
        return
    
    if data in ["search_next", "search_prev", "search_new"]:
        handle_search_navigation(call)
        return
    
    # Handle PDF action callbacks
    if data.startswith('view_'):
        handle_view_pdf_callback(call)
        return
    
    if data.startswith('download_'):
        handle_download_callback(call)
        return
    
    if data.startswith('like_') or data.startswith('unlike_'):
        handle_like_callback(call)
        return
    
    if data.startswith('report_'):
        handle_report_callback(call)
        return
    
    if data.startswith('share_'):
        handle_share_callback(call)
        return
    
    # Handle admin callbacks
    if data.startswith('admin_') or data.startswith('membership_'):
        if is_admin(user_id):
            admin.handle_admin_callback(bot, call)
        else:
            bot.answer_callback_query(call.id, texts.ERROR_PERMISSION)
        return
    
    # Handle membership verification
    if data.startswith('verify_telegram_') or data.startswith('verify_whatsapp_'):
        admin.handle_admin_callback(bot, call)
        return
    
    bot.answer_callback_query(call.id, "Unknown action")


# ==================== Registration Callback Functions ====================

def handle_region_callback(call):
    user_id = call.from_user.id
    current_state, data = db.get_user_state(user_id)
    
    if current_state != 'register':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    region = call.data.split('_')[1]
    
    if region not in texts.form_four_schools_by_region:
        data['step'] = 'manual_region'
        db.set_user_state(user_id, 'register', data)
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
        
        bot.edit_message_text(
            texts.MANUAL_REGION_PROMPT,
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
        return
    
    if DEBUG:
        print(f"📍 Region selected by {user_id}: {region}")
    
    data['region'] = region
    data['step'] = 'school'
    data['schools_page'] = 0
    db.set_user_state(user_id, 'register', data)
    
    show_schools_page(user_id, region, 0, call.message.message_id)
    bot.answer_callback_query(call.id)

def handle_schools_page_callback(call):
    user_id = call.from_user.id
    current_state, data = db.get_user_state(user_id)
    
    if current_state != 'register' or data.get('step') != 'school':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    parts = call.data.split('_')
    region = parts[2]
    page = int(parts[3])
    data['schools_page'] = page
    db.set_user_state(user_id, 'register', data)
    
    show_schools_page(user_id, region, page, call.message.message_id)
    bot.answer_callback_query(call.id)

def handle_manual_school_callback(call):
    user_id = call.from_user.id
    region = call.data.split('_')[2]
    current_state, data = db.get_user_state(user_id)
    
    if current_state != 'register' or data.get('step') != 'school':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    if DEBUG:
        print(f"✏️ Manual school requested by {user_id} for region {region}")
    
    data['step'] = 'manual_school'
    data['region'] = region
    db.set_user_state(user_id, 'register', data)
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    
    bot.edit_message_text(
        texts.MANUAL_SCHOOL_PROMPT.format(region=region),
        user_id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)
    
def handle_manual_region(message, data):
    user_id = message.from_user.id
    region = message.text.strip()
    
    if region.lower() == texts.BUTTON_CANCEL.lower():
        db.clear_user_state(user_id)
        bot.send_message(
            user_id, 
            texts.CANCELLED, 
            parse_mode='Markdown',
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )
        return
    
    if DEBUG:
        print(f"✏️ Manual region entered by {user_id}: {region}")
    
    location_info = f"📍 *Region:* `{region}`"
    
    for admin_id in ADMIN_IDS:
        try:
            # Add user management button to admin notification
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(
                "👤 View User", 
                callback_data=f"admin_user_details_{user_id}"
            ))
            
            bot.send_message(
                admin_id, 
                texts.ADMIN_MANUAL_ENTRY_NOTIFICATION.format(
                    entry_type="REGION",
                    user_name="New User (not registered)",
                    user_id=user_id,
                    user_phone=data.get('phone', 'Not provided'),
                    location_info=location_info,
                    date=datetime.now().strftime("%Y-%m-%d %H:%M")
                ),
                parse_mode='Markdown',
                reply_markup=markup
            )
        except:
            pass
    
    data['region'] = region
    data['step'] = 'school'
    data['schools_page'] = 0
    db.set_user_state(user_id, 'register', data)
    
    show_schools_page(user_id, region, 0)


def handle_school_callback(call):
    user_id = call.from_user.id
    current_state, data = db.get_user_state(user_id)
    
    if current_state != 'register' or data.get('step') != 'school':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    school = call.data.split('_', 1)[1]
    
    if DEBUG:
        print(f"🏫 School selected by {user_id}: {school}")
    
    data['school'] = school
    data['step'] = 'class'
    db.set_user_state(user_id, 'register', data)
    
    bot.edit_message_text(
        texts.REG_CLASS,
        user_id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=utils.create_class_keyboard()
    )
    bot.answer_callback_query(call.id)

def handle_class_callback(call):
    user_id = call.from_user.id
    current_state, data = db.get_user_state(user_id)
    
    if current_state != 'register' or data.get('step') != 'class':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    class_name = call.data.split('_')[1]
    data['class'] = class_name
    
    if DEBUG:
        print(f"🎓 Registration completed for {user_id}: Class {class_name}")
    
    referred_by = db.add_user(
        user_id=user_id,
        full_name=data.get('name'),
        phone=data.get('phone'),
        region=data.get('region'),
        school=data.get('school'),
        class_name=class_name,
        referred_by=data.get('referred_by')
    )
    
    if referred_by:
        notify_referrer(referred_by, user_id, data.get('name'))
    
    pending_pdf = data.get('pending_pdf')
    db.clear_user_state(user_id)
    
    bot.edit_message_text(
        texts.REG_SUCCESS,
        user_id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
    show_main_menu(user_id)
    
    if pending_pdf:
        handle_pdf_share(user_id, pending_pdf)
    
    bot.answer_callback_query(call.id)

def handle_back_callback(call):
    user_id = call.from_user.id
    current_state, data = db.get_user_state(user_id)
    
    if current_state != 'register':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    back_to = call.data.split('_')[1]
    
    if back_to == 'region':
        if DEBUG:
            print(f"🔙 User {user_id} went back to region selection")
        data['step'] = 'region'
        db.set_user_state(user_id, 'register', data)
        
        bot.edit_message_text(
            texts.REG_REGION,
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=utils.create_region_keyboard()
        )
    
    elif back_to == 'school':
        if DEBUG:
            print(f"🔙 User {user_id} went back to school selection")
        data['step'] = 'school'
        data['schools_page'] = 0
        db.set_user_state(user_id, 'register', data)
        region = data.get('region')
        show_schools_page(user_id, region, 0, call.message.message_id)
    
    bot.answer_callback_query(call.id)

# ==================== Upload Flow ====================

def start_upload(user_id):
    user = db.get_user(user_id)
    if not user:
        bot.send_message(user_id, texts.NOT_REGISTERED)
        return
    
    if DEBUG:
        print(f"📤 Upload started by user {user_id}")
    
    db.set_user_state(user_id, 'upload', {'step': 'waiting_for_file'})
    
    bot.send_message(
        user_id,
        texts.UPLOAD_FILE_PROMPT,
        parse_mode='Markdown',
        reply_markup=utils.create_cancel_keyboard()
    )

def handle_upload_pdf(message, data):
    user_id = message.from_user.id
    
    if not message.document or message.document.mime_type != 'application/pdf':
        bot.send_message(
            user_id,
            texts.UPLOAD_INVALID_FILE,
            parse_mode='Markdown',
            reply_markup=utils.create_cancel_keyboard()
        )
        return
    
    if DEBUG:
        print(f"📥 Received PDF from {user_id}: {message.document.file_name}")
    
    file_size = message.document.file_size
    file_size_display = utils.format_file_size(file_size)
    
    data['file_id'] = message.document.file_id
    data['file_name'] = message.document.file_name
    data['file_size'] = file_size
    data['step'] = 'subject'
    db.set_user_state(user_id, 'upload', data)
    
    bot.send_message(
        user_id,
        texts.UPLOAD_RECEIVED.format(
            file_name=message.document.file_name,
            size=file_size_display
        ),
        parse_mode='Markdown'
    )
    
    ask_subject(user_id)

def ask_subject(user_id):
    bot.send_message(
        user_id,
        texts.UPLOAD_SUBJECT,
        parse_mode='Markdown',
        reply_markup=utils.create_subject_keyboard()
    )
    
    if DEBUG:
        print(f"📚 Asked for subject from user {user_id}")

def handle_subject_callback(call):
    user_id = call.from_user.id
    current_state, data = db.get_user_state(user_id)
    
    if current_state != 'upload' or data.get('step') != 'subject':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    subject = call.data.split('_')[1]
    data['subject'] = subject
    data['step'] = 'tag'
    db.set_user_state(user_id, 'upload', data)
    
    if DEBUG:
        print(f"📚 Subject selected by {user_id}: {subject}")
    
    bot.edit_message_text(
        texts.UPLOAD_TAG,
        user_id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=utils.create_tag_keyboard()
    )
    bot.answer_callback_query(call.id)

def handle_tag_callback(call):
    user_id = call.from_user.id
    current_state, data = db.get_user_state(user_id)
    
    if current_state != 'upload' or data.get('step') != 'tag':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    tag = call.data.split('_')[1]
    
    if tag == 'skip':
        tag = None
    
    data['tag'] = tag
    data['step'] = 'finish'
    db.set_user_state(user_id, 'upload', data)
    
    if DEBUG:
        print(f"🏷️ Tag selected by {user_id}: {tag}")
    
    finish_upload(user_id, call.message.message_id)
    bot.answer_callback_query(call.id)

def finish_upload(user_id, message_id=None):
    current_state, data = db.get_user_state(user_id)
    
    if not current_state or data.get('step') != 'finish':
        if DEBUG:
            print(f"⚠️ Not in upload finish state")
        return
    
    file_id = data.get('file_id')
    file_name = data.get('file_name')
    subject = data['subject']
    tag = data.get('tag')
    
    if not file_id or not file_name:
        bot.send_message(user_id, texts.UPLOAD_FAILED, parse_mode='Markdown')
        db.clear_user_state(user_id)
        return
    
    # Remove file_size parameter - function expects 6 args only
    pdf_id = db.add_pdf(
        file_id=file_id,
        file_name=file_name,
        user_id=user_id,
        subject=subject,
        tag=tag,
        exam_year=None
    )
    
    db.clear_user_state(user_id)
    
    if DEBUG:
        print(f"✅ PDF uploaded by {user_id}: {file_name} (ID: {pdf_id})")
    
    msg = texts.UPLOAD_SUCCESS.format(
        file_name=file_name,
        subject=subject,
        tag=tag or "None",
        pdf_id=pdf_id
    )
    
    bot.send_message(
        user_id,
        msg,
        parse_mode='Markdown',
        reply_markup=utils.create_main_menu_keyboard(user_id)
    )
    
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(
                admin_id,
                f"📄 *New PDF Upload*\n\n"
                f"📄 *File:* `{file_name}`\n"
                f"👤 *User:* `{user_id}`\n"
                f"📚 *Subject:* `{subject}`\n"
                f"🏷️ *Tag:* `{tag or 'None'}`\n"
                f"🆔 *ID:* `{pdf_id}`",
                parse_mode='Markdown'
            )
        except:
            pass
    
    if message_id:
        try:
            bot.edit_message_reply_markup(user_id, message_id, reply_markup=None)
        except:
            pass

# ==================== Search Flow ====================

def start_search(user_id):
    user = db.get_user(user_id)
    if not user:
        bot.send_message(user_id, texts.NOT_REGISTERED)
        return
    
    if DEBUG:
        print(f"🔍 Search started by user {user_id}")
    
    bot.send_message(
        user_id,
        texts.SEARCH_START,
        parse_mode='Markdown',
        reply_markup=utils.create_subject_keyboard()
    )

def handle_search_subject_callback(call):
    user_id = call.from_user.id
    subject = call.data.split('_')[2]
    
    db.set_user_state(user_id, 'search', {'subject': subject, 'step': 'tag'})
    
    bot.edit_message_text(
        texts.SEARCH_SUBJECT_SELECTED.format(subject=subject),
        user_id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=utils.create_search_tag_keyboard()
    )
    bot.answer_callback_query(call.id)

def handle_search_tag_callback(call):
    user_id = call.from_user.id
    current_state, data = db.get_user_state(user_id)
    
    if current_state != 'search' or data.get('step') != 'tag':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    tag = call.data.split('_')[2]
    if tag == 'skip':
        tag = None
    
    data['tag'] = tag
    data['step'] = 'results'
    data['page'] = 0
    db.set_user_state(user_id, 'search', data)
    
    show_search_results(user_id, call.message.message_id)
    bot.answer_callback_query(call.id)

def show_search_results(user_id, message_id=None):
    current_state, data = db.get_user_state(user_id)
    
    if not current_state or data.get('step') != 'results':
        return
    
    subject = data.get('subject')
    tag = data.get('tag')
    page = data.get('page', 0)
    limit = 5
    offset = page * limit
    
    total = db.count_pdfs_by_filters(subject=subject, tag=tag)
    total_pages = (total + limit - 1) // limit
    
    if total == 0:
        bot.send_message(
            user_id,
            texts.SEARCH_NO_RESULTS,
            parse_mode='Markdown',
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )
        db.clear_user_state(user_id)
        return
    
    pdfs = db.get_pdfs_by_filters(subject=subject, tag=tag, limit=limit, offset=offset)
    
    text = texts.SEARCH_RESULTS.format(
        subject=subject,
        tag=tag or "All",
        total=total,
        page=page + 1,
        total_pages=total_pages
    )
    
    for idx, pdf in enumerate(pdfs, start=1):
        emoji = utils.get_pdf_emoji(pdf['tag'])
        text += texts.SEARCH_RESULT_ITEM.format(
            emoji=emoji,
            name=pdf['file_name'][:40],
            subject=pdf['subject'],
            tag=pdf['tag'],
            likes=pdf['like_count'],
            downloads=pdf['download_count'],
            id=pdf['id']
        )
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    if page > 0:
        markup.add(InlineKeyboardButton("◀️ Prev", callback_data="search_prev"))
    if page < total_pages - 1:
        markup.add(InlineKeyboardButton("Next ▶️", callback_data="search_next"))
    
    for pdf in pdfs:
        markup.add(InlineKeyboardButton(
            f"{utils.get_pdf_emoji(pdf['tag'])} {pdf['file_name'][:30]}",
            callback_data=f"view_{pdf['id']}"
        ))
    
    markup.add(InlineKeyboardButton("🔄 New Search", callback_data="search_new"))
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    
    if message_id:
        bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)

def handle_search_navigation(call):
    user_id = call.from_user.id
    current_state, data = db.get_user_state(user_id)
    
    if current_state != 'search' or data.get('step') != 'results':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    if call.data == "search_next":
        data['page'] += 1
    elif call.data == "search_prev":
        data['page'] -= 1
    elif call.data == "search_new":
        db.clear_user_state(user_id)
        start_search(user_id)
        bot.delete_message(user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    db.set_user_state(user_id, 'search', data)
    show_search_results(user_id, call.message.message_id)
    bot.answer_callback_query(call.id)

# ==================== PDF View Actions ====================

def handle_view_pdf_callback(call):
    user_id = call.from_user.id
    pdf_id = int(call.data.split('_')[1])
    pdf = db.get_pdf(pdf_id)
    
    if not pdf:
        bot.answer_callback_query(call.id, texts.ERROR_NOT_FOUND)
        return
    
    if not pdf['is_approved'] and not is_admin(user_id) and pdf['uploaded_by'] != user_id:
        bot.answer_callback_query(call.id, "⏳ This PDF is pending approval.")
        return
    
    uploader = db.get_user(pdf['uploaded_by'])
    uploader_name = uploader['full_name'] if uploader else "Unknown"
    
    text = texts.PDF_VIEW.format(
        name=pdf['file_name'],
        subject=pdf['subject'],
        tag=pdf['tag'],
        uploader=uploader_name,
        date=utils.format_date(pdf['upload_date']),
        downloads=pdf['download_count'],
        likes=pdf['like_count']
    )
    
    markup = utils.create_pdf_action_buttons(pdf_id, user_id, is_admin(user_id))
    
    bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
    bot.answer_callback_query(call.id)

def handle_download_callback(call):
    user_id = call.from_user.id
    pdf_id = int(call.data.split('_')[1])
    pdf = db.get_pdf(pdf_id)
    
    if not pdf:
        bot.answer_callback_query(call.id, texts.ERROR_NOT_FOUND)
        return
    
    if pdf['file_id']:
        try:
            bot.send_document(
                user_id, 
                pdf['file_id'], 
                caption=f"📄 *{pdf['file_name']}*\n\n📚 *Subject:* {pdf['subject']}\n🏷️ *Tag:* {pdf['tag']}",
                parse_mode='Markdown'
            )
            db.increment_download(pdf_id, user_id)
            
            if DEBUG:
                print(f"📥 PDF downloaded by {user_id}: {pdf['file_name']} (ID: {pdf_id})")
            
            bot.answer_callback_query(call.id, texts.PDF_DOWNLOAD_STARTED)
        except Exception as e:
            if DEBUG:
                print(f"❌ Download failed for {user_id}: {e}")
            bot.answer_callback_query(call.id, texts.PDF_DOWNLOAD_FAILED)
    else:
        bot.answer_callback_query(call.id, "❌ File not available.")

def handle_like_callback(call):
    user_id = call.from_user.id
    action, pdf_id = call.data.split('_')
    pdf_id = int(pdf_id)
    
    if action == 'like':
        if db.like_pdf(pdf_id, user_id):
            if DEBUG:
                print(f"❤️ PDF liked by {user_id}: {pdf_id}")
            bot.answer_callback_query(call.id, texts.PDF_LIKED)
        else:
            bot.answer_callback_query(call.id, "❤️ You already liked this.")
    else:
        db.unlike_pdf(pdf_id, user_id)
        if DEBUG:
            print(f"💔 PDF unliked by {user_id}: {pdf_id}")
        bot.answer_callback_query(call.id, texts.PDF_UNLIKED)
    
    pdf = db.get_pdf(pdf_id)
    if pdf:
        uploader = db.get_user(pdf['uploaded_by'])
        uploader_name = uploader['full_name'] if uploader else "Unknown"
        
        text = texts.PDF_VIEW.format(
            name=pdf['file_name'],
            subject=pdf['subject'],
            tag=pdf['tag'],
            uploader=uploader_name,
            date=utils.format_date(pdf['upload_date']),
            downloads=pdf['download_count'],
            likes=pdf['like_count']
        )
        
        markup = utils.create_pdf_action_buttons(pdf_id, user_id, is_admin(user_id))
        
        try:
            bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
        except:
            pass

def handle_report_callback(call):
    user_id = call.from_user.id
    pdf_id = int(call.data.split('_')[1])
    
    db.set_user_state(user_id, 'report', {'pdf_id': pdf_id})
    
    bot.send_message(
        user_id,
        texts.PDF_REPORT_PROMPT,
        parse_mode='Markdown',
        reply_markup=utils.create_cancel_keyboard()
    )
    bot.answer_callback_query(call.id)

def handle_share_callback(call):
    user_id = call.from_user.id
    pdf_id = int(call.data.split('_')[1])
    
    markup = utils.create_share_buttons(pdf_id, user_id)
    
    bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id)

def handle_report(message, data):
    user_id = message.from_user.id
    pdf_id = data['pdf_id']
    report_text = message.text
    
    if report_text.lower() == texts.BUTTON_CANCEL.lower():
        db.clear_user_state(user_id)
        bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard(user_id))
        return
    
    db.add_report(pdf_id, user_id, report_text)
    
    if DEBUG:
        print(f"⚠️ Report submitted by {user_id} for PDF {pdf_id}: {report_text[:50]}...")
    
    pdf = db.get_pdf(pdf_id)
    if pdf:
        uploader = db.get_user(pdf['uploaded_by'])
        if uploader:
            try:
                bot.send_message(
                    uploader['user_id'],
                    texts.REPORT_NOTIFY_UPLOADER.format(
                        pdf_name=pdf['file_name'],
                        reporter=message.from_user.full_name or message.from_user.first_name,
                        reason=report_text
                    ),
                    parse_mode='Markdown'
                )
            except:
                pass
    
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(
                admin_id,
                texts.REPORT_NOTIFY_ADMIN.format(
                    pdf_name=pdf['file_name'],
                    pdf_id=pdf_id,
                    uploader=uploader['full_name'] if uploader else "Unknown",
                    reporter=message.from_user.full_name or message.from_user.first_name,
                    reason=report_text
                ),
                parse_mode='Markdown'
            )
        except:
            pass
    
    db.clear_user_state(user_id)
    
    bot.send_message(
        user_id,
        texts.PDF_REPORT_SENT,
        parse_mode='Markdown',
        reply_markup=utils.create_main_menu_keyboard(user_id)
    )

# ==================== Profile ====================
def show_profile(user_id):
    user = db.get_user(user_id)
    if not user:
        bot.send_message(user_id, texts.NOT_REGISTERED)
        return
    
    # Update last active
    db.update_user_activity(user_id)
    
    uploads_count = db.get_user_upload_count(user_id)
    downloads_count = db.get_user_download_count(user_id)
    stats = db.get_user_referral_stats(user_id)
    
    # Get current time in Somalia timezone
    now = utils.get_current_time()
    
    # Calculate days since join - handle timezone properly
    join_date = user['join_date']
    if isinstance(join_date, str):
        join_date = datetime.fromisoformat(join_date)
        if join_date.tzinfo is None:
            join_date = pytz.timezone('Africa/Mogadishu').localize(join_date)
    
    last_active = user['last_active']
    if isinstance(last_active, str):
        last_active = datetime.fromisoformat(last_active)
        if last_active.tzinfo is None:
            last_active = pytz.timezone('Africa/Mogadishu').localize(last_active)
    
    days_joined = (now - join_date).days if join_date else 0
    last_active_str = utils.format_date(last_active) if last_active else "Never"
    
    text = texts.PROFILE_DISPLAY.format(
        name=user['full_name'],
        user_id=user_id,
        phone=user['phone'] or "Not set",
        class_=user['class'] or "Not set",
        region=user['region'] or "Not set",
        school=user['school'] or "Not set",
        joined=utils.format_date(join_date),
        last_active=last_active_str,
        days_joined=days_joined,
        uploads=uploads_count,
        downloads=downloads_count,
        conversions=stats['conversions']
    )
    
    text += texts.REFERRAL_LINK_TEXT.format(
        bot_username=BOT_USERNAME,
        user_id=user_id
    )
    
    bot.send_message(
        user_id,
        text,
        parse_mode='Markdown',
        reply_markup=utils.create_profile_buttons(user_id)
    )
    
    if DEBUG:
        print(f"👤 Profile viewed by user {user_id}")


def show_referral_share(user_id, message_id=None):
    referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
    whatsapp_link = f"https://wa.me/?text={referral_link.replace('&', '%26')}"
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(texts.BUTTON_SHARE_TELEGRAM, url=f"https://t.me/share/url?url={referral_link}&text=📚 Join Ardayda Educational Bot! Get educational PDFs for free! 🎓"),
        InlineKeyboardButton(texts.BUTTON_SHARE_WHATSAPP, url=whatsapp_link)
    )
    markup.add(InlineKeyboardButton("📋 Copy Link", callback_data="copy_referral_link"))
    markup.add(InlineKeyboardButton(texts.BUTTON_BACK, callback_data="back_to_profile"))
    
    if message_id:
        bot.edit_message_text(
            "🔗 *Share Your Referral Link*\n\n"
            "Share this link with your friends and classmates:\n\n"
            f"`{referral_link}`\n\n"
            "When they register using your link, you'll get credit! 🎉",
            user_id,
            message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
    else:
        bot.send_message(
            user_id,
            "🔗 *Share Your Referral Link*\n\n"
            f"`{referral_link}`\n\n"
            "Share this link with your friends!",
            parse_mode='Markdown',
            reply_markup=markup
        )

# ==================== Help ====================

def show_help(user_id):
    markup = utils.create_help_buttons()
    
    bot.send_message(
        user_id,
        texts.HELP_TEXT,
        parse_mode='Markdown',
        reply_markup=markup
    )

# ==================== Shared PDF Link Handler ====================

def handle_pdf_share(user_id, pdf_id):
    pdf = db.get_pdf(pdf_id)
    if not pdf:
        bot.send_message(user_id, "❌ PDF not found.")
        return
    
    user = db.get_user(user_id)
    if not user:
        db.set_user_state(user_id, 'register', {'step': 'name', 'pending_pdf': pdf_id})
        bot.send_message(
            user_id,
            "📚 *Shared PDF*\n\nPlease register first to view this PDF.",
            parse_mode='Markdown',
            reply_markup=utils.create_cancel_keyboard()
        )
        bot.send_message(user_id, texts.REG_NAME, parse_mode='Markdown')
    else:
        uploader = db.get_user(pdf['uploaded_by'])
        text = texts.PDF_VIEW.format(
            name=pdf['file_name'],
            subject=pdf['subject'],
            tag=pdf['tag'],
            uploader=uploader['full_name'] if uploader else "Unknown",
            date=utils.format_date(pdf['upload_date']),
            downloads=pdf['download_count'],
            likes=pdf['like_count']
        )
        markup = utils.create_pdf_action_buttons(pdf_id, user_id, is_admin(user_id))
        bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)

# ==================== Admin Broadcast & SQL ====================

def handle_admin_broadcast(message, data):
    user_id = message.from_user.id
    text = message.text
    
    if text.lower() == texts.BUTTON_CANCEL.lower():
        db.clear_user_state(user_id)
        bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard(user_id))
        return
    
    users = db.get_all_users()
    count = 0
    
    for user in users:
        try:
            bot.send_message(user['user_id'], text, parse_mode='Markdown')
            count += 1
        except:
            pass
    
    db.clear_user_state(user_id)
    
    if DEBUG:
        print(f"📢 Broadcast sent by admin {user_id} to {count} users")
    
    bot.send_message(
        user_id,
        texts.ADMIN_BROADCAST_CONFIRM.format(count=count),
        parse_mode='Markdown',
        reply_markup=utils.create_main_menu_keyboard(user_id)
    )

def handle_admin_sql(message, data):
    user_id = message.from_user.id
    sql = message.text
    
    if sql.lower() == texts.BUTTON_CANCEL.lower():
        db.clear_user_state(user_id)
        bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard(user_id))
        return
    
    result = db.execute_sql(sql)
    result_str = str(result)
    
    if len(result_str) > 4000:
        result_str = result_str[:4000] + "...(truncated)"
    
    if DEBUG:
        print(f"🔧 SQL executed by admin {user_id}")
    
    db.clear_user_state(user_id)
    
    bot.send_message(
        user_id,
        texts.ADMIN_SQL_RESULT.format(result=result_str),
        parse_mode='Markdown',
        reply_markup=utils.create_main_menu_keyboard(user_id)
    )