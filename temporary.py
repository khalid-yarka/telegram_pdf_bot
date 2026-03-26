# pdf_manager_bot.py
# Complete PDF Manager Bot - With Like/Unlike and Reply-based UI

import sqlite3
import os
import uuid
from datetime import datetime

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ==================== CONFIGURATION ====================
TOKEN = "6514233351:AAFMLJY1uEFDl2F5EBn0eBoWlYCnY_mmoJM"
ADMIN_IDS = [2094426161]

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "bot.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Your subjects
SUBJECTS = [
    "Math", "Physics", "Chemistry", "Biology", "ICT",
    "Arabic", "Islamic", "English", "Somali", "G.P",
    "Geography", "History", "Agriculture", "Business"
]

# Your tags
TAGS = [
    "Q/A", "Book", "Assignment", "W_Exam", "T1_Exam", 
    "T2_Exam", "E_Answered", "C_Answered", "A_Answered",
    "Exam", "Notes", "Summary", "Reviews"
]

# ==================== DATABASE FUNCTIONS ====================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def pdf_exists_by_file_id(file_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, file_name FROM pdfs WHERE file_id = ?', (file_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def add_pdf(file_id, file_name, user_id, subject, tag):
    conn = get_db()
    cursor = conn.cursor()
    
    existing = pdf_exists_by_file_id(file_id)
    if existing:
        conn.close()
        return None, True, existing['id']
    
    cursor.execute('''
        INSERT INTO pdfs (file_id, file_name, uploaded_by, upload_date, subject, tag, is_approved, download_count, like_count)
        VALUES (?, ?, ?, ?, ?, ?, 1, 0, 0)
    ''', (file_id, file_name, user_id, datetime.now(), subject, tag))
    
    pdf_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return pdf_id, False, None

def get_pdf(pdf_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pdfs WHERE id = ?', (pdf_id,))
    pdf = cursor.fetchone()
    conn.close()
    return pdf

def like_pdf(pdf_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM user_likes WHERE user_id = ? AND pdf_id = ?', (user_id, pdf_id))
    if cursor.fetchone():
        conn.close()
        return False
    
    cursor.execute('INSERT INTO user_likes (user_id, pdf_id) VALUES (?, ?)', (user_id, pdf_id))
    cursor.execute('UPDATE pdfs SET like_count = like_count + 1 WHERE id = ?', (pdf_id,))
    conn.commit()
    conn.close()
    return True

def unlike_pdf(pdf_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_likes WHERE user_id = ? AND pdf_id = ?', (user_id, pdf_id))
    cursor.execute('UPDATE pdfs SET like_count = like_count - 1 WHERE id = ?', (pdf_id,))
    conn.commit()
    conn.close()

def has_liked(pdf_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_likes WHERE user_id = ? AND pdf_id = ?', (user_id, pdf_id))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def increment_download(pdf_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE pdfs SET download_count = download_count + 1 WHERE id = ?', (pdf_id,))
    cursor.execute('INSERT INTO downloads (pdf_id, user_id, download_date) VALUES (?, ?, ?)',
                   (pdf_id, user_id, datetime.now()))
    conn.commit()
    conn.close()

def get_pdfs_by_filters(subject=None, tag=None, limit=10, offset=0):
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM pdfs WHERE is_approved = 1"
    params = []
    
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if tag:
        query += " AND tag = ?"
        params.append(tag)
    
    query += " ORDER BY upload_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    pdfs = cursor.fetchall()
    conn.close()
    return pdfs

def count_pdfs_by_filters(subject=None, tag=None):
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT COUNT(*) FROM pdfs WHERE is_approved = 1"
    params = []
    
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if tag:
        query += " AND tag = ?"
        params.append(tag)
    
    cursor.execute(query, params)
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_user_uploads(user_id, limit=10, offset=0):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM pdfs WHERE uploaded_by = ? ORDER BY upload_date DESC LIMIT ? OFFSET ?
    ''', (user_id, limit, offset))
    pdfs = cursor.fetchall()
    conn.close()
    return pdfs

def count_user_uploads(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM pdfs WHERE uploaded_by = ?', (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    total_users = cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_pdfs = cursor.execute('SELECT COUNT(*) FROM pdfs WHERE is_approved = 1').fetchone()[0]
    total_downloads = cursor.execute('SELECT SUM(download_count) FROM pdfs').fetchone()[0] or 0
    my_uploads = cursor.execute('SELECT COUNT(*) FROM pdfs WHERE uploaded_by = ?', (2094426161,)).fetchone()[0]
    conn.close()
    return {'total_users': total_users, 'total_pdfs': total_pdfs, 'total_downloads': total_downloads, 'my_uploads': my_uploads}

# ==================== MULTI-PDF SESSION STORAGE ====================

sessions = {}

def generate_session_id():
    return uuid.uuid4().hex[:12]

def get_session(user_id, session_id):
    if user_id in sessions and session_id in sessions[user_id]:
        return sessions[user_id][session_id]
    return None

def set_session(user_id, session_id, state, data=None):
    if user_id not in sessions:
        sessions[user_id] = {}
    sessions[user_id][session_id] = {
        'state': state,
        'data': data or {},
        'created_at': datetime.now()
    }

def update_session(user_id, session_id, state=None, data=None):
    if user_id in sessions and session_id in sessions[user_id]:
        if state:
            sessions[user_id][session_id]['state'] = state
        if data:
            sessions[user_id][session_id]['data'].update(data)

def clear_session(user_id, session_id):
    if user_id in sessions and session_id in sessions[user_id]:
        del sessions[user_id][session_id]
        if not sessions[user_id]:
            del sessions[user_id]

def format_file_size(bytes_size):
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"

def get_pdf_emoji(tag):
    emojis = {
        "Q/A": "❓", "Book": "📖", "Assignment": "✏️",
        "W_Exam": "📝", "T1_Exam": "📝", "T2_Exam": "📝",
        "E_Answered": "✅", "C_Answered": "✅", "A_Answered": "✅",
        "Exam": "📝", "Notes": "📘", "Summary": "📋", "Reviews": "📚"
    }
    return emojis.get(tag, "📄")

# ==================== KEYBOARDS ====================

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📤 Upload PDF"),
        KeyboardButton("🔍 Search PDFs")
    )
    markup.add(
        KeyboardButton("📊 My Uploads"),
        KeyboardButton("📈 Stats")
    )
    markup.add(
        KeyboardButton("👤 My Profile"),
        KeyboardButton("❓ Help")
    )
    return markup

def cancel_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("❌ Cancel"))
    return markup

def subject_keyboard(session_id):
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    for subject in SUBJECTS:
        buttons.append(InlineKeyboardButton(subject, callback_data=f"subj_{session_id}_{subject}"))
    for i in range(0, len(buttons), 3):
        markup.row(*buttons[i:i+3])
    markup.add(InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{session_id}"))
    return markup

def tag_keyboard(session_id):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for tag in TAGS:
        buttons.append(InlineKeyboardButton(tag, callback_data=f"tag_{session_id}_{tag}"))
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i+2])
    markup.row(
        InlineKeyboardButton("⏭️ Skip Tag", callback_data=f"tag_{session_id}_skip"),
        InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{session_id}")
    )
    return markup

def search_subject_keyboard():
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(s, callback_data=f"search_subj_{s}") for s in SUBJECTS]
    for i in range(0, len(buttons), 3):
        markup.row(*buttons[i:i+3])
    markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel_search"))
    return markup

def search_tag_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(t, callback_data=f"search_tag_{t}") for t in TAGS]
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i+2])
    markup.row(
        InlineKeyboardButton("📚 All Tags", callback_data="search_tag_all"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_search")
    )
    return markup

def pdf_action_buttons(pdf_id, user_id):
    """PDF action buttons with Like/Unlike"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    if has_liked(pdf_id, user_id):
        like_text = "💔 Unlike"
        like_callback = f"unlike_{pdf_id}"
    else:
        like_text = "❤️ Like"
        like_callback = f"like_{pdf_id}"
    
    markup.add(
        InlineKeyboardButton(like_text, callback_data=like_callback),
        InlineKeyboardButton("📥 Download", callback_data=f"down_{pdf_id}")
    )
    markup.add(
        InlineKeyboardButton("🔗 Share", callback_data=f"share_{pdf_id}"),
        InlineKeyboardButton("🔙 Back", callback_data="search_new")
    )
    return markup

def share_buttons(pdf_id):
    share_link = f"https://t.me/Ardayda_bot?start=pdf_{pdf_id}"
    whatsapp_link = f"https://wa.me/?text={share_link.replace('&', '%26')}"
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📱 Telegram", url=f"https://t.me/share/url?url={share_link}&text=📚 Check out this PDF!"),
        InlineKeyboardButton("💬 WhatsApp", url=whatsapp_link)
    )
    markup.add(InlineKeyboardButton("🔙 Back", callback_data=f"view_{pdf_id}"))
    return markup

def pagination_buttons(page, total_pages, subject, tag):
    markup = InlineKeyboardMarkup(row_width=3)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"page_{page-1}_{subject}_{tag or 'all'}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("Next ▶️", callback_data=f"page_{page+1}_{subject}_{tag or 'all'}"))
    if nav:
        markup.row(*nav)
    markup.add(InlineKeyboardButton("🔄 New Search", callback_data="search_new"))
    return markup

# ==================== BOT ====================

bot = telebot.TeleBot(TOKEN)

# ==================== COMMANDS ====================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if user:
        welcome = f"🎉 Welcome back, **{user['full_name']}!**\n\n"
    else:
        welcome = f"🎉 Welcome to PDF Manager Bot!\n\n"
    
    welcome += (
        f"📤 **Upload PDF** - Send PDF, choose subject & tag\n"
        f"🔍 **Search PDFs** - Find by subject and tag\n"
        f"📊 **My Uploads** - View your uploaded PDFs\n"
        f"📈 **Stats** - Bot statistics\n"
        f"👤 **My Profile** - View your info\n\n"
        f"❤️ **Like** - Support good PDFs\n"
        f"📥 **Download** - Get PDFs\n"
        f"🔗 **Share** - Share with friends\n\n"
        f"⚠️ **Note:** Duplicate files are automatically prevented!"
    )
    
    bot.send_message(user_id, welcome, parse_mode='Markdown', reply_markup=main_menu())

@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.from_user.id
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_size = format_file_size(message.document.file_size)
    session_id = generate_session_id()
    
    if message.document.mime_type != 'application/pdf':
        bot.reply_to(message, "❌ Please send a **PDF** file.", parse_mode='Markdown')
        return
    
    # Check for duplicate
    existing = pdf_exists_by_file_id(file_id)
    if existing:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👁️ View PDF", callback_data=f"view_{existing['id']}"))
        bot.reply_to(
            message,
            f"⚠️ **Duplicate File!**\n\n"
            f"📄 `{file_name}` already exists.\n"
            f"🆔 **ID:** `{existing['id']}`",
            parse_mode='Markdown',
            reply_markup=markup
        )
        return
    
    # Store session
    set_session(user_id, session_id, 'confirm', {
        'file_id': file_id,
        'file_name': file_name,
        'file_size': file_size
    })
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Yes, Upload", callback_data=f"confirm_{session_id}"),
        InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{session_id}")
    )
    
    # Reply to the sent PDF
    bot.reply_to(
        message,
        f"📄 **PDF Received!**\n\n"
        f"📌 `{file_name}`\n"
        f"📦 {file_size}\n\n"
        f"**Upload this PDF?**",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text
    
    if text == "❌ Cancel":
        if user_id in sessions:
            del sessions[user_id]
        bot.send_message(user_id, "❌ All uploads cancelled.", reply_markup=main_menu())
        return
    
    if text == "📤 Upload PDF":
        bot.send_message(user_id, "📤 Send me a **PDF** file:", parse_mode='Markdown', reply_markup=cancel_keyboard())
    
    elif text == "🔍 Search PDFs":
        bot.send_message(user_id, "🔍 Select **subject**:", parse_mode='Markdown', reply_markup=search_subject_keyboard())
    
    elif text == "📊 My Uploads":
        total = count_user_uploads(user_id)
        if total == 0:
            bot.send_message(user_id, "📭 No uploads yet.", reply_markup=main_menu())
            return
        
        pdfs = get_user_uploads(user_id, limit=10)
        msg = f"📊 **Your Uploads** ({total})\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        for pdf in pdfs:
            emoji = get_pdf_emoji(pdf['tag'])
            msg += f"{emoji} **{pdf['file_name'][:40]}**\n"
            msg += f"   📚 `{pdf['subject']}` | 🏷️ `{pdf['tag'] or 'None'}`\n"
            msg += f"   ❤️ `{pdf['like_count']}` | 📥 `{pdf['download_count']}`\n"
            msg += f"   🆔 `{pdf['id']}`\n\n"
        bot.send_message(user_id, msg, parse_mode='Markdown', reply_markup=main_menu())
    
    elif text == "📈 Stats":
        stats = get_stats()
        bot.send_message(
            user_id,
            f"📊 **Statistics**\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Users: `{stats['total_users']}`\n"
            f"📄 PDFs: `{stats['total_pdfs']}`\n"
            f"📥 Downloads: `{stats['total_downloads']}`\n"
            f"📤 Your Uploads: `{stats['my_uploads']}`",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
    
    elif text == "👤 My Profile":
        user = get_user(user_id)
        if not user:
            bot.send_message(user_id, "❌ Please /start first.", reply_markup=main_menu())
            return
        
        uploads = count_user_uploads(user_id)
        downloads = 0
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM downloads WHERE user_id = ?', (user_id,))
        downloads = cursor.fetchone()[0]
        conn.close()
        
        profile = (
            f"👤 **My Profile**\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"📛 **Name:** `{user['full_name']}`\n"
            f"🆔 **ID:** `{user_id}`\n"
            f"📞 **Phone:** `{user['phone'] or 'Not set'}`\n"
            f"🎓 **Class:** `{user['class'] or 'Not set'}`\n"
            f"📍 **Region:** `{user['region'] or 'Not set'}`\n"
            f"🏫 **School:** `{user['school'] or 'Not set'}`\n"
            f"📅 **Joined:** `{user['join_date'][:19] if user['join_date'] else 'Unknown'}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📤 Uploads: `{uploads}` | 📥 Downloads: `{downloads}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 **Referral Link**\n\n"
            f"`https://t.me/Ardayda_bot?start=ref_{user_id}`"
        )
        bot.send_message(user_id, profile, parse_mode='Markdown', reply_markup=main_menu())
    
    elif text == "❓ Help":
        help_text = (
            f"❓ **Help**\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📤 **Upload:** Send PDF → Subject → Tag\n"
            f"🔍 **Search:** Subject → Tag → View\n"
            f"❤️ **Like:** Click heart on any PDF\n"
            f"📥 **Download:** Get PDF files\n"
            f"🔗 **Share:** Share PDFs with friends\n"
            f"📊 **My Uploads:** View your PDFs\n"
            f"👤 **Profile:** Your info & referral"
        )
        bot.send_message(user_id, help_text, parse_mode='Markdown', reply_markup=main_menu())
    
    else:
        bot.send_message(user_id, "Use buttons below.", reply_markup=main_menu())

# ==================== CALLBACKS ====================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    
    # Cancel for specific PDF
    if data.startswith("cancel_"):
        session_id = data[7:]
        clear_session(user_id, session_id)
        bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=None)
        bot.send_message(user_id, "❌ Cancelled.", reply_markup=main_menu())
        bot.answer_callback_query(call.id)
        return
    
    if data == "cancel_search":
        bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=None)
        bot.send_message(user_id, "❌ Cancelled.", reply_markup=main_menu())
        bot.answer_callback_query(call.id)
        return
    
    # Confirm upload
    if data.startswith("confirm_"):
        session_id = data[8:]
        session = get_session(user_id, session_id)
        
        if not session:
            bot.answer_callback_query(call.id, "Session expired.")
            bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=None)
            return
        
        update_session(user_id, session_id, 'upload', {
            'file_id': session['data']['file_id'],
            'file_name': session['data']['file_name']
        })
        
        bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=None)
        
        bot.send_message(
            user_id,
            f"✅ **Uploading:** `{session['data']['file_name']}`\n"
            f"📦 {session['data']['file_size']}\n\n"
            f"📚 **Select Subject:**",
            parse_mode='Markdown',
            reply_markup=subject_keyboard(session_id)
        )
        bot.answer_callback_query(call.id)
        return
    
    # Subject selection
    if data.startswith("subj_"):
        parts = data.split("_", 2)
        session_id = parts[1]
        subject = parts[2]
        
        session = get_session(user_id, session_id)
        if not session or session['state'] != 'upload':
            bot.answer_callback_query(call.id, "Session expired.")
            clear_session(user_id, session_id)
            return
        
        update_session(user_id, session_id, 'upload', {'subject': subject})
        
        bot.edit_message_text(
            f"✅ **Uploading:** `{session['data']['file_name']}`\n"
            f"📚 **Subject:** `{subject}`\n\n"
            f"🏷️ **Select Tag:**",
            user_id, call.message.message_id,
            parse_mode='Markdown',
            reply_markup=tag_keyboard(session_id)
        )
        bot.answer_callback_query(call.id)
        return
    
    # Tag selection
    if data.startswith("tag_"):
        parts = data.split("_", 2)
        session_id = parts[1]
        tag_value = parts[2] if parts[2] != 'skip' else None
        
        session = get_session(user_id, session_id)
        if not session or session['state'] != 'upload':
            bot.answer_callback_query(call.id, "Session expired.")
            clear_session(user_id, session_id)
            return
        
        subject = session['data'].get('subject')
        file_name = session['data']['file_name']
        file_id = session['data']['file_id']
        
        pdf_id, is_duplicate, existing_id = add_pdf(
            file_id=file_id,
            file_name=file_name,
            user_id=user_id,
            subject=subject,
            tag=tag_value
        )
        
        if is_duplicate:
            clear_session(user_id, session_id)
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("👁️ View", callback_data=f"view_{existing_id}"))
            bot.edit_message_text(
                f"⚠️ **Duplicate!**\n\n📄 `{file_name}` already exists.",
                user_id, call.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
            bot.answer_callback_query(call.id, "Duplicate!")
            return
        
        clear_session(user_id, session_id)
        uploader = get_user(user_id)
        uploader_name = uploader['full_name'] if uploader else "Unknown"
        
        success_text = (
            f"🎉 **PDF Uploaded!**\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📄 **File:** `{file_name}`\n"
            f"📚 **Subject:** `{subject}`\n"
            f"🏷️ **Tag:** `{tag_value or 'None'}`\n"
            f"👤 **Uploader:** `{uploader_name}`\n"
            f"📅 **Date:** `{datetime.now().strftime('%Y-%m-%d %I:%M %p')}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"❤️ **Likes:** 0 | 📥 **Downloads:** 0\n"
            f"🆔 **ID:** `{pdf_id}`"
        )
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("👁️ View PDF", callback_data=f"view_{pdf_id}"),
            InlineKeyboardButton("📤 Upload Another", callback_data="upload_another")
        )
        
        bot.edit_message_text(
            success_text,
            user_id, call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
        bot.answer_callback_query(call.id, "✅ Uploaded!")
        return
    
    if data == "upload_another":
        bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=None)
        bot.send_message(user_id, "📤 Send another PDF:", reply_markup=cancel_keyboard())
        bot.answer_callback_query(call.id)
        return
    
    # ==================== SEARCH ====================
    
    if data.startswith("search_subj_"):
        subject = data[11:]
        bot.edit_message_text(
            f"🔍 **Subject:** `{subject}`\n\n🏷️ **Select Tag:**",
            user_id, call.message.message_id,
            parse_mode='Markdown',
            reply_markup=search_tag_keyboard()
        )
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("search_tag_"):
        tag = data[10:] if data != "search_tag_all" else None
        
        msg_text = call.message.text
        subject = None
        for line in msg_text.split('\n'):
            if "Subject:" in line:
                subject = line.split("`")[1]
                break
        
        total = count_pdfs_by_filters(subject=subject, tag=tag)
        if total == 0:
            bot.edit_message_text(
                f"😕 **No Results**\n\n📚 `{subject}` | 🏷️ `{tag or 'All'}`",
                user_id, call.message.message_id,
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id)
            return
        
        show_results(user_id, call.message.message_id, subject, tag, 0)
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("page_"):
        parts = data.split("_")
        page = int(parts[1])
        subject = parts[2]
        tag = parts[3] if parts[3] != 'all' else None
        show_results(user_id, call.message.message_id, subject, tag, page)
        bot.answer_callback_query(call.id)
        return
    
    if data == "search_new":
        bot.edit_message_text(
            "🔍 **Select Subject:**",
            user_id, call.message.message_id,
            parse_mode='Markdown',
            reply_markup=search_subject_keyboard()
        )
        bot.answer_callback_query(call.id)
        return
    
    # ==================== PDF ACTIONS ====================
    
    if data.startswith("view_"):
        pdf_id = int(data[5:])
        pdf = get_pdf(pdf_id)
        if not pdf:
            bot.answer_callback_query(call.id, "Not found.")
            return
        
        uploader = get_user(pdf['uploaded_by'])
        uploader_name = uploader['full_name'] if uploader else "Unknown"
        
        text = (
            f"📄 **{pdf['file_name']}**\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"📚 `{pdf['subject']}` | 🏷️ `{pdf['tag'] or 'None'}`\n"
            f"👤 `{uploader_name}`\n"
            f"📅 `{pdf['upload_date'][:19]}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"❤️ `{pdf['like_count']}` | 📥 `{pdf['download_count']}`\n"
            f"🆔 `{pdf_id}`"
        )
        
        bot.edit_message_text(
            text, user_id, call.message.message_id,
            parse_mode='Markdown',
            reply_markup=pdf_action_buttons(pdf_id, user_id)
        )
        bot.answer_callback_query(call.id)
        return
    
    # Like button
    if data.startswith("like_"):
        pdf_id = int(data[5:])
        if like_pdf(pdf_id, user_id):
            bot.answer_callback_query(call.id, "❤️ Liked!")
        else:
            bot.answer_callback_query(call.id, "❤️ Already liked!")
        
        # Refresh view
        refresh_pdf_view(user_id, call.message.message_id, pdf_id)
        return
    
    # Unlike button
    if data.startswith("unlike_"):
        pdf_id = int(data[7:])
        unlike_pdf(pdf_id, user_id)
        bot.answer_callback_query(call.id, "💔 Unliked")
        
        # Refresh view
        refresh_pdf_view(user_id, call.message.message_id, pdf_id)
        return
    
    # Download button
    if data.startswith("down_"):
        pdf_id = int(data[5:])
        pdf = get_pdf(pdf_id)
        if pdf and pdf['file_id']:
            try:
                bot.send_document(user_id, pdf['file_id'], caption=f"📄 {pdf['file_name']}")
                increment_download(pdf_id, user_id)
                bot.answer_callback_query(call.id, "✅ Download started!")
            except:
                bot.answer_callback_query(call.id, "❌ Failed.")
        else:
            bot.answer_callback_query(call.id, "File not available.")
        return
    
    # Share button
    if data.startswith("share_"):
        pdf_id = int(data[6:])
        bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=share_buttons(pdf_id))
        bot.answer_callback_query(call.id)
        return
    
    bot.answer_callback_query(call.id, "Unknown")

def refresh_pdf_view(user_id, message_id, pdf_id):
    """Refresh PDF view after like/unlike"""
    pdf = get_pdf(pdf_id)
    if not pdf:
        return
    
    uploader = get_user(pdf['uploaded_by'])
    uploader_name = uploader['full_name'] if uploader else "Unknown"
    
    text = (
        f"📄 **{pdf['file_name']}**\n━━━━━━━━━━━━━━━━━━━━━\n"
        f"📚 `{pdf['subject']}` | 🏷️ `{pdf['tag'] or 'None'}`\n"
        f"👤 `{uploader_name}`\n"
        f"📅 `{pdf['upload_date'][:19]}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"❤️ `{pdf['like_count']}` | 📥 `{pdf['download_count']}`\n"
        f"🆔 `{pdf_id}`"
    )
    
    try:
        bot.edit_message_text(
            text, user_id, message_id,
            parse_mode='Markdown',
            reply_markup=pdf_action_buttons(pdf_id, user_id)
        )
    except:
        pass

def show_results(user_id, message_id, subject, tag, page):
    """Display search results"""
    limit = 5
    offset = page * limit
    total = count_pdfs_by_filters(subject=subject, tag=tag)
    total_pages = (total + limit - 1) // limit
    pdfs = get_pdfs_by_filters(subject=subject, tag=tag, limit=limit, offset=offset)
    
    text = f"🔍 **Results**\n━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"📚 `{subject}` | 🏷️ `{tag or 'All'}`\n"
    text += f"📄 {total} | Page {page+1}/{total_pages}\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for pdf in pdfs:
        emoji = get_pdf_emoji(pdf['tag'])
        text += f"{emoji} **{pdf['file_name'][:40]}**\n"
        text += f"   📚 `{pdf['subject']}` | 🏷️ `{pdf['tag'] or 'None'}`\n"
        text += f"   ❤️ `{pdf['like_count']}` | 📥 `{pdf['download_count']}`\n"
        text += f"   🆔 `{pdf['id']}`\n\n"
    
    markup = InlineKeyboardMarkup()
    for pdf in pdfs[:5]:
        markup.add(InlineKeyboardButton(f"📄 {pdf['file_name'][:30]}", callback_data=f"view_{pdf['id']}"))
    
    pagination = pagination_buttons(page, total_pages, subject, tag)
    for row in pagination.keyboard:
        markup.row(*row)
    
    bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)

# ==================== START ====================

if __name__ == "__main__":
    print("=" * 50)
    print("📚 PDF Manager Bot Starting...")
    print("=" * 50)
    print(f"📁 Database: {DB_PATH}")
    
    if os.path.exists(DB_PATH):
        print("✅ Database found")
    
    bot_info = bot.get_me()
    print(f"🤖 Bot: @{bot_info.username}")
    print("=" * 50)
    
    try:
        webhook = bot.get_webhook_info()
        if webhook.url:
            bot.delete_webhook()
            print("✅ Webhook removed")
    except:
        pass
    
    print("🚀 Bot started! Press Ctrl+C to stop")
    print("=" * 50)
    
    bot.infinity_polling(timeout=10)