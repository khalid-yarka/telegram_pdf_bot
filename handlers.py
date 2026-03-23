# telegram_pdf_bot/handlers.py
# All message and callback handlers

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN, ADMIN_IDS, TAGS, TAGS_REQUIRING_YEAR, YEARS, CLASSES, BOT_USERNAME, REQUIRED_CHANNEL, MAX_FILE_SIZE, DEBUG
import database as db
import texts
import state_management as state
import utils
from datetime import datetime

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
        bot.send_message(user_id, texts.HOME_WELCOME.format(name=user['full_name']),
                         parse_mode='Markdown', reply_markup=utils.create_main_menu_keyboard())
        if DEBUG:
            print(f"📱 Main menu shown to user {user_id}")
    else:
        bot.send_message(user_id, texts.HOME_WELCOME.format(name="User"),
                         parse_mode='Markdown', reply_markup=utils.create_main_menu_keyboard())

def notify_admin_manual_entry(user_id, entry_type, location_info):
    """Send notification to admins about manual entry"""
    user = db.get_user(user_id)
    user_name = user['full_name'] if user else "Unknown"
    user_phone = user['phone'] if user and user['phone'] else "Not provided"
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    notification_text = texts.ADMIN_MANUAL_ENTRY_NOTIFICATION.format(
        entry_type=entry_type,
        entry_type_lower=entry_type.lower(),
        user_name=user_name,
        user_id=user_id,
        user_phone=user_phone,
        location_info=location_info,
        date=current_time
    )
    
    if DEBUG:
        print(f"📢 Sending manual entry notification: {entry_type} - User: {user_name} (ID: {user_id})")
        print(f"📍 {location_info}")
    
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, notification_text, parse_mode='Markdown')
            if DEBUG:
                print(f"✅ Notification sent to admin {admin_id}")
        except Exception as e:
            if DEBUG:
                print(f"❌ Failed to send to admin {admin_id}: {e}")

def require_channel_member(func):
    """Decorator to check if user is a member of required channel."""
    def wrapper(message_or_call, *args, **kwargs):
        user_id = message_or_call.from_user.id if hasattr(message_or_call, 'from_user') else message_or_call.message.from_user.id
        if not utils.is_channel_member(bot, user_id, REQUIRED_CHANNEL):
            if DEBUG:
                print(f"🔒 User {user_id} not in required channel")
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(texts.CHANNEL_JOIN_BUTTON, url=f"https://t.me/{REQUIRED_CHANNEL}"))
            markup.add(InlineKeyboardButton(texts.CHANNEL_CHECK_BUTTON, callback_data="check_channel"))
            bot.send_message(user_id, texts.CHANNEL_REQUIRED, parse_mode='Markdown', reply_markup=markup)
            return
        return func(message_or_call, *args, **kwargs)
    return wrapper

# ==================== Start & Registration ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    args = message.text.split()
    start_param = args[1] if len(args) > 1 else None
    
    if DEBUG:
        print(f"🚀 /start from user {user_id}")

    # Check channel membership
    if not utils.is_channel_member(bot, user_id, REQUIRED_CHANNEL):
        if DEBUG:
            print(f"🔒 User {user_id} blocked by channel requirement")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts.CHANNEL_JOIN_BUTTON, url=f"https://t.me/{REQUIRED_CHANNEL}"))
        markup.add(InlineKeyboardButton(texts.CHANNEL_CHECK_BUTTON, callback_data="check_channel"))
        bot.send_message(user_id, texts.CHANNEL_REQUIRED, parse_mode='Markdown', reply_markup=markup)
        return

    # Check if user exists
    user = db.get_user(user_id)
    if user and not user['is_banned']:
        if DEBUG:
            print(f"👤 Existing user {user_id} logged in")
        if start_param and start_param.startswith('pdf_'):
            pdf_id = start_param.split('_')[1]
            handle_pdf_share(user_id, pdf_id)
        elif start_param and start_param.startswith('ref_'):
            bot.send_message(user_id, "You are already registered. Use the main menu.")
            show_main_menu(user_id)
        else:
            show_main_menu(user_id)
        return

    # New user registration
    referred_by = None
    if start_param and start_param.startswith('ref_'):
        referrer_id = start_param.split('_')[1]
        referrer = db.get_user(referrer_id)
        if referrer:
            referred_by = referrer['user_id']
            if DEBUG:
                print(f"🔗 New user referred by {referrer_id}")

    pending_pdf = None
    if start_param and start_param.startswith('pdf_'):
        pending_pdf = start_param.split('_')[1]

    state.set_user_state(user_id, 'register', {
        'step': 'name',
        'referred_by': referred_by,
        'pending_pdf': pending_pdf
    })
    bot.send_message(user_id, texts.REG_NAME, parse_mode='Markdown')
    if DEBUG:
        print(f"📝 New registration started for user {user_id}")

# ==================== Contact Handler ====================
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = message.from_user.id
    current_state, data = state.get_user_state(user_id)
    if current_state == 'register' and data.get('step') == 'phone':
        phone = message.contact.phone_number
        data['phone'] = phone
        data['step'] = 'region'
        state.set_user_state(user_id, 'register', data)
        if DEBUG:
            print(f"📞 Phone received for user {user_id}: {phone}")
        markup = InlineKeyboardMarkup(row_width=2)
        for region in texts.form_four_schools_by_region.keys():
            markup.add(InlineKeyboardButton(region, callback_data=f"region_{region}"))
        markup.add(InlineKeyboardButton(texts.BUTTON_REGION_NOT_LISTED, callback_data="manual_region_start"))
        bot.send_message(user_id, texts.REG_REGION, parse_mode='Markdown', reply_markup=markup)

# ==================== Main Message Handler ====================
@bot.message_handler(func=lambda message: True)
@require_channel_member
def handle_messages(message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    if user and user['is_banned']:
        bot.send_message(user_id, texts.ACCOUNT_SUSPENDED)
        return

    current_state, data = state.get_user_state(user_id)
    if current_state == 'register':
        handle_registration(message, data)
    elif current_state == 'upload':
        handle_upload(message, data)
    elif current_state == 'search':
        handle_search(message, data)
    elif current_state == 'report':
        handle_report(message, data)
    elif current_state == 'admin_broadcast':
        handle_admin_broadcast(message, data)
    elif current_state == 'admin_sql':
        handle_admin_sql(message, data)
    else:
        if message.text == texts.BUTTON_UPLOAD:
            start_upload(user_id)
        elif message.text == texts.BUTTON_SEARCH:
            start_search(user_id)
        elif message.text == texts.BUTTON_PROFILE:
            show_profile(user_id)
        elif message.text == texts.BUTTON_HELP:
            bot.send_message(user_id, texts.HELP_TEXT, parse_mode='Markdown')
        elif message.text == texts.BUTTON_ADMIN and is_admin(user_id):
            show_admin_panel(user_id)
        else:
            bot.send_message(user_id, texts.UNKNOWN_INPUT, reply_markup=utils.create_main_menu_keyboard())

# ==================== Registration Flow ====================
def handle_registration(message, data):
    user_id = message.from_user.id
    step = data.get('step')
    
    if step == 'name':
        full_name = message.text.strip()
        parts = full_name.split()
        if len(parts) < 2:
            bot.send_message(user_id, "Please enter your full name (at least first and last name).")
            return
        data['name'] = full_name
        data['step'] = 'phone'
        state.set_user_state(user_id, 'register', data)
        if DEBUG:
            print(f"📝 Name saved for {user_id}: {full_name}")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("📱 Share my phone number", request_contact=True))
        bot.send_message(user_id, texts.REG_PHONE, reply_markup=markup)
    
    elif step == 'manual_region':
        handle_manual_region(message, data)
    
    elif step == 'manual_school':
        handle_manual_school(message, data)
    
    elif step == 'phone':
        phone = message.text.strip()
        if not any(c.isdigit() for c in phone):
            bot.send_message(user_id, "Invalid phone number. Please use the contact button.")
            return
        data['phone'] = phone
        data['step'] = 'region'
        state.set_user_state(user_id, 'register', data)
        markup = InlineKeyboardMarkup(row_width=2)
        for region in texts.form_four_schools_by_region.keys():
            markup.add(InlineKeyboardButton(region, callback_data=f"region_{region}"))
        markup.add(InlineKeyboardButton(texts.BUTTON_REGION_NOT_LISTED, callback_data="manual_region_start"))
        bot.send_message(user_id, texts.REG_REGION, parse_mode='Markdown', reply_markup=markup)
    
    elif step == 'region':
        markup = InlineKeyboardMarkup(row_width=2)
        for region in texts.form_four_schools_by_region.keys():
            markup.add(InlineKeyboardButton(region, callback_data=f"region_{region}"))
        markup.add(InlineKeyboardButton(texts.BUTTON_REGION_NOT_LISTED, callback_data="manual_region_start"))
        bot.send_message(user_id, texts.REG_REGION, parse_mode='Markdown', reply_markup=markup)
    
    else:
        state.clear_user_state(user_id)
        start_command(message)

def handle_manual_region(message, data):
    """Handle manual region entry"""
    user_id = message.from_user.id
    region = message.text.strip()
    
    if region.lower() == 'cancel':
        state.clear_user_state(user_id)
        bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard())
        return
    
    if DEBUG:
        print(f"✏️ Manual region entered by {user_id}: {region}")
    
    location_info = f"📍 *Missing Region*\n└ `{region}`\n\n🏫 *School:* `{data.get('school', 'Not selected yet')}`"
    notify_admin_manual_entry(user_id, "REGION", location_info)
    
    data['region'] = region
    data['step'] = 'school'
    data['schools_page'] = 0
    state.set_user_state(user_id, 'register', data)
    
    show_schools_page(user_id, region, 0, None)
    bot.send_message(user_id, texts.REG_SCHOOL.format(region=region), parse_mode='Markdown')

def handle_manual_school(message, data):
    """Handle manual school entry"""
    user_id = message.from_user.id
    school = message.text.strip()
    region = data.get('region')
    
    if school.lower() == 'cancel':
        data['step'] = 'school'
        data['schools_page'] = 0
        state.set_user_state(user_id, 'register', data)
        show_schools_page(user_id, region, 0, None)
        bot.send_message(user_id, texts.REG_SCHOOL.format(region=region), parse_mode='Markdown')
        return
    
    if DEBUG:
        print(f"✏️ Manual school entered by {user_id}: {school} in {region}")
    
    location_info = f"📍 *Region:* `{region}`\n\n🏫 *Missing School*\n└ `{school}`"
    notify_admin_manual_entry(user_id, "SCHOOL", location_info)
    
    data['school'] = school
    data['step'] = 'class'
    state.set_user_state(user_id, 'register', data)
    
    markup = InlineKeyboardMarkup(row_width=2)
    for class_name in CLASSES:
        markup.add(InlineKeyboardButton(class_name, callback_data=f"class_{class_name}"))
    markup.add(InlineKeyboardButton(texts.BUTTON_BACK, callback_data="back_school"))
    bot.send_message(user_id, texts.REG_CLASS, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('region_'))
def region_callback(call):
    user_id = call.from_user.id
    current_state, data = state.get_user_state(user_id)
    if current_state != 'register' or data.get('step') != 'region':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    region = call.data.split('_')[1]
    
    if region not in texts.form_four_schools_by_region:
        if DEBUG:
            print(f"⚠️ Region '{region}' not found, asking for manual entry")
        data['step'] = 'manual_region'
        data['original_region'] = region
        state.set_user_state(user_id, current_state, data)
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
        bot.edit_message_text(
            texts.MANUAL_REGION_PROMPT, 
            user_id, 
            call.message.message_id, 
            parse_mode='Markdown',
            reply_markup=markup
        )
        return
    
    if DEBUG:
        print(f"📍 Region selected by {user_id}: {region}")
    
    data['region'] = region
    data['step'] = 'school'
    data['schools_page'] = 0
    state.set_user_state(user_id, current_state, data)
    show_schools_page(user_id, region, 0, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "manual_region_start")
def manual_region_start_callback(call):
    user_id = call.from_user.id
    current_state, data = state.get_user_state(user_id)
    if current_state != 'register':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    if DEBUG:
        print(f"✏️ Manual region requested by {user_id}")
    
    data['step'] = 'manual_region'
    state.set_user_state(user_id, current_state, data)
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    bot.edit_message_text(
        texts.MANUAL_REGION_PROMPT,
        user_id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=markup
    )

def show_schools_page(user_id, region, page, message_id):
    schools = texts.form_four_schools_by_region.get(region, [])
    total = len(schools)
    page_size = 6
    start = page * page_size
    end = start + page_size
    page_schools = schools[start:end]
    total_pages = (total + page_size - 1) // page_size

    markup = InlineKeyboardMarkup(row_width=2)
    for school in page_schools:
        markup.add(InlineKeyboardButton(school, callback_data=f"school_{school}"))
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀ Prev", callback_data=f"schools_page_{region}_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶", callback_data=f"schools_page_{region}_{page+1}"))
    if nav_buttons:
        markup.row(*nav_buttons)
    
    markup.add(InlineKeyboardButton(texts.BUTTON_SCHOOL_NOT_LISTED, callback_data=f"manual_school_{region}"))
    markup.add(InlineKeyboardButton(texts.BUTTON_BACK, callback_data="back_region"))
    
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

@bot.callback_query_handler(func=lambda call: call.data.startswith('schools_page_'))
def schools_page_callback(call):
    user_id = call.from_user.id
    current_state, data = state.get_user_state(user_id)
    if current_state != 'register' or data.get('step') != 'school':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    parts = call.data.split('_')
    region = parts[2]
    page = int(parts[3])
    data['schools_page'] = page
    state.set_user_state(user_id, current_state, data)
    show_schools_page(user_id, region, page, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('manual_school_'))
def manual_school_callback(call):
    user_id = call.from_user.id
    region = call.data.split('_')[2]
    current_state, data = state.get_user_state(user_id)
    if current_state != 'register' or data.get('step') != 'school':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    if DEBUG:
        print(f"✏️ Manual school requested by {user_id} for region {region}")
    
    data['step'] = 'manual_school'
    data['region'] = region
    state.set_user_state(user_id, current_state, data)
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="back_to_schools"))
    bot.edit_message_text(
        texts.MANUAL_SCHOOL_PROMPT.format(region=region),
        user_id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_schools")
def back_to_schools_callback(call):
    user_id = call.from_user.id
    current_state, data = state.get_user_state(user_id)
    if current_state != 'register':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    data['step'] = 'school'
    data['schools_page'] = 0
    state.set_user_state(user_id, current_state, data)
    region = data.get('region')
    show_schools_page(user_id, region, 0, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('school_'))
def school_callback(call):
    user_id = call.from_user.id
    current_state, data = state.get_user_state(user_id)
    if current_state != 'register' or data.get('step') != 'school':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    school = call.data.split('_', 1)[1]
    region = data.get('region')
    schools_list = texts.form_four_schools_by_region.get(region, [])
    
    if school not in schools_list:
        if DEBUG:
            print(f"⚠️ School '{school}' not found in {region}, notifying admin")
        location_info = f"📍 *Region:* `{region}`\n\n🏫 *Missing School*\n└ `{school}`"
        notify_admin_manual_entry(user_id, "SCHOOL", location_info)
    
    if DEBUG:
        print(f"🏫 School selected by {user_id}: {school} in {region}")
    
    data['school'] = school
    data['step'] = 'class'
    state.set_user_state(user_id, current_state, data)
    
    markup = InlineKeyboardMarkup(row_width=2)
    for class_name in CLASSES:
        markup.add(InlineKeyboardButton(class_name, callback_data=f"class_{class_name}"))
    markup.add(InlineKeyboardButton(texts.BUTTON_BACK, callback_data="back_school"))
    bot.edit_message_text(
        texts.REG_CLASS, 
        user_id, 
        call.message.message_id, 
        parse_mode='Markdown', 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('class_'))
def class_callback(call):
    user_id = call.from_user.id
    current_state, data = state.get_user_state(user_id)
    if current_state != 'register' or data.get('step') != 'class':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    class_name = call.data.split('_')[1]
    data['class'] = class_name
    
    if DEBUG:
        print(f"🎓 Registration completed for {user_id}: Class {class_name}")
    
    db.add_user(
        user_id=user_id,
        full_name=data.get('name'),
        phone=data.get('phone'),
        region=data.get('region'),
        school=data.get('school'),
        class_name=class_name,
        referred_by=data.get('referred_by')
    )
    
    pending_pdf = data.get('pending_pdf')
    state.clear_user_state(user_id)
    
    bot.send_message(user_id, texts.REG_SUCCESS, parse_mode='Markdown', reply_markup=utils.create_main_menu_keyboard())
    
    if pending_pdf:
        handle_pdf_share(user_id, pending_pdf)

@bot.callback_query_handler(func=lambda call: call.data.startswith('back_'))
def back_callback(call):
    user_id = call.from_user.id
    current_state, data = state.get_user_state(user_id)
    if current_state != 'register':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    back_to = call.data.split('_')[1]
    if back_to == 'region':
        if DEBUG:
            print(f"🔙 User {user_id} went back to region selection")
        data['step'] = 'region'
        state.set_user_state(user_id, current_state, data)
        markup = InlineKeyboardMarkup(row_width=2)
        for region in texts.form_four_schools_by_region.keys():
            markup.add(InlineKeyboardButton(region, callback_data=f"region_{region}"))
        markup.add(InlineKeyboardButton(texts.BUTTON_REGION_NOT_LISTED, callback_data="manual_region_start"))
        bot.edit_message_text(texts.REG_REGION, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
    elif back_to == 'school':
        if DEBUG:
            print(f"🔙 User {user_id} went back to school selection")
        data['step'] = 'school'
        data['schools_page'] = 0
        state.set_user_state(user_id, current_state, data)
        region = data.get('region')
        show_schools_page(user_id, region, 0, call.message.message_id)

# ==================== Upload Flow ====================
def start_upload(user_id):
    user = db.get_user(user_id)
    if not user:
        bot.send_message(user_id, texts.NOT_REGISTERED)
        return
    if DEBUG:
        print(f"📤 Upload started by user {user_id}")
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton(texts.BUTTON_FILE, callback_data="upload_file"),
               InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    bot.send_message(user_id, texts.UPLOAD_START, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "upload_file")
def upload_method_callback(call):
    user_id = call.from_user.id
    # Set state to upload with step waiting for file
    state.set_user_state(user_id, 'upload', {'step': 'waiting_for_file', 'method': 'file'})
    bot.send_message(user_id, texts.UPLOAD_FILE_PROMPT, parse_mode='Markdown', reply_markup=utils.create_cancel_keyboard())
    bot.answer_callback_query(call.id)
    if DEBUG:
        print(f"📤 Upload file requested by user {user_id}")

def handle_upload(message, data):
    """Handle upload state - expecting PDF file"""
    user_id = message.from_user.id
    step = data.get('step')
    
    if DEBUG:
        print(f"📥 handle_upload called for user {user_id}, step: {step}")
    
    if step == 'waiting_for_file':
        # Check if user sent a PDF document
        if message.document and message.document.mime_type == 'application/pdf':
            # Check file size
            if message.document.file_size > MAX_FILE_SIZE:
                bot.send_message(user_id, texts.UPLOAD_TOO_LARGE.format(max_size=MAX_FILE_SIZE // (1024*1024)), parse_mode='Markdown')
                return
            
            # Save file info
            data['file_id'] = message.document.file_id
            data['file_name'] = message.document.file_name
            data['step'] = 'subject'
            state.set_user_state(user_id, 'upload', data)
            
            if DEBUG:
                print(f"✅ PDF received from {user_id}: {message.document.file_name}")
            
            # Ask for subject
            ask_subject(user_id)
        else:
            # Not a PDF file
            bot.send_message(user_id, texts.UPLOAD_INVALID_FILE, parse_mode='Markdown')
    else:
        # If not in waiting_for_file state, ignore
        if DEBUG:
            print(f"⚠️ User {user_id} in upload but step is {step}, ignoring")
        pass

def ask_subject(user_id):
    """Ask user to select subject for the PDF"""
    markup = InlineKeyboardMarkup(row_width=3)
    for subject in texts.SUBJECTS:
        markup.add(InlineKeyboardButton(subject, callback_data=f"subject_{subject}"))
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    bot.send_message(user_id, texts.UPLOAD_SUBJECT, parse_mode='Markdown', reply_markup=markup)
    if DEBUG:
        print(f"📚 Asked for subject from user {user_id}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('subject_'))
def subject_callback(call):
    user_id = call.from_user.id
    current_state, data = state.get_user_state(user_id)
    
    if DEBUG:
        print(f"📚 Subject callback: state={current_state}, data={data}")
    
    if current_state != 'upload' or data.get('step') != 'subject':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    subject = call.data.split('_')[1]
    data['subject'] = subject
    data['step'] = 'tag'
    state.set_user_state(user_id, current_state, data)
    
    if DEBUG:
        print(f"📚 Subject selected by {user_id}: {subject}")
    
    # Ask for tag
    markup = InlineKeyboardMarkup(row_width=2)
    for tag in texts.TAGS:
        markup.add(InlineKeyboardButton(tag, callback_data=f"tag_{tag}"))
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    bot.edit_message_text(
        texts.UPLOAD_TAG, 
        user_id, 
        call.message.message_id, 
        parse_mode='Markdown', 
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('tag_'))
def tag_callback(call):
    user_id = call.from_user.id
    current_state, data = state.get_user_state(user_id)
    
    if DEBUG:
        print(f"🏷️ Tag callback: state={current_state}, data={data}")
    
    if current_state != 'upload' or data.get('step') != 'tag':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    
    tag = call.data.split('_')[1]
    data['tag'] = tag
    data['step'] = 'finish'
    state.set_user_state(user_id, current_state, data)
    
    if DEBUG:
        print(f"🏷️ Tag selected by {user_id}: {tag}")
    
    finish_upload(user_id, call.message.message_id)
    bot.answer_callback_query(call.id)

def finish_upload(user_id, message_id=None):
    """Save PDF to database and complete upload"""
    current_state, data = state.get_user_state(user_id)
    
    if DEBUG:
        print(f"🎯 finish_upload called for user {user_id}, state={current_state}")
    
    if not current_state or data.get('step') != 'finish':
        if DEBUG:
            print(f"⚠️ Not in finish state, current step: {data.get('step') if data else 'None'}")
        return
    
    file_id = data.get('file_id')
    file_name = data.get('file_name')
    subject = data['subject']
    tag = data['tag']
    
    if not file_id or not file_name:
        bot.send_message(user_id, texts.UPLOAD_FAILED, parse_mode='Markdown')
        state.clear_user_state(user_id)
        return
    
    # Save to database
    pdf_id = db.add_pdf(
        file_id=file_id,
        file_name=file_name,
        user_id=user_id,
        subject=subject,
        tag=tag,
        exam_year=None
    )
    
    state.clear_user_state(user_id)
    
    if DEBUG:
        print(f"✅ PDF uploaded by {user_id}: {file_name} (ID: {pdf_id})")
    
    msg = texts.UPLOAD_SUCCESS.format(pdf_id=pdf_id)
    bot.send_message(user_id, msg, parse_mode='Markdown', reply_markup=utils.create_main_menu_keyboard())
    
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
    markup = InlineKeyboardMarkup(row_width=3)
    for subject in texts.SUBJECTS:
        markup.add(InlineKeyboardButton(subject, callback_data=f"search_subject_{subject}"))
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    bot.send_message(user_id, texts.SEARCH_START, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('search_subject_'))
def search_subject_callback(call):
    user_id = call.from_user.id
    subject = call.data.split('_')[2]
    state.set_user_state(user_id, 'search', {'subject': subject, 'step': 'tag'})
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Skip", callback_data="search_tag_skip"))
    for tag in texts.TAGS:
        markup.add(InlineKeyboardButton(tag, callback_data=f"search_tag_{tag}"))
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    bot.edit_message_text(texts.SEARCH_SUBJECT_SELECTED.format(subject=subject), user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('search_tag_'))
def search_tag_callback(call):
    user_id = call.from_user.id
    current_state, data = state.get_user_state(user_id)
    if current_state != 'search' or data.get('step') != 'tag':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    tag = call.data.split('_')[2]
    if tag == 'skip':
        tag = None
    data['tag'] = tag
    data['step'] = 'results'
    data['page'] = 0
    state.set_user_state(user_id, current_state, data)
    show_search_results(user_id, call.message.message_id)

def show_search_results(user_id, message_id=None):
    current_state, data = state.get_user_state(user_id)
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
        bot.send_message(user_id, texts.SEARCH_NO_RESULTS, parse_mode='Markdown', reply_markup=utils.create_main_menu_keyboard())
        state.clear_user_state(user_id)
        return
    pdfs = db.get_pdfs_by_filters(subject=subject, tag=tag, limit=limit, offset=offset)
    text = texts.SEARCH_RESULTS.format(page=page+1, total_pages=total_pages)
    for idx, pdf in enumerate(pdfs, start=1):
        text += texts.SEARCH_RESULT_ITEM.format(
            number=idx,
            name=pdf['file_name'],
            subject=pdf['subject'],
            tag=pdf['tag'],
            likes=pdf['like_count'],
            id=pdf['id']
        )
    markup = InlineKeyboardMarkup()
    if page > 0:
        markup.add(InlineKeyboardButton(texts.BUTTON_PREV, callback_data="search_prev"))
    if page < total_pages - 1:
        markup.add(InlineKeyboardButton(texts.BUTTON_NEXT, callback_data="search_next"))
    for pdf in pdfs:
        markup.add(InlineKeyboardButton(f"📄 {pdf['file_name'][:30]}", callback_data=f"view_{pdf['id']}"))
    markup.add(InlineKeyboardButton(texts.SEARCH_NEW, callback_data="search_new"))
    markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
    if message_id:
        bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "search_next")
def search_next_callback(call):
    user_id = call.from_user.id
    current_state, data = state.get_user_state(user_id)
    if current_state != 'search' or data.get('step') != 'results':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    data['page'] += 1
    state.set_user_state(user_id, current_state, data)
    show_search_results(user_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "search_prev")
def search_prev_callback(call):
    user_id = call.from_user.id
    current_state, data = state.get_user_state(user_id)
    if current_state != 'search' or data.get('step') != 'results':
        bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
        return
    data['page'] -= 1
    state.set_user_state(user_id, current_state, data)
    show_search_results(user_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "search_new")
def search_new_callback(call):
    user_id = call.from_user.id
    state.clear_user_state(user_id)
    start_search(user_id)
    bot.delete_message(user_id, call.message.message_id)

# ==================== PDF View Actions ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith('view_'))
def view_pdf_callback(call):
    user_id = call.from_user.id
    pdf_id = int(call.data.split('_')[1])
    pdf = db.get_pdf(pdf_id)
    if not pdf:
        bot.answer_callback_query(call.id, texts.ERROR_NOT_FOUND)
        return
    if not pdf['is_approved'] and not is_admin(user_id) and pdf['uploaded_by'] != user_id:
        bot.answer_callback_query(call.id, "This PDF is pending approval.")
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

@bot.callback_query_handler(func=lambda call: call.data.startswith('download_'))
def download_pdf_callback(call):
    user_id = call.from_user.id
    pdf_id = int(call.data.split('_')[1])
    pdf = db.get_pdf(pdf_id)
    if not pdf:
        bot.answer_callback_query(call.id, texts.ERROR_NOT_FOUND)
        return
    if pdf['file_id']:
        try:
            bot.send_document(user_id, pdf['file_id'], caption=f"📄 {pdf['file_name']}")
            db.increment_download(pdf_id, user_id)
            if DEBUG:
                print(f"📥 PDF downloaded by {user_id}: {pdf['file_name']} (ID: {pdf_id})")
            bot.answer_callback_query(call.id, texts.PDF_DOWNLOAD_STARTED)
        except Exception as e:
            if DEBUG:
                print(f"❌ Download failed for {user_id}: {e}")
            bot.answer_callback_query(call.id, texts.PDF_DOWNLOAD_FAILED)
    else:
        bot.answer_callback_query(call.id, "No file available.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('like_') or call.data.startswith('unlike_'))
def like_callback(call):
    user_id = call.from_user.id
    action, pdf_id = call.data.split('_')
    pdf_id = int(pdf_id)
    if action == 'like':
        if db.like_pdf(pdf_id, user_id):
            if DEBUG:
                print(f"❤️ PDF liked by {user_id}: {pdf_id}")
            bot.answer_callback_query(call.id, texts.PDF_LIKED)
        else:
            bot.answer_callback_query(call.id, "You already liked this.")
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
        bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('report_'))
def report_callback(call):
    user_id = call.from_user.id
    pdf_id = int(call.data.split('_')[1])
    state.set_user_state(user_id, 'report', {'pdf_id': pdf_id})
    bot.send_message(user_id, texts.PDF_REPORT_PROMPT, parse_mode='Markdown', reply_markup=utils.create_cancel_keyboard())
    bot.answer_callback_query(call.id)

def handle_report(message, data):
    user_id = message.from_user.id
    pdf_id = data['pdf_id']
    report_text = message.text
    db.add_report(pdf_id, user_id, report_text)
    if DEBUG:
        print(f"⚠️ Report submitted by {user_id} for PDF {pdf_id}: {report_text[:50]}...")
    pdf = db.get_pdf(pdf_id)
    if pdf:
        uploader = db.get_user(pdf['uploaded_by'])
        if uploader:
            bot.send_message(uploader['user_id'], texts.REPORT_NOTIFY_UPLOADER.format(
                pdf_name=pdf['file_name'],
                reporter=message.from_user.full_name or message.from_user.first_name,
                reason=report_text
            ), parse_mode='Markdown')
    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, texts.REPORT_NOTIFY_ADMIN.format(
            pdf_name=pdf['file_name'],
            pdf_id=pdf_id,
            uploader=uploader['full_name'] if uploader else "Unknown",
            reporter=message.from_user.full_name or message.from_user.first_name,
            reason=report_text
        ), parse_mode='Markdown')
    state.clear_user_state(user_id)
    bot.send_message(user_id, texts.PDF_REPORT_SENT, parse_mode='Markdown', reply_markup=utils.create_main_menu_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith('share_'))
def share_callback(call):
    user_id = call.from_user.id
    pdf_id = int(call.data.split('_')[1])
    share_link = f"https://t.me/{BOT_USERNAME}?start=pdf_{pdf_id}"
    bot.send_message(user_id, f"🔗 Share this link:\n\n{share_link}", parse_mode='Markdown')
    bot.answer_callback_query(call.id)

# ==================== Profile ====================
def show_profile(user_id):
    user = db.get_user(user_id)
    if not user:
        bot.send_message(user_id, texts.NOT_REGISTERED)
        return
    uploads_count = db.get_user_upload_count(user_id)
    downloads_count = db.get_user_download_count(user_id)
    text = texts.PROFILE_DISPLAY.format(
        name=user['full_name'],
        user_id=user_id,
        phone=user['phone'] or "Not set",
        class_=user['class'] or "Not set",
        region=user['region'] or "Not set",
        school=user['school'] or "Not set",
        joined=utils.format_date(user['join_date']),
        uploads=uploads_count,
        downloads=downloads_count
    )
    stats = db.get_user_referral_stats(user_id)
    text += texts.PROFILE_REFERRAL.format(
        bot_username=BOT_USERNAME,
        user_id=user_id,
        conversions=stats['conversions']
    )
    if DEBUG:
        print(f"👤 Profile viewed by user {user_id}")
    bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=utils.create_main_menu_keyboard())

# ==================== Admin Panel ====================
def show_admin_panel(user_id):
    if DEBUG:
        print(f"👑 Admin panel opened by {user_id}")
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
               InlineKeyboardButton("👥 Users", callback_data="admin_users"))
    markup.add(InlineKeyboardButton("⏳ Pending PDFs", callback_data="admin_pending"),
               InlineKeyboardButton("🚨 Reports", callback_data="admin_reports"))
    markup.add(InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
               InlineKeyboardButton("🔧 SQL", callback_data="admin_sql"))
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="cancel"))
    bot.send_message(user_id, texts.ADMIN_PANEL, parse_mode='Markdown', reply_markup=markup)

def show_users_page(user_id, page, message_id):
    limit = 10
    offset = page * limit
    users = db.get_all_users(limit=limit, offset=offset)
    total = db.count_users()
    total_pages = (total + limit - 1) // limit

    text = texts.ADMIN_USER_LIST
    for idx, u in enumerate(users, start=offset+1):
        status = "🚫 " if u['is_banned'] else "✅ "
        role = "👑 " if u['is_admin'] else "👤 "
        text += texts.ADMIN_USER_ITEM.format(
            status=status, role=role, name=u['full_name'],
            id=u['user_id'], class_=u['class'] or '-', school=u['school'] or '-'
        )
    markup = InlineKeyboardMarkup()
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀ Prev", callback_data="admin_users_prev"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶", callback_data="admin_users_next"))
    if nav_buttons:
        markup.row(*nav_buttons)
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back"))
    bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_callback(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, texts.ERROR_PERMISSION)
        return
    action = call.data.split('_')[1]
    if action == 'stats':
        stats = db.get_stats()
        text = texts.ADMIN_STATS.format(**stats)
        bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown')
        if DEBUG:
            print(f"📊 Stats viewed by admin {user_id}")
    elif action == 'users':
        page = 0
        state.set_user_state(user_id, 'admin_users', {'page': page})
        show_users_page(user_id, page, call.message.message_id)
    elif action == 'pending':
        pending = db.get_unapproved_pdfs()
        if not pending:
            bot.edit_message_text("No pending PDFs.", user_id, call.message.message_id)
            return
        text = texts.ADMIN_PDF_PENDING_LIST
        for idx, pdf in enumerate(pending, start=1):
            uploader = db.get_user(pdf['uploaded_by'])
            text += texts.ADMIN_PDF_PENDING_ITEM.format(
                number=idx,
                name=pdf['file_name'],
                subject=pdf['subject'],
                tag=pdf['tag'],
                uploader=uploader['full_name'] if uploader else 'Unknown',
                id=pdf['id']
            )
        markup = InlineKeyboardMarkup(row_width=2)
        for pdf in pending:
            markup.add(InlineKeyboardButton(f"✅ {pdf['file_name'][:20]}", callback_data=f"approve_{pdf['id']}"),
                       InlineKeyboardButton(f"❌ Delete", callback_data=f"delete_{pdf['id']}"))
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back"))
        bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
    elif action == 'reports':
        reports = db.get_pending_reports()
        if not reports:
            bot.edit_message_text("No pending reports.", user_id, call.message.message_id)
            return
        text = texts.ADMIN_REPORT_LIST
        for idx, r in enumerate(reports, start=1):
            text += texts.ADMIN_REPORT_ITEM.format(
                number=idx,
                pdf_name=r['pdf_name'],
                pdf_id=r['pdf_id'],
                reporter=r['reporter_name'] or f"ID:{r['reported_by']}",
                reason=r['report_text']
            )
        markup = InlineKeyboardMarkup()
        for r in reports:
            markup.add(InlineKeyboardButton(f"✅ Resolve report {r['id']}", callback_data=f"resolve_{r['id']}"))
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back"))
        bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
    elif action == 'broadcast':
        state.set_user_state(user_id, 'admin_broadcast', {})
        bot.send_message(user_id, texts.ADMIN_BROADCAST_PROMPT, parse_mode='Markdown', reply_markup=utils.create_cancel_keyboard())
        bot.answer_callback_query(call.id)
    elif action == 'sql':
        state.set_user_state(user_id, 'admin_sql', {})
        bot.send_message(user_id, texts.ADMIN_SQL_PROMPT, parse_mode='Markdown', reply_markup=utils.create_cancel_keyboard())
        bot.answer_callback_query(call.id)
    elif action == 'back':
        show_admin_panel(user_id)
        bot.delete_message(user_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_users_next")
def admin_users_next(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, texts.ERROR_PERMISSION)
        return
    current_state, data = state.get_user_state(user_id)
    if current_state != 'admin_users':
        data = {'page': 0}
    page = data.get('page', 0) + 1
    data['page'] = page
    state.set_user_state(user_id, 'admin_users', data)
    show_users_page(user_id, page, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_users_prev")
def admin_users_prev(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, texts.ERROR_PERMISSION)
        return
    current_state, data = state.get_user_state(user_id)
    if current_state != 'admin_users':
        data = {'page': 1}
    page = data.get('page', 0) - 1
    if page < 0:
        page = 0
    data['page'] = page
    state.set_user_state(user_id, 'admin_users', data)
    show_users_page(user_id, page, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def approve_pdf_callback(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, texts.ERROR_PERMISSION)
        return
    pdf_id = int(call.data.split('_')[1])
    db.approve_pdf(pdf_id)
    if DEBUG:
        print(f"✅ PDF {pdf_id} approved by admin {user_id}")
    bot.answer_callback_query(call.id, texts.ADMIN_PDF_APPROVE_SUCCESS)
    bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=None)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_pdf_callback(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, texts.ERROR_PERMISSION)
        return
    pdf_id = int(call.data.split('_')[1])
    db.delete_pdf(pdf_id)
    if DEBUG:
        print(f"🗑️ PDF {pdf_id} deleted by admin {user_id}")
    bot.answer_callback_query(call.id, texts.ADMIN_PDF_DELETE_SUCCESS)
    bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=None)

@bot.callback_query_handler(func=lambda call: call.data.startswith('resolve_'))
def resolve_report_callback(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, texts.ERROR_PERMISSION)
        return
    report_id = int(call.data.split('_')[1])
    db.resolve_report(report_id)
    if DEBUG:
        print(f"✅ Report {report_id} resolved by admin {user_id}")
    bot.answer_callback_query(call.id, texts.ADMIN_REPORT_RESOLVE_SUCCESS)
    bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=None)

def handle_admin_broadcast(message, data):
    user_id = message.from_user.id
    text = message.text
    users = db.get_all_users()
    count = 0
    for user in users:
        try:
            bot.send_message(user['user_id'], text, parse_mode='Markdown')
            count += 1
        except:
            pass
    state.clear_user_state(user_id)
    if DEBUG:
        print(f"📢 Broadcast sent by admin {user_id} to {count} users")
    bot.send_message(user_id, texts.ADMIN_BROADCAST_CONFIRM.format(count=count), parse_mode='Markdown', reply_markup=utils.create_main_menu_keyboard())

def handle_admin_sql(message, data):
    user_id = message.from_user.id
    sql = message.text
    result = db.execute_sql(sql)
    state.clear_user_state(user_id)
    result_str = str(result)
    if len(result_str) > 4000:
        result_str = result_str[:4000] + "...(truncated)"
    if DEBUG:
        print(f"🔧 SQL executed by admin {user_id}")
    bot.send_message(user_id, texts.ADMIN_SQL_RESULT.format(result=result_str), parse_mode='Markdown', reply_markup=utils.create_main_menu_keyboard())

# ==================== Shared PDF Link Handler ====================
def handle_pdf_share(user_id, pdf_id):
    pdf = db.get_pdf(pdf_id)
    if not pdf:
        bot.send_message(user_id, "PDF not found.")
        return
    user = db.get_user(user_id)
    if not user:
        state.set_user_state(user_id, 'register', {'step': 'name', 'pending_pdf': pdf_id})
        bot.send_message(user_id, "Please register first to view the PDF.")
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

# ==================== Channel Check Callback ====================
@bot.callback_query_handler(func=lambda call: call.data == "check_channel")
def check_channel_callback(call):
    user_id = call.from_user.id
    if utils.is_channel_member(bot, user_id, REQUIRED_CHANNEL):
        if DEBUG:
            print(f"✅ User {user_id} confirmed channel membership")
        bot.answer_callback_query(call.id, "✅ You are now a member! Please use /start again.")
        bot.delete_message(user_id, call.message.message_id)
        start_command(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ You are not a member yet. Please join the channel first.", show_alert=True)

# ==================== Cancel ====================
@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def cancel_callback(call):
    user_id = call.from_user.id
    state.clear_user_state(user_id)
    if DEBUG:
        print(f"❌ Operation cancelled by user {user_id}")
    bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=None)
    bot.send_message(user_id, texts.CANCELLED, parse_mode='Markdown', reply_markup=utils.create_main_menu_keyboard())