# telegram_pdf_bot/admin.py
# Admin functions for managing membership requirements and monitoring

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS, DEBUG
import database as db
import texts
import utils
from datetime import datetime

def is_admin(user_id):
    """Check if user is admin"""
    return user_id in ADMIN_IDS or (db.get_user(user_id) and db.get_user(user_id)['is_admin'])

def show_admin_panel(bot, user_id):
    """Show the main admin panel with membership management options"""
    if not is_admin(user_id):
        bot.send_message(user_id, texts.ERROR_PERMISSION)
        return
    
    if DEBUG:
        print(f"👑 Admin panel opened by {user_id}")
    
    # Get stats for display
    stats = db.get_stats()
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"📊 Stats ({stats['total_users']} users)", callback_data="admin_stats"),
        InlineKeyboardButton(f"👥 Users", callback_data="admin_users")
    )
    markup.add(
        InlineKeyboardButton(f"⏳ Pending PDFs ({stats['pending_pdfs']})", callback_data="admin_pending"),
        InlineKeyboardButton(f"🚨 Reports ({stats['total_reports']})", callback_data="admin_reports")
    )
    markup.add(
        InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
        InlineKeyboardButton("🔧 SQL Console", callback_data="admin_sql")
    )
    markup.add(
        InlineKeyboardButton("🔗 Membership Requirements", callback_data="admin_membership"),
        InlineKeyboardButton("📊 Membership Stats", callback_data="admin_membership_stats")
    )
    markup.add(
        InlineKeyboardButton("🔙 Back to Main", callback_data="cancel")
    )
    
    bot.send_message(
        user_id, 
        texts.ADMIN_PANEL, 
        parse_mode='Markdown', 
        reply_markup=markup
    )

# ==================== User Management Functions ====================

def show_user_details(bot, user_id, target_user_id, message_id=None):
    """Show detailed user information with management options"""
    user = db.get_user(target_user_id)
    if not user:
        bot.edit_message_text("❌ User not found.", user_id, message_id)
        return
    
    # Get user stats
    uploads = db.get_user_upload_count(target_user_id)
    downloads = db.get_user_download_count(target_user_id)
    referrals = db.get_user_referral_stats(target_user_id)
    
    # Format dates
    join_date = utils.format_date(user['join_date'])
    last_active = utils.format_date(user['last_active']) if user['last_active'] else "Never"
    
    text = f"👤 *User Details*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"📛 *Name:* `{user['full_name']}`\n"
    text += f"🆔 *ID:* `{target_user_id}`\n"
    text += f"📞 *Phone:* `{user['phone'] or 'Not set'}`\n"
    text += f"🎓 *Class:* `{user['class'] or 'Not set'}`\n"
    text += f"📍 *Region:* `{user['region'] or 'Not set'}`\n"
    text += f"🏫 *School:* `{user['school'] or 'Not set'}`\n"
    text += f"📅 *Joined:* `{join_date}`\n"
    text += f"🕐 *Last Active:* `{last_active}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"📊 *Stats*\n"
    text += f"📤 *Uploads:* `{uploads}`\n"
    text += f"📥 *Downloads:* `{downloads}`\n"
    text += f"👥 *Referrals:* `{referrals['conversions']}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"👑 *Admin:* `{'Yes' if user['is_admin'] else 'No'}`\n"
    text += f"🚫 *Banned:* `{'Yes' if user['is_banned'] else 'No'}`\n"
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    # Management buttons
    if user['is_banned']:
        markup.add(InlineKeyboardButton("✅ Unban User", callback_data=f"admin_unban_{target_user_id}"))
    else:
        markup.add(InlineKeyboardButton("🚫 Ban User", callback_data=f"admin_ban_{target_user_id}"))
    
    if user['is_admin']:
        markup.add(InlineKeyboardButton("👑 Remove Admin", callback_data=f"admin_remove_admin_{target_user_id}"))
    else:
        markup.add(InlineKeyboardButton("👑 Make Admin", callback_data=f"admin_make_admin_{target_user_id}"))
    
    markup.add(
        InlineKeyboardButton("📄 View User's Uploads", callback_data=f"admin_user_uploads_{target_user_id}"),
        InlineKeyboardButton("📥 View User's Downloads", callback_data=f"admin_user_downloads_{target_user_id}")
    )
    markup.add(InlineKeyboardButton("🔙 Back to Users", callback_data="admin_users"))
    
    if message_id:
        bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)

def show_user_uploads(bot, user_id, target_user_id, page=0, message_id=None):
    """Show user's uploaded PDFs"""
    limit = 5
    offset = page * limit
    
    pdfs = db.get_pdfs_by_filters(uploaded_by=target_user_id, approved_only=False, limit=limit, offset=offset)
    total = db.count_pdfs_by_filters(uploaded_by=target_user_id, approved_only=False)
    total_pages = (total + limit - 1) // limit
    
    if not pdfs:
        if message_id:
            bot.edit_message_text("📭 No uploads found.", user_id, message_id)
        else:
            bot.send_message(user_id, "📭 No uploads found.")
        return
    
    text = f"📄 *User Uploads*\n"
    text += f"👤 User ID: `{target_user_id}`\n"
    text += f"📄 Total: `{total}` PDFs\n"
    text += f"📄 Page: `{page + 1}/{total_pages}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for pdf in pdfs:
        status = "✅" if pdf['is_approved'] else "⏳"
        text += f"{status} *{pdf['file_name'][:40]}*\n"
        text += f"   📚 `{pdf['subject']}` | 🏷️ `{pdf['tag']}`\n"
        text += f"   📥 `{pdf['download_count']}` | ❤️ `{pdf['like_count']}`\n"
        text += f"   🆔 `{pdf['id']}`\n\n"
    
    markup = InlineKeyboardMarkup(row_width=3)
    
    # Navigation
    if page > 0:
        markup.add(InlineKeyboardButton("◀️ Prev", callback_data=f"admin_user_uploads_page_{target_user_id}_{page-1}"))
    if page < total_pages - 1:
        markup.add(InlineKeyboardButton("Next ▶️", callback_data=f"admin_user_uploads_page_{target_user_id}_{page+1}"))
    
    markup.add(InlineKeyboardButton("🔙 Back to User", callback_data=f"admin_user_details_{target_user_id}"))
    
    if message_id:
        bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)

def show_user_downloads(bot, user_id, target_user_id, page=0, message_id=None):
    """Show user's downloaded PDFs"""
    from database import get_db
    
    limit = 5
    offset = page * limit
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, d.download_date 
            FROM downloads d
            JOIN pdfs p ON d.pdf_id = p.id
            WHERE d.user_id = ?
            ORDER BY d.download_date DESC
            LIMIT ? OFFSET ?
        ''', (target_user_id, limit, offset))
        downloads = cursor.fetchall()
        
        cursor.execute('SELECT COUNT(*) FROM downloads WHERE user_id = ?', (target_user_id,))
        total = cursor.fetchone()[0]
    
    total_pages = (total + limit - 1) // limit
    
    if not downloads:
        if message_id:
            bot.edit_message_text("📭 No downloads found.", user_id, message_id)
        else:
            bot.send_message(user_id, "📭 No downloads found.")
        return
    
    text = f"📥 *User Downloads*\n"
    text += f"👤 User ID: `{target_user_id}`\n"
    text += f"📥 Total: `{total}` downloads\n"
    text += f"📄 Page: `{page + 1}/{total_pages}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for download in downloads:
        text += f"📄 *{download['file_name'][:40]}*\n"
        text += f"   📚 `{download['subject']}` | 🏷️ `{download['tag']}`\n"
        text += f"   📅 `{utils.format_date(download['download_date'])}`\n"
        text += f"   🆔 `{download['id']}`\n\n"
    
    markup = InlineKeyboardMarkup(row_width=3)
    
    # Navigation
    if page > 0:
        markup.add(InlineKeyboardButton("◀️ Prev", callback_data=f"admin_user_downloads_page_{target_user_id}_{page-1}"))
    if page < total_pages - 1:
        markup.add(InlineKeyboardButton("Next ▶️", callback_data=f"admin_user_downloads_page_{target_user_id}_{page+1}"))
    
    markup.add(InlineKeyboardButton("🔙 Back to User", callback_data=f"admin_user_details_{target_user_id}"))
    
    if message_id:
        bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)

# ==================== Membership Management ====================

def show_membership_management(bot, user_id, message_id=None):
    """Show membership requirements management menu"""
    requirements = db.get_requirements(active_only=False)
    
    text = "🔗 *Membership Requirements Management*\n\n"
    text += "Add channels/groups that users must join before using the bot.\n\n"
    
    active_count = sum(1 for req in requirements if req['is_active'])
    inactive_count = len(requirements) - active_count
    
    text += f"📊 *Summary:*\n"
    text += f"├ ✅ Active: `{active_count}`\n"
    text += f"└ ❌ Inactive: `{inactive_count}`\n\n"
    
    if requirements:
        text += "*Current Requirements:*\n"
        for req in requirements[:5]:  # Show first 5
            status = "✅" if req['is_active'] else "❌"
            text += f"\n{status} *{req['name']}* ({req['type'].upper()})\n"
            text += f"   🔗 `{req['link'][:30]}...`\n"
        
        if len(requirements) > 5:
            text += f"\n... and {len(requirements) - 5} more. Use *List All* to see full list."
    else:
        text += "*No requirements set yet.*\n"
    
    text += "\n*Actions:*"
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ Add Telegram Channel", callback_data="membership_add_telegram"),
        InlineKeyboardButton("➕ Add WhatsApp Group", callback_data="membership_add_whatsapp")
    )
    markup.add(
        InlineKeyboardButton("📋 List All", callback_data="membership_list"),
        InlineKeyboardButton("🔄 Refresh", callback_data="admin_membership")
    )
    markup.add(
        InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_back")
    )
    
    if message_id:
        bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)

def show_membership_list(bot, user_id, message_id=None, page=0):
    """Show paginated list of membership requirements"""
    requirements = db.get_requirements(active_only=False)
    
    if not requirements:
        if message_id:
            bot.edit_message_text("📭 No requirements found.", user_id, message_id)
        else:
            bot.send_message(user_id, "📭 No requirements found.")
        return
    
    items_per_page = 5
    total_pages = (len(requirements) + items_per_page - 1) // items_per_page
    start = page * items_per_page
    end = start + items_per_page
    page_items = requirements[start:end]
    
    text = f"🔗 *Membership Requirements*\n"
    text += f"📄 Page `{page + 1}/{total_pages}` | Total: `{len(requirements)}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for req in page_items:
        status = "✅ ACTIVE" if req['is_active'] else "❌ INACTIVE"
        type_icon = "📢" if req['type'] == 'telegram' else "💬"
        
        text += f"{type_icon} *ID: {req['id']} - {req['name']}*\n"
        text += f"├ Type: `{req['type'].upper()}`\n"
        text += f"├ Link: `{req['link'][:40]}{'...' if len(req['link']) > 40 else ''}`\n"
        text += f"├ Status: {status}\n"
        if req['description']:
            desc = req['description'][:50] + ('...' if len(req['description']) > 50 else '')
            text += f"└ Description: {desc}\n"
        text += "\n"
    
    markup = InlineKeyboardMarkup(row_width=3)
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"membership_list_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"membership_list_page_{page+1}"))
    if nav_buttons:
        markup.row(*nav_buttons)
    
    # Action buttons for each requirement - 2 per row for better UI
    for req in page_items:
        type_icon = "📢" if req['type'] == 'telegram' else "💬"
        action_text = f"{type_icon} {req['name'][:20]}"
        markup.add(InlineKeyboardButton(action_text, callback_data=f"membership_edit_{req['id']}"))
    
    markup.add(InlineKeyboardButton("➕ Add New", callback_data="membership_add_menu"))
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="membership_back"))
    
    if message_id:
        bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)

def show_membership_edit(bot, user_id, req_id, message_id=None):
    """Show edit options for a specific membership requirement"""
    req = db.get_requirement(req_id)
    if not req:
        bot.edit_message_text("❌ Requirement not found.", user_id, message_id)
        return
    
    status = "✅ Active" if req['is_active'] else "❌ Inactive"
    type_icon = "📢" if req['type'] == 'telegram' else "💬"
    
    text = f"{type_icon} *Edit Requirement: {req['name']}*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"🆔 *ID:* `{req['id']}`\n"
    text += f"📌 *Type:* `{req['type'].upper()}`\n"
    text += f"🔗 *Link:* `{req['link']}`\n"
    text += f"📊 *Status:* {status}\n"
    if req['description']:
        text += f"📝 *Description:* {req['description']}\n"
    text += f"📅 *Created:* `{req['created_at'][:10] if req['created_at'] else 'Unknown'}`\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Get membership stats for this requirement
    users = db.get_all_users()
    members = 0
    for user in users:
        if req['type'] == 'telegram':
            if utils.is_telegram_member(bot, user['user_id'], req['link']):
                members += 1
        else:  # whatsapp
            if db.is_whatsapp_verified(user['user_id'], req_id):
                members += 1
    
    if users:
        percentage = int(members / len(users) * 100)
    else:
        percentage = 0
    
    text += f"📊 *Stats:*\n"
    text += f"├ 👥 Total Users: `{len(users)}`\n"
    text += f"└ ✅ Members: `{members}` ({percentage}%)\n"
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    # Toggle active/inactive
    if req['is_active']:
        markup.add(InlineKeyboardButton("❌ Deactivate", callback_data=f"membership_toggle_{req_id}_0"))
    else:
        markup.add(InlineKeyboardButton("✅ Activate", callback_data=f"membership_toggle_{req_id}_1"))
    
    # Edit buttons
    markup.add(
        InlineKeyboardButton("✏️ Edit Name", callback_data=f"membership_edit_name_{req_id}"),
        InlineKeyboardButton("🔗 Edit Link", callback_data=f"membership_edit_link_{req_id}")
    )
    markup.add(
        InlineKeyboardButton("📝 Edit Description", callback_data=f"membership_edit_desc_{req_id}"),
        InlineKeyboardButton("🗑️ Delete", callback_data=f"membership_delete_{req_id}")
    )
    markup.add(InlineKeyboardButton("🔙 Back to List", callback_data="membership_list"))
    
    if message_id:
        bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)

def show_membership_stats(bot, user_id, message_id=None):
    """Show membership statistics for all requirements"""
    requirements = db.get_requirements(active_only=True)
    users = db.get_all_users()
    
    text = "📊 *Membership Statistics*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"👥 *Total Users:* `{len(users)}`\n\n"
    
    if requirements:
        text += "*Active Requirements:*\n"
        for req in requirements:
            members = 0
            for user in users:
                if req['type'] == 'telegram':
                    if utils.is_telegram_member(bot, user['user_id'], req['link']):
                        members += 1
                else:
                    if db.is_whatsapp_verified(user['user_id'], req['id']):
                        members += 1
            
            percentage = int(members / len(users) * 100) if users else 0
            type_icon = "📢" if req['type'] == 'telegram' else "💬"
            
            text += f"\n{type_icon} *{req['name']}*\n"
            text += f"├ Type: `{req['type'].upper()}`\n"
            text += f"├ Members: `{members}/{len(users)}` (`{percentage}%`)\n"
            text += f"└ Link: `{req['link'][:40]}{'...' if len(req['link']) > 40 else ''}`\n"
    else:
        text += "*No active requirements.*\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━\n"
    text += "*Note:* Users must join all active requirements to use the bot."
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🔄 Refresh", callback_data="admin_membership_stats"),
        InlineKeyboardButton("🔙 Back", callback_data="admin_back")
    )
    
    if message_id:
        bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)

# ==================== Add Requirement Flow ====================

def start_add_requirement(bot, user_id, req_type, message_id=None):
    """Start the process of adding a new requirement"""
    type_icon = "📢" if req_type == 'telegram' else "💬"
    
    text = f"{type_icon} *Add {req_type.upper()} Requirement*\n\n"
    text += f"Please send the *name* for this {req_type} requirement.\n\n"
    text += f"📌 *Example:* `Main Channel` or `Support Group`\n\n"
    text += f"Type *Cancel* to cancel."
    
    if message_id:
        bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown')
    else:
        bot.send_message(user_id, text, parse_mode='Markdown')
    
    # Store in user state
    db.set_user_state(user_id, 'add_requirement', {'type': req_type, 'step': 'name'})

def process_add_requirement(bot, user_id, message):
    """Process the add requirement flow"""
    current_state, data = db.get_user_state(user_id)
    
    if current_state != 'add_requirement':
        return False
    
    step = data.get('step')
    
    if step == 'name':
        name = message.text.strip()
        
        if name.lower() == texts.BUTTON_CANCEL.lower():
            db.clear_user_state(user_id)
            bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard())
            return True
        
        if len(name) < 3:
            bot.send_message(user_id, "❌ Name must be at least 3 characters. Please try again.")
            return True
        
        data['name'] = name
        data['step'] = 'link'
        db.set_user_state(user_id, 'add_requirement', data)
        
        req_type = data['type']
        type_icon = "📢" if req_type == 'telegram' else "💬"
        
        if req_type == 'telegram':
            text = f"{type_icon} *Add {req_type.upper()} Requirement*\n\n"
            text += f"📌 *Name:* `{name}`\n\n"
            text += f"Now send the *channel/group link*.\n\n"
            text += f"📌 *Example:* `https://t.me/username` or `@username`\n\n"
            text += f"Type *Cancel* to cancel."
        else:
            text = f"{type_icon} *Add {req_type.upper()} Requirement*\n\n"
            text += f"📌 *Name:* `{name}`\n\n"
            text += f"Now send the *WhatsApp group invite link*.\n\n"
            text += f"📌 *Example:* `https://chat.whatsapp.com/xxxxx`\n\n"
            text += f"Type *Cancel* to cancel."
        
        bot.send_message(user_id, text, parse_mode='Markdown')
        return True
    
    elif step == 'link':
        link = message.text.strip()
        
        if link.lower() == texts.BUTTON_CANCEL.lower():
            db.clear_user_state(user_id)
            bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard())
            return True
        
        # Basic validation
        if data['type'] == 'telegram':
            if not ('t.me/' in link or link.startswith('@')):
                bot.send_message(user_id, "❌ Invalid Telegram link. Please use format: `https://t.me/username` or `@username`", parse_mode='Markdown')
                return True
        else:
            if not 'chat.whatsapp.com' in link:
                bot.send_message(user_id, "❌ Invalid WhatsApp link. Please use format: `https://chat.whatsapp.com/xxxxx`", parse_mode='Markdown')
                return True
        
        data['link'] = link
        data['step'] = 'description'
        db.set_user_state(user_id, 'add_requirement', data)
        
        text = f"📝 *Add {data['type'].upper()} Requirement*\n\n"
        text += f"📌 *Name:* `{data['name']}`\n"
        text += f"🔗 *Link:* `{link}`\n\n"
        text += f"Now send a *description* (optional).\n\n"
        text += f"Type `skip` to skip or *Cancel* to cancel."
        
        bot.send_message(user_id, text, parse_mode='Markdown')
        return True
    
    elif step == 'description':
        description = message.text.strip()
        
        if description.lower() == texts.BUTTON_CANCEL.lower():
            db.clear_user_state(user_id)
            bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard())
            return True
        
        if description.lower() == 'skip':
            description = None
        
        # Save to database
        req_id = db.add_requirement(
            name=data['name'],
            req_type=data['type'],
            link=data['link'],
            description=description,
            created_by=user_id
        )
        
        db.clear_user_state(user_id)
        
        type_icon = "📢" if data['type'] == 'telegram' else "💬"
        
        text = f"✅ *Requirement Added Successfully!*\n\n"
        text += f"{type_icon} *Name:* {data['name']}\n"
        text += f"📌 *Type:* {data['type'].upper()}\n"
        text += f"🔗 *Link:* `{data['link']}`\n"
        text += f"🆔 *ID:* `{req_id}`\n\n"
        text += f"Users must now join this to use the bot."
        
        bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=utils.create_main_menu_keyboard())
        
        # Notify all admins
        for admin_id in ADMIN_IDS:
            if admin_id != user_id:
                try:
                    bot.send_message(
                        admin_id,
                        f"🔔 *New Requirement Added*\n\n"
                        f"{type_icon} *Name:* {data['name']}\n"
                        f"📌 *Type:* {data['type'].upper()}\n"
                        f"🔗 *Link:* `{data['link']}`\n"
                        f"👤 *Added by:* `{user_id}`",
                        parse_mode='Markdown'
                    )
                except:
                    pass
        
        return True
    
    return False

# ==================== Edit Requirement Flow ====================

def edit_requirement_field(bot, user_id, req_id, field, message_id=None):
    """Start editing a specific field of a requirement"""
    req = db.get_requirement(req_id)
    if not req:
        bot.send_message(user_id, "❌ Requirement not found.")
        return
    
    field_names = {
        'name': 'Name',
        'link': 'Link',
        'desc': 'Description'
    }
    
    current_value = req[field] if field != 'desc' else req['description']
    if not current_value:
        current_value = '(empty)'
    
    text = f"✏️ *Edit {field_names[field]}*\n\n"
    text += f"Current value: `{current_value}`\n\n"
    text += f"Please send the new {field_names[field].lower()}.\n\n"
    text += f"Type *Cancel* to cancel."
    
    if message_id:
        bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown')
    else:
        bot.send_message(user_id, text, parse_mode='Markdown')
    
    # Store in user state
    db.set_user_state(user_id, 'edit_requirement', {
        'req_id': req_id,
        'field': field,
        'step': 'value'
    })

def process_edit_requirement(bot, user_id, message):
    """Process the edit requirement flow"""
    current_state, data = db.get_user_state(user_id)
    
    if current_state != 'edit_requirement':
        return False
    
    new_value = message.text.strip()
    
    if new_value.lower() == texts.BUTTON_CANCEL.lower():
        db.clear_user_state(user_id)
        bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard())
        return True
    
    req_id = data['req_id']
    field = data['field']
    
    # Update the field
    with db.get_db() as conn:
        cursor = conn.cursor()
        if field == 'name':
            cursor.execute('UPDATE requirements SET name = ? WHERE id = ?', (new_value, req_id))
        elif field == 'link':
            cursor.execute('UPDATE requirements SET link = ? WHERE id = ?', (new_value, req_id))
        elif field == 'desc':
            cursor.execute('UPDATE requirements SET description = ? WHERE id = ?', (new_value, req_id))
    
    db.clear_user_state(user_id)
    
    field_display = {'name': 'Name', 'link': 'Link', 'desc': 'Description'}
    
    bot.send_message(
        user_id,
        f"✅ *Requirement updated successfully!*\n\n"
        f"📝 *Field:* {field_display[field]}\n"
        f"🆕 *New value:* `{new_value}`",
        parse_mode='Markdown',
        reply_markup=utils.create_main_menu_keyboard()
    )
    
    return True

# ==================== Membership Verification ====================

def check_user_membership(bot, user_id):
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

def send_membership_required_message(bot, user_id, requirement):
    """Send message asking user to join requirement"""
    type_icon = "📢" if requirement['type'] == 'telegram' else "💬"
    
    text = f"🔒 *Membership Required*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"To use this bot, you must join:\n\n"
    text += f"{type_icon} *{requirement['name']}*\n"
    text += f"📌 *Type:* `{requirement['type'].upper()}`\n"
    
    if requirement['description']:
        text += f"📝 *Description:* {requirement['description']}\n\n"
    
    text += f"🔗 *Link:* `{requirement['link']}`\n\n"
    
    if requirement['type'] == 'telegram':
        text += "After joining, click the button below to verify."
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ I've Joined", callback_data=f"verify_telegram_{requirement['id']}"),
            InlineKeyboardButton("📢 Join Channel", url=requirement['link'])
        )
    else:  # whatsapp
        text += "After joining the WhatsApp group, click the button below to verify."
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("📱 Join WhatsApp Group", url=requirement['link']),
            InlineKeyboardButton("✅ Verify", callback_data=f"verify_whatsapp_{requirement['id']}")
        )
    
    bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)

def verify_telegram_membership(bot, user_id, requirement_id):
    """Verify if user joined Telegram channel/group"""
    req = db.get_requirement(requirement_id)
    if not req:
        return False
    
    if utils.is_telegram_member(bot, user_id, req['link']):
        # Record membership
        db.record_membership(user_id, requirement_id, True)
        return True
    
    return False

def start_whatsapp_verification(bot, user_id, requirement_id):
    """Start WhatsApp verification process"""
    import random
    import string
    
    # Generate verification code
    code = ''.join(random.choices(string.digits, k=6))
    
    # Store in database
    db.add_whatsapp_verification(user_id, requirement_id, code)
    
    req = db.get_requirement(requirement_id)
    
    text = f"🔐 *WhatsApp Verification*\n\n"
    text += f"To verify you've joined *{req['name']}*, please send this code in the WhatsApp group:\n\n"
    text += f"`VERIFY {code}`\n\n"
    text += f"After sending, click the button below to confirm."
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ I've Sent the Code", callback_data=f"confirm_whatsapp_{requirement_id}_{code}"),
        InlineKeyboardButton("📱 Join Group", url=req['link'])
    )
    markup.add(InlineKeyboardButton("🔙 Cancel", callback_data="cancel"))
    
    bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)

def confirm_whatsapp_verification(bot, user_id, requirement_id, code):
    """Confirm WhatsApp verification"""
    verification = db.get_whatsapp_verification(user_id, requirement_id)
    
    if verification and verification['verification_code'] == code:
        db.record_membership(user_id, requirement_id, True)
        bot.send_message(
            user_id, 
            texts.WHATSAPP_VERIFICATION_SUCCESS, 
            parse_mode='Markdown',
            reply_markup=utils.create_main_menu_keyboard()
        )
        return True
    else:
        bot.send_message(
            user_id, 
            texts.WHATSAPP_VERIFICATION_FAILED, 
            parse_mode='Markdown'
        )
        return False

# ==================== Admin Callback Handler ====================

def handle_admin_callback(bot, call):
    """Handle admin-related callbacks"""
    user_id = call.from_user.id
    
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, texts.ERROR_PERMISSION)
        return
    
    data = call.data
    
    # Stats
    if data == "admin_stats":
        stats = db.get_stats()
        text = texts.ADMIN_STATS.format(
            total_users=stats['total_users'],
            total_pdfs=stats['total_pdfs'],
            total_downloads=stats['total_downloads'],
            pending_pdfs=stats['pending_pdfs'],
            total_reports=stats['total_reports']
        )
        bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
        return
    
    # Membership management
    if data == "admin_membership":
        show_membership_management(bot, user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if data == "admin_membership_stats":
        show_membership_stats(bot, user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if data == "membership_back":
        show_membership_management(bot, user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if data == "membership_list":
        show_membership_list(bot, user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("membership_list_page_"):
        page = int(data.split("_")[-1])
        show_membership_list(bot, user_id, call.message.message_id, page)
        bot.answer_callback_query(call.id)
        return
    
    if data == "membership_add_telegram":
        start_add_requirement(bot, user_id, 'telegram', call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if data == "membership_add_whatsapp":
        start_add_requirement(bot, user_id, 'whatsapp', call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if data == "membership_add_menu":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("📢 Telegram Channel", callback_data="membership_add_telegram"),
            InlineKeyboardButton("💬 WhatsApp Group", callback_data="membership_add_whatsapp")
        )
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="membership_back"))
        bot.edit_message_text(
            "➕ *Add New Requirement*\n\nSelect type:",
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("membership_edit_"):
        req_id = int(data.split("_")[2])
        show_membership_edit(bot, user_id, req_id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("membership_toggle_"):
        parts = data.split("_")
        req_id = int(parts[2])
        is_active = bool(int(parts[3]))
        db.toggle_requirement(req_id, is_active)
        
        status = "activated" if is_active else "deactivated"
        bot.answer_callback_query(call.id, f"✅ Requirement {status}!")
        show_membership_edit(bot, user_id, req_id, call.message.message_id)
        return
    
    if data.startswith("membership_edit_name_"):
        req_id = int(data.split("_")[3])
        edit_requirement_field(bot, user_id, req_id, 'name', call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("membership_edit_link_"):
        req_id = int(data.split("_")[3])
        edit_requirement_field(bot, user_id, req_id, 'link', call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("membership_edit_desc_"):
        req_id = int(data.split("_")[3])
        edit_requirement_field(bot, user_id, req_id, 'desc', call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("membership_delete_"):
        req_id = int(data.split("_")[2])
        req = db.get_requirement(req_id)
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Yes, Delete", callback_data=f"membership_confirm_delete_{req_id}"),
            InlineKeyboardButton("❌ No, Cancel", callback_data=f"membership_edit_{req_id}")
        )
        
        type_icon = "📢" if req['type'] == 'telegram' else "💬"
        
        bot.edit_message_text(
            f"⚠️ *Delete Requirement?*\n\n"
            f"Are you sure you want to delete:\n"
            f"{type_icon} *{req['name']}* ({req['type'].upper()})\n\n"
            f"This action cannot be undone.",
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("membership_confirm_delete_"):
        req_id = int(data.split("_")[3])
        db.delete_requirement(req_id)
        bot.answer_callback_query(call.id, "🗑️ Requirement deleted!")
        show_membership_list(bot, user_id, call.message.message_id)
        return
    
    # Membership verification
    if data.startswith("verify_telegram_"):
        req_id = int(data.split("_")[2])
        if verify_telegram_membership(bot, user_id, req_id):
            bot.answer_callback_query(call.id, "✅ Verified! You can now use the bot.")
            # Check all requirements
            all_met, missing = check_user_membership(bot, user_id)
            if all_met:
                from handlers import show_main_menu
                show_main_menu(user_id)
        else:
            bot.answer_callback_query(call.id, "❌ Not a member yet. Please join first.", show_alert=True)
        return
    
    if data.startswith("verify_whatsapp_"):
        req_id = int(data.split("_")[2])
        start_whatsapp_verification(bot, user_id, req_id)
        bot.delete_message(user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("confirm_whatsapp_"):
        parts = data.split("_")
        req_id = int(parts[2])
        code = parts[3]
        if confirm_whatsapp_verification(bot, user_id, req_id, code):
            bot.answer_callback_query(call.id, "✅ Verified!")
            # Check all requirements
            all_met, missing = check_user_membership(bot, user_id)
            if all_met:
                from handlers import show_main_menu
                show_main_menu(user_id)
        else:
            bot.answer_callback_query(call.id, "❌ Verification failed. Please try again.")
        return
    
    # Back to admin
    if data == "admin_back":
        show_admin_panel(bot, user_id)
        bot.delete_message(user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    # Broadcast
    if data == "admin_broadcast":
        db.set_user_state(user_id, 'admin_broadcast', {})
        bot.edit_message_text(
            texts.ADMIN_BROADCAST_PROMPT,
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=utils.create_cancel_keyboard()
        )
        bot.answer_callback_query(call.id)
        return
    
    # SQL Console
    if data == "admin_sql":
        db.set_user_state(user_id, 'admin_sql', {})
        bot.edit_message_text(
            texts.ADMIN_SQL_PROMPT,
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=utils.create_cancel_keyboard()
        )
        bot.answer_callback_query(call.id)
        return
    
    # Users list with clickable buttons
    if data == "admin_users":
        users = db.get_all_users(limit=30)
        total_users = db.count_users()
        
        text = "👥 *User List*\n"
        text += "━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📊 Total: `{total_users}` users\n"
        text += f"📄 Showing first `{len(users)}`\n\n"
        
        markup = InlineKeyboardMarkup(row_width=2)
        
        for user in users:
            status = "🚫" if user['is_banned'] else "✅"
            role = "👑" if user['is_admin'] else "👤"
            name = user['full_name'][:25] if user['full_name'] else f"User_{user['user_id']}"
            markup.add(InlineKeyboardButton(
                f"{status} {role} {name}",
                callback_data=f"admin_user_details_{user['user_id']}"
            ))
        
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back"))
        
        bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    
    # User details
    if data.startswith("admin_user_details_"):
        target_user_id = int(data.split("_")[3])
        show_user_details(bot, user_id, target_user_id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    # User uploads
    if data.startswith("admin_user_uploads_"):
        parts = data.split("_")
        if len(parts) == 4:
            target_user_id = int(parts[3])
            show_user_uploads(bot, user_id, target_user_id, 0, call.message.message_id)
        elif len(parts) == 6 and parts[4] == "page":
            target_user_id = int(parts[4])
            page = int(parts[5])
            show_user_uploads(bot, user_id, target_user_id, page, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    # User downloads
    if data.startswith("admin_user_downloads_"):
        parts = data.split("_")
        if len(parts) == 4:
            target_user_id = int(parts[3])
            show_user_downloads(bot, user_id, target_user_id, 0, call.message.message_id)
        elif len(parts) == 6 and parts[4] == "page":
            target_user_id = int(parts[4])
            page = int(parts[5])
            show_user_downloads(bot, user_id, target_user_id, page, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    # Ban user
    if data.startswith("admin_ban_"):
        target_user_id = int(data.split("_")[2])
        db.ban_user(target_user_id)
        bot.answer_callback_query(call.id, f"🚫 User {target_user_id} banned!")
        show_user_details(bot, user_id, target_user_id, call.message.message_id)
        return
    
    # Unban user
    if data.startswith("admin_unban_"):
        target_user_id = int(data.split("_")[2])
        db.unban_user(target_user_id)
        bot.answer_callback_query(call.id, f"✅ User {target_user_id} unbanned!")
        show_user_details(bot, user_id, target_user_id, call.message.message_id)
        return
    
    # Make admin
    if data.startswith("admin_make_admin_"):
        target_user_id = int(data.split("_")[3])
        db.set_admin(target_user_id, True)
        bot.answer_callback_query(call.id, f"👑 User {target_user_id} is now admin!")
        show_user_details(bot, user_id, target_user_id, call.message.message_id)
        return
    
    # Remove admin
    if data.startswith("admin_remove_admin_"):
        target_user_id = int(data.split("_")[3])
        db.set_admin(target_user_id, False)
        bot.answer_callback_query(call.id, f"👑 Admin rights removed from {target_user_id}!")
        show_user_details(bot, user_id, target_user_id, call.message.message_id)
        return
    
    # Pending PDFs
    if data == "admin_pending":
        pending = db.get_unapproved_pdfs()
        if not pending:
            bot.edit_message_text("📭 No pending PDFs.", user_id, call.message.message_id)
            bot.answer_callback_query(call.id)
            return
        
        text = texts.ADMIN_PDF_PENDING_LIST
        for idx, pdf in enumerate(pending[:20], start=1):
            uploader = db.get_user(pdf['uploaded_by'])
            uploader_name = uploader['full_name'] if uploader else "Unknown"
            text += texts.ADMIN_PDF_PENDING_ITEM.format(
                number=idx,
                name=pdf['file_name'],
                subject=pdf['subject'],
                tag=pdf['tag'],
                uploader=uploader_name,
                id=pdf['id']
            )
        
        markup = InlineKeyboardMarkup(row_width=2)
        for pdf in pending[:10]:
            markup.add(InlineKeyboardButton(f"📄 {pdf['file_name'][:25]}", callback_data=f"view_{pdf['id']}"))
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back"))
        
        bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    
    # Reports
    if data == "admin_reports":
        reports = db.get_pending_reports()
        if not reports:
            bot.edit_message_text("📭 No pending reports.", user_id, call.message.message_id)
            bot.answer_callback_query(call.id)
            return
        
        text = texts.ADMIN_REPORT_LIST
        for idx, report in enumerate(reports[:20], start=1):
            text += texts.ADMIN_REPORT_ITEM.format(
                number=idx,
                pdf_name=report['pdf_name'],
                pdf_id=report['pdf_id'],
                reporter=report['reporter_name'],
                reason=report['report_text'][:50]
            )
        
        markup = InlineKeyboardMarkup(row_width=2)
        for report in reports[:10]:
            markup.add(InlineKeyboardButton(f"📄 View PDF {report['pdf_id']}", callback_data=f"view_{report['pdf_id']}"))
            markup.add(InlineKeyboardButton(f"✅ Resolve", callback_data=f"resolve_report_{report['id']}"))
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back"))
        
        bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    
    # Resolve report
    if data.startswith("resolve_report_"):
        report_id = int(data.split("_")[2])
        db.resolve_report(report_id)
        bot.answer_callback_query(call.id, "✅ Report resolved!")
        # Refresh reports view
        handle_admin_callback(bot, call)
        return