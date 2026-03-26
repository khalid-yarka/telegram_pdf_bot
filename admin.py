# telegram_pdf_bot/admin.py
# Admin functions for managing membership requirements and monitoring - Class-based structure

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from config import ADMIN_IDS, DEBUG
import database as db
import texts
import utils
from utils import get_current_time
from datetime import datetime


class Admin:
    """Admin class for Ardayda Bot - handles all admin functionality"""
    
    def __init__(self, bot, handlers=None):
        """Initialize admin with bot instance and optional handlers reference"""
        self.bot = bot
        self.handlers = handlers  # Reference to handlers instance for callbacks
        
        if DEBUG:
            print("👑 Admin module initialized")
    
    # ==================== Helper Functions ====================
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        return user_id in ADMIN_IDS or (db.get_user(user_id) and db.get_user(user_id)['is_admin'])
    
    # ==================== Admin Panel ====================
    
    def show_admin_panel(self, user_id, message_id=None):
        """Show the main admin panel with membership management options"""
        if not self.is_admin(user_id):
            self.bot.send_message(user_id, texts.ERROR_PERMISSION)
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
            InlineKeyboardButton("⚙️ Bot Settings", callback_data="admin_settings"),
            InlineKeyboardButton("🔗 Membership Requirements", callback_data="admin_membership")
        )
        markup.add(
            InlineKeyboardButton("📊 Membership Stats", callback_data="admin_membership_stats"),
            InlineKeyboardButton("📋 Membership Events", callback_data="admin_membership_events")
        )
        markup.add(
            InlineKeyboardButton("📈 Member Analytics", callback_data="admin_membership_analytics"),
            InlineKeyboardButton("🔙 Back to Main", callback_data="cancel")
        )
        
        if message_id:
            try:
                self.bot.edit_message_text(
                    texts.ADMIN_PANEL, 
                    user_id, 
                    message_id, 
                    parse_mode='Markdown', 
                    reply_markup=markup
                )
            except Exception as e:
                if DEBUG:
                    print(f"   Could not edit message: {e}")
                self.bot.send_message(
                    user_id, 
                    texts.ADMIN_PANEL, 
                    parse_mode='Markdown', 
                    reply_markup=markup
                )
        else:
            self.bot.send_message(
                user_id, 
                texts.ADMIN_PANEL, 
                parse_mode='Markdown', 
                reply_markup=markup
            )
    
    # ==================== Settings Management ====================
    
    def show_settings_panel(self, user_id, message_id=None):
        """Show bot settings management panel"""
        if not self.is_admin(user_id):
            self.bot.send_message(user_id, texts.ERROR_PERMISSION)
            return
        
        # Get current settings
        auto_approve = db.get_setting('auto_approve_pdfs', '0') == '1'
        notify_admin_upload = db.get_setting('notify_admin_on_upload', '1') == '1'
        membership_enabled = db.get_setting('membership_required', '1') == '1'
        whatsapp_enabled = db.get_setting('whatsapp_required', '1') == '1'
        whatsapp_reminders = db.get_setting('whatsapp_reminders', '3')
        broadcast_enabled = db.get_setting('broadcast_enabled', '1') == '1'
        show_admin_name = db.get_setting('show_admin_name_in_broadcast', '1') == '1'
        search_per_page = db.get_setting('search_results_per_page', '5')
        show_uploader = db.get_setting('show_uploader_in_search', '1') == '1'
        welcome_message = db.get_setting('welcome_message_enabled', '1') == '1'
        channel_leave_alert = db.get_setting('channel_leave_alert', '1') == '1'
        user_can_delete = db.get_setting('allow_user_delete_pdf', '0') == '1'
        
        text = "⚙️ **BOT SETTINGS**\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        text += "📄 **PDF SETTINGS**\n"
        text += f"├ Auto-approve PDFs: {'✅ ON' if auto_approve else '❌ OFF'}\n"
        text += f"├ Notify admin on upload: {'✅ ON' if notify_admin_upload else '❌ OFF'}\n"
        text += f"└ Allow users to delete own PDFs: {'✅ ON' if user_can_delete else '❌ OFF'}\n\n"
        
        text += "🔐 **MEMBERSHIP SETTINGS**\n"
        text += f"├ Membership required: {'✅ ON' if membership_enabled else '❌ OFF'}\n"
        text += f"├ WhatsApp required: {'✅ ON' if whatsapp_enabled else '❌ OFF'}\n"
        text += f"└ WhatsApp reminders: `{whatsapp_reminders}` times\n\n"
        
        text += "📢 **BROADCAST SETTINGS**\n"
        text += f"├ Broadcast enabled: {'✅ ON' if broadcast_enabled else '❌ OFF'}\n"
        text += f"└ Show admin name: {'✅ ON' if show_admin_name else '❌ OFF'}\n\n"
        
        text += "🔍 **SEARCH SETTINGS**\n"
        text += f"├ Results per page: `{search_per_page}`\n"
        text += f"└ Show uploader name: {'✅ ON' if show_uploader else '❌ OFF'}\n\n"
        
        text += "🔔 **NOTIFICATION SETTINGS**\n"
        text += f"├ Welcome message: {'✅ ON' if welcome_message else '❌ OFF'}\n"
        text += f"└ Channel leave alert: {'✅ ON' if channel_leave_alert else '❌ OFF'}\n\n"
        
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "Click buttons below to toggle settings:"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"📄 Auto-approve: {'ON' if auto_approve else 'OFF'}", callback_data="setting_auto_approve_pdfs"),
            InlineKeyboardButton(f"📢 Notify upload: {'ON' if notify_admin_upload else 'OFF'}", callback_data="setting_notify_admin_on_upload")
        )
        markup.add(
            InlineKeyboardButton(f"🔐 Membership: {'ON' if membership_enabled else 'OFF'}", callback_data="setting_membership_required"),
            InlineKeyboardButton(f"💬 WhatsApp: {'ON' if whatsapp_enabled else 'OFF'}", callback_data="setting_whatsapp_required")
        )
        markup.add(
            InlineKeyboardButton(f"📢 Broadcast: {'ON' if broadcast_enabled else 'OFF'}", callback_data="setting_broadcast_enabled"),
            InlineKeyboardButton(f"👤 Show admin: {'ON' if show_admin_name else 'OFF'}", callback_data="setting_show_admin_name_in_broadcast")
        )
        markup.add(
            InlineKeyboardButton(f"🔍 Results/page: {search_per_page}", callback_data="setting_search_results_per_page"),
            InlineKeyboardButton(f"👤 Show uploader: {'ON' if show_uploader else 'OFF'}", callback_data="setting_show_uploader_in_search")
        )
        markup.add(
            InlineKeyboardButton(f"🎉 Welcome: {'ON' if welcome_message else 'OFF'}", callback_data="setting_welcome_message_enabled"),
            InlineKeyboardButton(f"⚠️ Leave alert: {'ON' if channel_leave_alert else 'OFF'}", callback_data="setting_channel_leave_alert")
        )
        markup.add(
            InlineKeyboardButton(f"🗑️ User delete: {'ON' if user_can_delete else 'OFF'}", callback_data="setting_allow_user_delete_pdf"),
            InlineKeyboardButton(f"💬 WhatsApp reminders: {whatsapp_reminders}", callback_data="setting_whatsapp_reminders")
        )
        markup.add(
            InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_back")
        )
        
        if message_id:
            try:
                self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
            except Exception as e:
                if DEBUG:
                    print(f"   Could not edit settings: {e}")
                self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    def handle_setting_callback(self, user_id, setting_key, message_id):
        """Handle setting toggles"""
        current = db.get_setting(setting_key, '0')
        
        if DEBUG:
            print(f"⚙️ Toggling setting: {setting_key}, current: {current}")
        
        if setting_key in ['search_results_per_page', 'whatsapp_reminders']:
            # Handle numeric settings
            try:
                current_value = int(current) if current and str(current).isdigit() else 0
            except:
                current_value = 0
            
            if setting_key == 'search_results_per_page':
                # Cycle through: 5, 10, 15, 20, 5
                if current_value == 5:
                    new_value = 10
                elif current_value == 10:
                    new_value = 15
                elif current_value == 15:
                    new_value = 20
                else:
                    new_value = 5
                db.set_setting(setting_key, str(new_value), f"Search results per page: {new_value}")
                self.bot.answer_callback_query(user_id, f"✅ Search results per page set to {new_value}")
            elif setting_key == 'whatsapp_reminders':
                # Cycle through: 0, 1, 2, 3, 4, 5
                new_value = (current_value + 1) % 6
                db.set_setting(setting_key, str(new_value), f"WhatsApp reminders: {new_value}")
                self.bot.answer_callback_query(user_id, f"✅ WhatsApp reminders set to {new_value}")
        else:
            # Handle boolean settings
            new_value = '0' if current == '1' else '1'
            db.set_setting(setting_key, new_value)
            status = "ON" if new_value == '1' else "OFF"
            # Get display name for the setting
            setting_names = {
                'auto_approve_pdfs': 'Auto-approve PDFs',
                'notify_admin_on_upload': 'Notify admin on upload',
                'membership_required': 'Membership required',
                'whatsapp_required': 'WhatsApp required',
                'broadcast_enabled': 'Broadcast enabled',
                'show_admin_name_in_broadcast': 'Show admin name in broadcast',
                'show_uploader_in_search': 'Show uploader in search',
                'welcome_message_enabled': 'Welcome message',
                'channel_leave_alert': 'Channel leave alert',
                'allow_user_delete_pdf': 'User PDF deletion'
            }
            setting_name = setting_names.get(setting_key, setting_key)
            self.bot.answer_callback_query(user_id, f"✅ {setting_name} turned {status}")
        
        # Refresh settings panel
        self.show_settings_panel(user_id, message_id)
    
    # ==================== User Management Functions ====================
    
    def show_user_details(self, user_id, target_user_id, message_id=None):
        """Show detailed user information with management options"""
        user = db.get_user(target_user_id)
        if not user:
            if message_id:
                self.bot.edit_message_text("❌ User not found.", user_id, message_id)
            else:
                self.bot.send_message(user_id, "❌ User not found.")
            return
        
        uploads = db.get_user_upload_count(target_user_id)
        downloads = db.get_user_download_count(target_user_id)
        referrals = db.get_user_referral_stats(target_user_id)
        
        whatsapp_confirmed = db.get_whatsapp_confirmed(target_user_id)
        membership_status = "✅ Completed" if whatsapp_confirmed else "⏳ Pending"
        
        join_date = utils.format_date(user['join_date'])
        last_active = utils.format_date(user['last_active']) if user['last_active'] else "Never"
        
        text = f"👤 **User Details**\n"
        text += "━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📛 **Name:** `{user['full_name']}`\n"
        text += f"🆔 **ID:** `{target_user_id}`\n"
        text += f"📞 **Phone:** `{user['phone'] or 'Not set'}`\n"
        text += f"🎓 **Class:** `{user['class'] or 'Not set'}`\n"
        text += f"📍 **Region:** `{user['region'] or 'Not set'}`\n"
        text += f"🏫 **School:** `{user['school'] or 'Not set'}`\n"
        text += f"📅 **Joined:** `{join_date}`\n"
        text += f"🕐 **Last Active:** `{last_active}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📊 **Stats**\n"
        text += f"📤 **Uploads:** `{uploads}`\n"
        text += f"📥 **Downloads:** `{downloads}`\n"
        text += f"👥 **Referrals:** `{referrals['conversions']}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"🔐 **Membership**\n"
        text += f"├ WhatsApp: `{membership_status}`\n"
        text += f"└ Telegram: Auto-detected\n"
        text += "━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"👑 **Admin:** `{'Yes' if user['is_admin'] else 'No'}`\n"
        text += f"🚫 **Banned:** `{'Yes' if user['is_banned'] else 'No'}`\n"
        
        markup = InlineKeyboardMarkup(row_width=2)
        
        if user['is_banned']:
            markup.add(InlineKeyboardButton("✅ Unban User", callback_data=f"admin_unban_{target_user_id}"))
        else:
            markup.add(InlineKeyboardButton("🚫 Ban User", callback_data=f"admin_ban_{target_user_id}"))
        
        if user['is_admin']:
            markup.add(InlineKeyboardButton("👑 Remove Admin", callback_data=f"admin_remove_admin_{target_user_id}"))
        else:
            markup.add(InlineKeyboardButton("👑 Make Admin", callback_data=f"admin_make_admin_{target_user_id}"))
        
        if not whatsapp_confirmed:
            markup.add(InlineKeyboardButton("✅ Confirm WhatsApp", callback_data=f"admin_confirm_whatsapp_{target_user_id}"))
        
        markup.add(
            InlineKeyboardButton("📄 View User's Uploads", callback_data=f"admin_user_uploads_{target_user_id}"),
            InlineKeyboardButton("📥 View User's Downloads", callback_data=f"admin_user_downloads_{target_user_id}")
        )
        markup.add(InlineKeyboardButton("🔙 Back to Users", callback_data="admin_users"))
        
        if message_id:
            try:
                self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
            except:
                self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    def show_user_uploads(self, user_id, target_user_id, page=0, message_id=None):
        """Show user's uploaded PDFs"""
        limit = 5
        offset = page * limit
        
        pdfs = db.get_pdfs_by_filters(uploaded_by=target_user_id, approved_only=False, limit=limit, offset=offset)
        total = db.count_pdfs_by_filters(uploaded_by=target_user_id, approved_only=False)
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        
        if not pdfs:
            if message_id:
                self.bot.edit_message_text("📭 No uploads found.", user_id, message_id)
            else:
                self.bot.send_message(user_id, "📭 No uploads found.")
            return
        
        text = f"📄 **User Uploads**\n"
        text += f"👤 User ID: `{target_user_id}`\n"
        text += f"📄 Total: `{total}` PDFs\n"
        text += f"📄 Page: `{page + 1}/{total_pages}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for pdf in pdfs:
            status = "✅" if pdf['is_approved'] else "⏳"
            text += f"{status} **{pdf['file_name'][:40]}**\n"
            text += f"   📚 `{pdf['subject']}` | 🏷️ `{pdf['tag']}`\n"
            text += f"   📥 `{pdf['download_count']}` | ❤️ `{pdf['like_count']}`\n"
            text += f"   🆔 `{pdf['id']}`\n\n"
        
        markup = InlineKeyboardMarkup(row_width=3)
        
        if page > 0:
            markup.add(InlineKeyboardButton("◀️ Prev", callback_data=f"admin_user_uploads_page_{target_user_id}_{page-1}"))
        if page < total_pages - 1:
            markup.add(InlineKeyboardButton("Next ▶️", callback_data=f"admin_user_uploads_page_{target_user_id}_{page+1}"))
        
        markup.add(InlineKeyboardButton("🔙 Back to User", callback_data=f"admin_user_details_{target_user_id}"))
        
        if message_id:
            self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    def show_user_downloads(self, user_id, target_user_id, page=0, message_id=None):
        """Show user's downloaded PDFs"""
        limit = 5
        offset = page * limit
        
        with db.get_db() as conn:
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
        
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        
        if not downloads:
            if message_id:
                self.bot.edit_message_text("📭 No downloads found.", user_id, message_id)
            else:
                self.bot.send_message(user_id, "📭 No downloads found.")
            return
        
        text = f"📥 **User Downloads**\n"
        text += f"👤 User ID: `{target_user_id}`\n"
        text += f"📥 Total: `{total}` downloads\n"
        text += f"📄 Page: `{page + 1}/{total_pages}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for download in downloads:
            text += f"📄 **{download['file_name'][:40]}**\n"
            text += f"   📚 `{download['subject']}` | 🏷️ `{download['tag']}`\n"
            text += f"   📅 `{utils.format_date(download['download_date'])}`\n"
            text += f"   🆔 `{download['id']}`\n\n"
        
        markup = InlineKeyboardMarkup(row_width=3)
        
        if page > 0:
            markup.add(InlineKeyboardButton("◀️ Prev", callback_data=f"admin_user_downloads_page_{target_user_id}_{page-1}"))
        if page < total_pages - 1:
            markup.add(InlineKeyboardButton("Next ▶️", callback_data=f"admin_user_downloads_page_{target_user_id}_{page+1}"))
        
        markup.add(InlineKeyboardButton("🔙 Back to User", callback_data=f"admin_user_details_{target_user_id}"))
        
        if message_id:
            self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    # ==================== Delete PDF Functions ====================
    
    def delete_pdf(self, user_id, pdf_id, message_id=None):
        """Delete PDF with confirmation"""
        pdf = db.get_pdf(pdf_id)
        if not pdf:
            self.bot.answer_callback_query(user_id, "❌ PDF not found.")
            return
        
        # Check permission
        user_can_delete = db.get_setting('allow_user_delete_pdf', '0') == '1'
        can_delete = self.is_admin(user_id) or (user_can_delete and pdf['uploaded_by'] == user_id)
        
        if not can_delete:
            self.bot.answer_callback_query(user_id, "❌ You don't have permission to delete this PDF.")
            return
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ Yes, Delete", callback_data=f"confirm_delete_{pdf_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"view_{pdf_id}")
        )
        
        confirm_text = (
            f"⚠️ **Delete PDF?**\n\n"
            f"📄 **File:** `{pdf['file_name'][:50]}`\n"
            f"🆔 **ID:** `{pdf_id}`\n\n"
            f"This action cannot be undone.\n\n"
            f"Are you sure?"
        )
        
        if message_id:
            try:
                self.bot.edit_message_text(
                    confirm_text, user_id, message_id,
                    parse_mode='Markdown', reply_markup=markup
                )
            except:
                self.bot.send_message(
                    user_id, confirm_text,
                    parse_mode='Markdown', reply_markup=markup
                )
        else:
            self.bot.send_message(
                user_id, confirm_text,
                parse_mode='Markdown', reply_markup=markup
            )
    
    def confirm_delete_pdf(self, user_id, pdf_id, message_id=None):
        """Confirm and execute PDF deletion"""
        pdf = db.get_pdf(pdf_id)
        if not pdf:
            self.bot.answer_callback_query(user_id, "❌ PDF not found.")
            return
        
        db.delete_pdf(pdf_id)
        
        if DEBUG:
            print(f"🗑️ PDF {pdf_id} deleted by user {user_id}")
        
        self.bot.answer_callback_query(user_id, f"✅ PDF deleted!")
        
        if message_id:
            try:
                self.bot.delete_message(user_id, message_id)
            except:
                pass
    
    # ==================== Membership Management ====================
    
    def show_membership_management(self, user_id, message_id=None):
        """Show membership requirements management menu"""
        requirements = db.get_requirements(active_only=False)
        
        text = "🔗 **Membership Requirements Management**\n\n"
        text += "Add channels/groups that users must join before using the bot.\n\n"
        
        active_count = sum(1 for req in requirements if req['is_active'])
        inactive_count = len(requirements) - active_count
        
        text += f"📊 **Summary:**\n"
        text += f"├ ✅ Active: `{active_count}`\n"
        text += f"└ ❌ Inactive: `{inactive_count}`\n\n"
        
        if requirements:
            text += "**Current Requirements:**\n"
            for req in requirements[:5]:
                status = "✅" if req['is_active'] else "❌"
                type_icon = "📢" if req['type'] == 'telegram' else "💬"
                text += f"\n{status} {type_icon} **{req['name']}** ({req['type'].upper()})\n"
                text += f"   🔗 `{req['link'][:30]}...`\n"
            
            if len(requirements) > 5:
                text += f"\n... and {len(requirements) - 5} more. Use **List All** to see full list."
        else:
            text += "*No requirements set yet.*\n"
        
        text += "\n**Actions:**"
        
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
            InlineKeyboardButton("📊 Detailed Stats", callback_data="admin_membership_stats"),
            InlineKeyboardButton("📋 Event Log", callback_data="admin_membership_events")
        )
        markup.add(
            InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_back")
        )
        
        if message_id:
            self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    def show_membership_list(self, user_id, message_id=None, page=0):
        """Show paginated list of membership requirements"""
        requirements = db.get_requirements(active_only=False)
        
        if not requirements:
            if message_id:
                self.bot.edit_message_text("📭 No requirements found.", user_id, message_id)
            else:
                self.bot.send_message(user_id, "📭 No requirements found.")
            return
        
        items_per_page = 5
        total_pages = (len(requirements) + items_per_page - 1) // items_per_page
        start = page * items_per_page
        end = start + items_per_page
        page_items = requirements[start:end]
        
        text = f"🔗 **Membership Requirements**\n"
        text += f"📄 Page `{page + 1}/{total_pages}` | Total: `{len(requirements)}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for req in page_items:
            status = "✅ ACTIVE" if req['is_active'] else "❌ INACTIVE"
            type_icon = "📢" if req['type'] == 'telegram' else "💬"
            
            text += f"{type_icon} **ID: {req['id']} - {req['name']}**\n"
            text += f"├ Type: `{req['type'].upper()}`\n"
            text += f"├ Link: `{req['link'][:40]}{'...' if len(req['link']) > 40 else ''}`\n"
            text += f"├ Status: {status}\n"
            if req['description']:
                desc = req['description'][:50] + ('...' if len(req['description']) > 50 else '')
                text += f"└ Description: {desc}\n"
            text += "\n"
        
        markup = InlineKeyboardMarkup(row_width=3)
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"membership_list_page_{page-1}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"membership_list_page_{page+1}"))
        if nav_buttons:
            markup.row(*nav_buttons)
        
        for req in page_items:
            type_icon = "📢" if req['type'] == 'telegram' else "💬"
            action_text = f"{type_icon} {req['name'][:20]}"
            markup.add(InlineKeyboardButton(action_text, callback_data=f"membership_edit_{req['id']}"))
        
        markup.add(InlineKeyboardButton("➕ Add New", callback_data="membership_add_menu"))
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="membership_back"))
        
        if message_id:
            self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    def show_membership_edit(self, user_id, req_id, message_id=None):
        """Show edit options for a specific membership requirement"""
        req = db.get_requirement(req_id)
        if not req:
            self.bot.edit_message_text("❌ Requirement not found.", user_id, message_id)
            return
        
        status = "✅ Active" if req['is_active'] else "❌ Inactive"
        type_icon = "📢" if req['type'] == 'telegram' else "💬"
        
        text = f"{type_icon} **Edit Requirement: {req['name']}**\n"
        text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        text += f"🆔 **ID:** `{req['id']}`\n"
        text += f"📌 **Type:** `{req['type'].upper()}`\n"
        text += f"🔗 **Link:** `{req['link']}`\n"
        text += f"📊 **Status:** {status}\n"
        if req['description']:
            text += f"📝 **Description:** {req['description']}\n"
        text += f"📅 **Created:** `{req['created_at'][:10] if req['created_at'] else 'Unknown'}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        users = db.get_all_users()
        members = 0
        for user in users:
            if req['type'] == 'telegram':
                if utils.is_telegram_member(self.bot, user['user_id'], req['link']):
                    members += 1
            else:
                if db.get_whatsapp_confirmed(user['user_id']):
                    members += 1
        
        if users:
            percentage = int(members / len(users) * 100)
        else:
            percentage = 0
        
        text += f"📊 **Stats:**\n"
        text += f"├ 👥 Total Users: `{len(users)}`\n"
        text += f"└ ✅ Members: `{members}` ({percentage}%)\n"
        
        markup = InlineKeyboardMarkup(row_width=2)
        
        if req['is_active']:
            markup.add(InlineKeyboardButton("❌ Deactivate", callback_data=f"membership_toggle_{req_id}_0"))
        else:
            markup.add(InlineKeyboardButton("✅ Activate", callback_data=f"membership_toggle_{req_id}_1"))
        
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
            self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    def show_membership_stats(self, user_id, message_id=None):
        """Show detailed membership statistics for all requirements"""
        requirements = db.get_requirements(active_only=True)
        users = db.get_all_users()
        
        text = "📊 **MEMBERSHIP STATISTICS**\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"👥 **Total Users:** `{len(users)}`\n\n"
        
        if requirements:
            text += "**REQUIREMENTS BREAKDOWN**\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for req in requirements:
                members = 0
                for user in users:
                    if req['type'] == 'telegram':
                        if utils.is_telegram_member(self.bot, user['user_id'], req['link']):
                            members += 1
                    else:
                        if db.get_whatsapp_confirmed(user['user_id']):
                            members += 1
                
                percentage = int(members / len(users) * 100) if users else 0
                type_icon = "📢" if req['type'] == 'telegram' else "💬"
                
                bar_length = 20
                filled = int(bar_length * percentage / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                
                text += f"{type_icon} **{req['name']}**\n"
                text += f"├ Type: `{req['type'].upper()}`\n"
                text += f"├ Members: `{members}/{len(users)}` ({percentage}%)\n"
                text += f"├ Progress: `{bar}`\n"
                text += f"└ Link: `{req['link'][:50]}{'...' if len(req['link']) > 50 else ''}`\n\n"
            
            total_joined_telegram = 0
            total_joined_whatsapp = 0
            
            for user in users:
                all_telegram = True
                for req in requirements:
                    if req['type'] == 'telegram':
                        if not utils.is_telegram_member(self.bot, user['user_id'], req['link']):
                            all_telegram = False
                            break
                if all_telegram:
                    total_joined_telegram += 1
                
                if db.get_whatsapp_confirmed(user['user_id']):
                    total_joined_whatsapp += 1
            
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            text += "**OVERALL COMPLETION**\n"
            text += f"├ Telegram All Joined: `{total_joined_telegram}/{len(users)}` ({int(total_joined_telegram/len(users)*100) if users else 0}%)\n"
            text += f"└ WhatsApp Confirmed: `{total_joined_whatsapp}/{len(users)}` ({int(total_joined_whatsapp/len(users)*100) if users else 0}%)\n"
        else:
            text += "*No active requirements.*\n"
        
        text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "*Note:* Users must join all active requirements to use the bot."
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🔄 Refresh", callback_data="admin_membership_stats"),
            InlineKeyboardButton("📋 Events", callback_data="admin_membership_events"),
            InlineKeyboardButton("🔙 Back", callback_data="admin_back")
        )
        
        if message_id:
            self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    def show_membership_events(self, user_id, message_id=None, page=0):
        """Show recent membership events for monitoring"""
        events = db.get_recent_membership_events(limit=20)
        
        if not events:
            if message_id:
                self.bot.edit_message_text("📭 No membership events found.", user_id, message_id)
            else:
                self.bot.send_message(user_id, "📭 No membership events found.")
            return
        
        items_per_page = 10
        total_pages = (len(events) + items_per_page - 1) // items_per_page
        start = page * items_per_page
        end = start + items_per_page
        page_events = events[start:end]
        
        text = "📋 **MEMBERSHIP EVENTS**\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📄 Page `{page + 1}/{total_pages}` | Total: `{len(events)}` events\n\n"
        
        for event in page_events:
            event_type_icon = "✅" if event['event_type'] == 'confirm_whatsapp' else "❓"
            text += f"{event_type_icon} **{event['event_type'].replace('_', ' ').title()}**\n"
            text += f"├ 👤 User: `{event['user_name'] or event['user_id']}`\n"
            text += f"├ 📢 Requirement: `{event['requirement_name'] or 'N/A'}`\n"
            text += f"└ 📅 Time: `{utils.format_date(event['event_date'])}`\n\n"
        
        markup = InlineKeyboardMarkup(row_width=3)
        
        if page > 0:
            markup.add(InlineKeyboardButton("◀️ Prev", callback_data=f"membership_events_page_{page-1}"))
        if page < total_pages - 1:
            markup.add(InlineKeyboardButton("Next ▶️", callback_data=f"membership_events_page_{page+1}"))
        
        markup.add(InlineKeyboardButton("🔄 Refresh", callback_data="admin_membership_events"))
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="admin_back"))
        
        if message_id:
            self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    def show_membership_analytics(self, user_id, message_id=None):
        """Show membership analytics for admin"""
        users = db.get_all_users()
        requirements = db.get_requirements(active_only=True)
        
        if not users or not requirements:
            text = "📊 **MEMBERSHIP ANALYTICS**\n\n"
            text += "Not enough data to display analytics.\n"
            text += "Add requirements and wait for users to join."
            if message_id:
                self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown')
            else:
                self.bot.send_message(user_id, text, parse_mode='Markdown')
            return
        
        text = "📈 **MEMBERSHIP ANALYTICS**\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        completed_users = 0
        partial_users = 0
        
        for user in users:
            all_joined = True
            for req in requirements:
                if req['type'] == 'telegram':
                    if not utils.is_telegram_member(self.bot, user['user_id'], req['link']):
                        all_joined = False
                        break
                else:
                    if not db.get_whatsapp_confirmed(user['user_id']):
                        all_joined = False
                        break
            if all_joined:
                completed_users += 1
            else:
                partial_users += 1
        
        total = len(users)
        completion_rate = int(completed_users / total * 100) if total > 0 else 0
        
        text += "**COMPLETION RATE**\n"
        bar_length = 20
        filled = int(bar_length * completion_rate / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        text += f"└ `{bar}` {completion_rate}%\n\n"
        
        text += "**DISTRIBUTION**\n"
        text += f"├ ✅ Fully Completed: `{completed_users}` users\n"
        text += f"└ ⏳ Partial/None: `{partial_users}` users\n\n"
        
        text += "**RECENT ACTIVITY (Last 7 days)**\n"
        from datetime import timedelta
        now = get_current_time()
        
        for i in range(7, 0, -1):
            date = now - timedelta(days=i)
            day_count = 0
            for event in db.get_recent_membership_events(limit=100):
                event_date = datetime.fromisoformat(event['event_date']) if isinstance(event['event_date'], str) else event['event_date']
                if event_date.date() == date.date():
                    day_count += 1
            bar = "█" * min(day_count, 10)
            text += f"├ {date.strftime('%a')}: `{bar}` ({day_count} events)\n"
        
        text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "**Actions:**"
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("📊 Detailed Stats", callback_data="admin_membership_stats"),
            InlineKeyboardButton("📋 Events", callback_data="admin_membership_events"),
            InlineKeyboardButton("🔙 Back", callback_data="admin_back")
        )
        
        if message_id:
            self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    # ==================== Add Requirement Flow ====================
    
    def start_add_requirement(self, user_id, req_type, message_id=None):
        """Start the process of adding a new requirement"""
        type_icon = "📢" if req_type == 'telegram' else "💬"
        
        text = f"{type_icon} **Add {req_type.upper()} Requirement**\n\n"
        text += f"Please send the **name** for this {req_type} requirement.\n\n"
        text += f"📌 **Example:** `Main Channel` or `Support Group`\n\n"
        text += f"Type **Cancel** to cancel."
        
        if message_id:
            try:
                self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown')
            except:
                self.bot.send_message(user_id, text, parse_mode='Markdown')
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown')
        
        db.set_user_state(user_id, 'add_requirement', {'type': req_type, 'step': 'name'})
    
    def process_add_requirement(self, user_id, message):
        """Process the add requirement flow"""
        current_state, data = db.get_user_state(user_id)
        
        if current_state != 'add_requirement':
            return False
        
        step = data.get('step')
        
        if step == 'name':
            name = message.text.strip()
            
            if name.lower() == texts.BUTTON_CANCEL.lower():
                db.clear_user_state(user_id)
                self.bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard(user_id))
                return True
            
            if len(name) < 3:
                self.bot.send_message(user_id, "❌ Name must be at least 3 characters. Please try again.")
                return True
            
            data['name'] = name
            data['step'] = 'link'
            db.set_user_state(user_id, 'add_requirement', data)
            
            req_type = data['type']
            type_icon = "📢" if req_type == 'telegram' else "💬"
            
            if req_type == 'telegram':
                text = f"{type_icon} **Add {req_type.upper()} Requirement**\n\n"
                text += f"📌 **Name:** `{name}`\n\n"
                text += f"Now send the **channel/group link**.\n\n"
                text += f"📌 **Example:** `https://t.me/username` or `@username`\n\n"
                text += f"Type **Cancel** to cancel."
            else:
                text = f"{type_icon} **Add {req_type.upper()} Requirement**\n\n"
                text += f"📌 **Name:** `{name}`\n\n"
                text += f"Now send the **WhatsApp group invite link**.\n\n"
                text += f"📌 **Example:** `https://chat.whatsapp.com/xxxxx`\n\n"
                text += f"💡 **Tip:** Add a description after to explain the purpose of this group.\n\n"
                text += f"Type **Cancel** to cancel."
            
            self.bot.send_message(user_id, text, parse_mode='Markdown')
            return True
        
        elif step == 'link':
            link = message.text.strip()
            
            if link.lower() == texts.BUTTON_CANCEL.lower():
                db.clear_user_state(user_id)
                self.bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard(user_id))
                return True
            
            if data['type'] == 'telegram':
                if not ('t.me/' in link or link.startswith('@')):
                    self.bot.send_message(user_id, "❌ Invalid Telegram link. Please use format: `https://t.me/username` or `@username`", parse_mode='Markdown')
                    return True
            else:
                if 'chat.whatsapp.com' not in link:
                    self.bot.send_message(user_id, "❌ Invalid WhatsApp link. Please use format: `https://chat.whatsapp.com/xxxxx`", parse_mode='Markdown')
                    return True
            
            data['link'] = link
            data['step'] = 'description'
            db.set_user_state(user_id, 'add_requirement', data)
            
            text = f"📝 **Add {data['type'].upper()} Requirement**\n\n"
            text += f"📌 **Name:** `{data['name']}`\n"
            text += f"🔗 **Link:** `{link}`\n\n"
            text += f"Now send a **description** (optional but recommended).\n\n"
            text += f"📝 **Example for WhatsApp:** 'This group is for sharing study tips and updates. Admin: @username'\n\n"
            text += f"Type `skip` to skip or **Cancel** to cancel."
            
            self.bot.send_message(user_id, text, parse_mode='Markdown')
            return True
        
        elif step == 'description':
            description = message.text.strip()
            
            if description.lower() == texts.BUTTON_CANCEL.lower():
                db.clear_user_state(user_id)
                self.bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard(user_id))
                return True
            
            if description.lower() == 'skip':
                description = None
            
            req_id = db.add_requirement(
                name=data['name'],
                req_type=data['type'],
                link=data['link'],
                description=description,
                created_by=user_id
            )
            
            db.clear_user_state(user_id)
            
            type_icon = "📢" if data['type'] == 'telegram' else "💬"
            
            text = f"✅ **Requirement Added Successfully!**\n\n"
            text += f"{type_icon} **Name:** {data['name']}\n"
            text += f"📌 **Type:** {data['type'].upper()}\n"
            text += f"🔗 **Link:** `{data['link']}`\n"
            if description:
                text += f"📝 **Description:** {description}\n"
            text += f"🆔 **ID:** `{req_id}`\n\n"
            text += f"Users must now join this to use the bot."
            
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=utils.create_main_menu_keyboard(user_id))
            
            for admin_id in ADMIN_IDS:
                if admin_id != user_id:
                    try:
                        self.bot.send_message(
                            admin_id,
                            f"🔔 **New Requirement Added**\n\n"
                            f"{type_icon} **Name:** {data['name']}\n"
                            f"📌 **Type:** {data['type'].upper()}\n"
                            f"🔗 **Link:** `{data['link']}`\n"
                            f"📝 **Description:** {description or 'None'}\n"
                            f"👤 **Added by:** `{user_id}`",
                            parse_mode='Markdown'
                        )
                    except:
                        pass
            
            return True
        
        return False
    
    # ==================== Edit Requirement Flow ====================
    
    def edit_requirement_field(self, user_id, req_id, field, message_id=None):
        """Start editing a specific field of a requirement"""
        req = db.get_requirement(req_id)
        if not req:
            self.bot.send_message(user_id, "❌ Requirement not found.")
            return
        
        field_names = {
            'name': 'Name',
            'link': 'Link',
            'desc': 'Description'
        }
        
        current_value = req[field] if field != 'desc' else req['description']
        if not current_value:
            current_value = '(empty)'
        
        text = f"✏️ **Edit {field_names[field]}**\n\n"
        text += f"Current value: `{current_value}`\n\n"
        text += f"Please send the new {field_names[field].lower()}.\n\n"
        text += f"Type **Cancel** to cancel."
        
        if message_id:
            try:
                self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown')
            except:
                self.bot.send_message(user_id, text, parse_mode='Markdown')
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown')
        
        db.set_user_state(user_id, 'edit_requirement', {
            'req_id': req_id,
            'field': field,
            'step': 'value'
        })
    
    def process_edit_requirement(self, user_id, message):
        """Process the edit requirement flow"""
        current_state, data = db.get_user_state(user_id)
        
        if current_state != 'edit_requirement':
            return False
        
        new_value = message.text.strip()
        
        if new_value.lower() == texts.BUTTON_CANCEL.lower():
            db.clear_user_state(user_id)
            self.bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard(user_id))
            return True
        
        req_id = data['req_id']
        field = data['field']
        
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
        
        self.bot.send_message(
            user_id,
            f"✅ **Requirement updated successfully!**\n\n"
            f"📝 **Field:** {field_display[field]}\n"
            f"🆕 **New value:** `{new_value}`",
            parse_mode='Markdown',
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )
        
        return True
    
    # ==================== Membership Verification ====================
    
    def verify_telegram_membership(self, user_id, requirement_id):
        req = db.get_requirement(requirement_id)
        if not req:
            return False
        
        if utils.is_telegram_member(self.bot, user_id, req['link']):
            db.record_membership(user_id, requirement_id, True)
            return True
        
        return False
    
    def start_whatsapp_verification(self, user_id, requirement_id):
        import random
        import string
        
        code = ''.join(random.choices(string.digits, k=6))
        
        db.add_whatsapp_verification(user_id, requirement_id, code)
        
        req = db.get_requirement(requirement_id)
        
        text = f"🔐 **WhatsApp Verification**\n\n"
        text += f"To verify you've joined **{req['name']}**, please send this code in the WhatsApp group:\n\n"
        text += f"`VERIFY {code}`\n\n"
        text += f"After sending, click the button below to confirm."
        
        if req['description']:
            text += f"\n\n💡 **About this group:** {req['description']}"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ I've Sent the Code", callback_data=f"confirm_whatsapp_{requirement_id}_{code}"),
            InlineKeyboardButton("📱 Join Group", url=req['link'])
        )
        markup.add(InlineKeyboardButton("🔙 Cancel", callback_data="cancel"))
        
        self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    def confirm_whatsapp_verification(self, user_id, requirement_id, code):
        verification = db.get_whatsapp_verification(user_id, requirement_id)
        
        if verification and verification['verification_code'] == code:
            db.record_membership(user_id, requirement_id, True)
            self.bot.send_message(
                user_id, 
                texts.WHATSAPP_VERIFICATION_SUCCESS, 
                parse_mode='Markdown',
                reply_markup=utils.create_main_menu_keyboard(user_id)
            )
            return True
        else:
            self.bot.send_message(
                user_id, 
                texts.WHATSAPP_VERIFICATION_FAILED, 
                parse_mode='Markdown'
            )
            return False
    
    def admin_confirm_whatsapp(self, user_id, target_user_id, message_id=None):
        db.set_whatsapp_confirmed(target_user_id, True)
        db.log_membership_event(target_user_id, None, 'admin_confirm')
        
        self.bot.answer_callback_query(user_id, f"✅ WhatsApp confirmed for user {target_user_id}!")
        self.show_user_details(user_id, target_user_id, message_id)
    
    def start_admin_reply_to_user(self, user_id, target_user_id, message_id=None):
        if DEBUG:
            print(f"📝 Admin {user_id} starting reply to user {target_user_id}")
        
        db.set_user_state(user_id, 'admin_reply_user', {
            'target_user_id': target_user_id,
            'step': 'waiting_for_message'
        })
        
        self.bot.send_message(
            user_id,
            f"💬 **Reply to User**\n\n"
            f"👤 **User ID:** `{target_user_id}`\n\n"
            f"Please type your reply message below.\n\n"
            f"Type **Cancel** to cancel.",
            parse_mode='Markdown',
            reply_markup=utils.create_cancel_keyboard()
        )
        
        if message_id:
            try:
                self.bot.delete_message(user_id, message_id)
            except:
                pass
    
    def send_admin_reply_to_user(self, admin_id, target_user_id, reply_text):
        admin = db.get_user(admin_id)
        admin_name = admin['full_name'] if admin else f"Admin {admin_id}"
        
        user_message = (
            f"📢 **REPLY FROM ADMIN**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{reply_text}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Admin:** {admin_name}\n"
            f"📅 **Date:** {get_current_time().strftime('%Y-%m-%d %I:%M %p')}"
        )
        
        try:
            self.bot.send_message(
                target_user_id,
                user_message,
                parse_mode='Markdown'
            )
            return True
        except Exception as e:
            if DEBUG:
                print(f"❌ Failed to send admin reply to user {target_user_id}: {e}")
            return False
    
    # ==================== Admin Callback Handler ====================
    
    def handle_admin_callback(self, call):
        user_id = call.from_user.id
        
        if not self.is_admin(user_id):
            self.bot.answer_callback_query(call.id, texts.ERROR_PERMISSION)
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
            try:
                self.bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown')
            except:
                self.bot.send_message(user_id, text, parse_mode='Markdown')
            self.bot.answer_callback_query(call.id)
            return
        
        # Settings
        if data == "admin_settings":
            self.show_settings_panel(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        # Setting toggles - Fixed: now handles full setting keys
        if data.startswith("setting_"):
            setting_key = data[8:]  # Remove "setting_" prefix
            self.handle_setting_callback(user_id, setting_key, call.message.message_id)
            return
        
        # Membership management
        if data == "admin_membership":
            self.show_membership_management(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "admin_membership_stats":
            self.show_membership_stats(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "admin_membership_events":
            self.show_membership_events(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "admin_membership_analytics":
            self.show_membership_analytics(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data.startswith("membership_events_page_"):
            page = int(data.split("_")[3])
            self.show_membership_events(user_id, call.message.message_id, page)
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "membership_back":
            self.show_membership_management(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "membership_list":
            self.show_membership_list(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data.startswith("membership_list_page_"):
            page = int(data.split("_")[-1])
            self.show_membership_list(user_id, call.message.message_id, page)
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "membership_add_telegram":
            self.start_add_requirement(user_id, 'telegram', call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "membership_add_whatsapp":
            self.start_add_requirement(user_id, 'whatsapp', call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "membership_add_menu":
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("📢 Telegram Channel", callback_data="membership_add_telegram"),
                InlineKeyboardButton("💬 WhatsApp Group", callback_data="membership_add_whatsapp")
            )
            markup.add(InlineKeyboardButton("🔙 Back", callback_data="membership_back"))
            try:
                self.bot.edit_message_text(
                    "➕ **Add New Requirement**\n\nSelect type:",
                    user_id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            except:
                self.bot.send_message(
                    user_id,
                    "➕ **Add New Requirement**\n\nSelect type:",
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            self.bot.answer_callback_query(call.id)
            return
        
        if data.startswith("membership_edit_"):
            req_id = int(data.split("_")[2])
            self.show_membership_edit(user_id, req_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data.startswith("membership_toggle_"):
            parts = data.split("_")
            req_id = int(parts[2])
            is_active = bool(int(parts[3]))
            db.toggle_requirement(req_id, is_active)
            
            status = "activated" if is_active else "deactivated"
            self.bot.answer_callback_query(call.id, f"✅ Requirement {status}!")
            self.show_membership_edit(user_id, req_id, call.message.message_id)
            return
        
        if data.startswith("membership_edit_name_"):
            req_id = int(data.split("_")[3])
            self.edit_requirement_field(user_id, req_id, 'name', call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data.startswith("membership_edit_link_"):
            req_id = int(data.split("_")[3])
            self.edit_requirement_field(user_id, req_id, 'link', call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data.startswith("membership_edit_desc_"):
            req_id = int(data.split("_")[3])
            self.edit_requirement_field(user_id, req_id, 'desc', call.message.message_id)
            self.bot.answer_callback_query(call.id)
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
            
            try:
                self.bot.edit_message_text(
                    f"⚠️ **Delete Requirement?**\n\n"
                    f"Are you sure you want to delete:\n"
                    f"{type_icon} **{req['name']}** ({req['type'].upper()})\n\n"
                    f"This action cannot be undone.",
                    user_id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            except:
                self.bot.send_message(
                    user_id,
                    f"⚠️ **Delete Requirement?**\n\n"
                    f"Are you sure you want to delete:\n"
                    f"{type_icon} **{req['name']}** ({req['type'].upper()})\n\n"
                    f"This action cannot be undone.",
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            self.bot.answer_callback_query(call.id)
            return
        
        if data.startswith("membership_confirm_delete_"):
            req_id = int(data.split("_")[3])
            db.delete_requirement(req_id)
            self.bot.answer_callback_query(call.id, "🗑️ Requirement deleted!")
            self.show_membership_list(user_id, call.message.message_id)
            return
        
        # Admin WhatsApp confirmation
        if data.startswith("admin_confirm_whatsapp_"):
            target_user_id = int(data.split("_")[3])
            self.admin_confirm_whatsapp(user_id, target_user_id, call.message.message_id)
            return
        
        # Membership verification (legacy)
        if data.startswith("verify_telegram_"):
            req_id = int(data.split("_")[2])
            if self.verify_telegram_membership(user_id, req_id):
                self.bot.answer_callback_query(call.id, "✅ Verified! You can now use the bot.")
                if self.handlers:
                    all_met, missing = self.handlers.check_all_memberships(user_id)
                    if all_met and self.handlers:
                        self.handlers.show_main_menu(user_id)
            else:
                self.bot.answer_callback_query(call.id, "❌ Not a member yet. Please join first.", show_alert=True)
            return
        
        if data.startswith("verify_whatsapp_"):
            req_id = int(data.split("_")[2])
            self.start_whatsapp_verification(user_id, req_id)
            try:
                self.bot.delete_message(user_id, call.message.message_id)
            except:
                pass
            self.bot.answer_callback_query(call.id)
            return
        
        if data.startswith("confirm_whatsapp_"):
            parts = data.split("_")
            req_id = int(parts[2])
            code = parts[3]
            if self.confirm_whatsapp_verification(user_id, req_id, code):
                self.bot.answer_callback_query(call.id, "✅ Verified!")
                if self.handlers:
                    all_met, missing = self.handlers.check_all_memberships(user_id)
                    if all_met and self.handlers:
                        self.handlers.show_main_menu(user_id)
            else:
                self.bot.answer_callback_query(call.id, "❌ Verification failed. Please try again.")
            return
        
        # Back to admin
        if data == "admin_back":
            self.show_admin_panel(user_id)
            try:
                self.bot.delete_message(user_id, call.message.message_id)
            except:
                pass
            self.bot.answer_callback_query(call.id)
            return
        
        # Broadcast
        if data == "admin_broadcast":
            broadcast_enabled = db.get_setting('broadcast_enabled', '1') == '1'
            if not broadcast_enabled:
                self.bot.answer_callback_query(call.id, "❌ Broadcast is disabled in settings.")
                return
            
            db.set_user_state(user_id, 'admin_broadcast', {})
            try:
                self.bot.delete_message(user_id, call.message.message_id)
            except:
                pass
            self.bot.send_message(
                user_id,
                texts.ADMIN_BROADCAST_PROMPT,
                parse_mode='Markdown',
                reply_markup=utils.create_cancel_keyboard()
            )
            self.bot.answer_callback_query(call.id)
            return
        
        # SQL Console
        if data == "admin_sql":
            db.clear_user_state(user_id)
            db.set_user_state(user_id, 'admin_sql', {})
            
            if DEBUG:
                print(f"🔧 SQL Console opened by admin {user_id}")
            
            try:
                self.bot.delete_message(user_id, call.message.message_id)
            except:
                pass
            
            self.bot.send_message(
                user_id,
                texts.ADMIN_SQL_PROMPT,
                parse_mode='Markdown',
                reply_markup=utils.create_cancel_keyboard()
            )
            self.bot.answer_callback_query(call.id)
            return
        
        # Users list
        if data == "admin_users":
            users = db.get_all_users(limit=30)
            total_users = db.count_users()
            
            text = "👥 **User List**\n"
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
            
            try:
                self.bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
            except:
                self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
            self.bot.answer_callback_query(call.id)
            return
        
        # User details
        if data.startswith("admin_user_details_"):
            target_user_id = int(data.split("_")[3])
            self.show_user_details(user_id, target_user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        # User uploads
        if data.startswith("admin_user_uploads_"):
            parts = data.split("_")
            if len(parts) == 4:
                target_user_id = int(parts[3])
                self.show_user_uploads(user_id, target_user_id, 0, call.message.message_id)
            elif len(parts) == 6 and parts[4] == "page":
                target_user_id = int(parts[4])
                page = int(parts[5])
                self.show_user_uploads(user_id, target_user_id, page, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        # User downloads
        if data.startswith("admin_user_downloads_"):
            parts = data.split("_")
            if len(parts) == 4:
                target_user_id = int(parts[3])
                self.show_user_downloads(user_id, target_user_id, 0, call.message.message_id)
            elif len(parts) == 6 and parts[4] == "page":
                target_user_id = int(parts[4])
                page = int(parts[5])
                self.show_user_downloads(user_id, target_user_id, page, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        # Ban/Unban
        if data.startswith("admin_ban_"):
            target_user_id = int(data.split("_")[2])
            db.ban_user(target_user_id)
            self.bot.answer_callback_query(call.id, f"🚫 User {target_user_id} banned!")
            self.show_user_details(user_id, target_user_id, call.message.message_id)
            return
        
        if data.startswith("admin_unban_"):
            target_user_id = int(data.split("_")[2])
            db.unban_user(target_user_id)
            self.bot.answer_callback_query(call.id, f"✅ User {target_user_id} unbanned!")
            self.show_user_details(user_id, target_user_id, call.message.message_id)
            return
        
        # Make/Remove admin
        if data.startswith("admin_make_admin_"):
            target_user_id = int(data.split("_")[3])
            db.set_admin(target_user_id, True)
            self.bot.answer_callback_query(call.id, f"👑 User {target_user_id} is now admin!")
            self.show_user_details(user_id, target_user_id, call.message.message_id)
            return
        
        if data.startswith("admin_remove_admin_"):
            target_user_id = int(data.split("_")[3])
            db.set_admin(target_user_id, False)
            self.bot.answer_callback_query(call.id, f"👑 Admin rights removed from {target_user_id}!")
            self.show_user_details(user_id, target_user_id, call.message.message_id)
            return
        
        # Pending PDFs
        if data == "admin_pending":
            pending = db.get_unapproved_pdfs()
            if not pending:
                try:
                    self.bot.edit_message_text("📭 No pending PDFs.", user_id, call.message.message_id)
                except:
                    self.bot.send_message(user_id, "📭 No pending PDFs.")
                self.bot.answer_callback_query(call.id)
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
            
            try:
                self.bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
            except:
                self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
            self.bot.answer_callback_query(call.id)
            return
        
        # Reports
        if data == "admin_reports":
            reports = db.get_pending_reports()
            if not reports:
                try:
                    self.bot.edit_message_text("📭 No pending reports.", user_id, call.message.message_id)
                except:
                    self.bot.send_message(user_id, "📭 No pending reports.")
                self.bot.answer_callback_query(call.id)
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
            
            try:
                self.bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
            except:
                self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
            self.bot.answer_callback_query(call.id)
            return
        
        # Resolve report
        if data.startswith("resolve_report_"):
            report_id = int(data.split("_")[2])
            db.resolve_report(report_id)
            self.bot.answer_callback_query(call.id, "✅ Report resolved!")
            # Refresh admin panel or pending list
            self.handle_admin_callback(call)
            return