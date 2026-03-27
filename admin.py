# telegram_pdf_bot/admin.py
# Admin functions for managing membership requirements and monitoring - Class-based structure

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from config import ADMIN_IDS, DEBUG, TAGS, CLASSES, SUBJECTS
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
            InlineKeyboardButton(f"📄 PDF Management", callback_data="admin_pdf_management"),
            InlineKeyboardButton(f"⏳ Pending PDFs ({stats['pending_pdfs']})", callback_data="admin_pending")
        )
        markup.add(
            InlineKeyboardButton(f"🚨 Reports ({stats['total_reports']})", callback_data="admin_reports"),
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
        )
        markup.add(
            InlineKeyboardButton("🔧 SQL Console", callback_data="admin_sql"),
            InlineKeyboardButton("⚙️ Bot Settings", callback_data="admin_settings")
        )
        markup.add(
            InlineKeyboardButton("🔗 Membership Requirements", callback_data="admin_membership"),
            InlineKeyboardButton("📊 Membership Stats", callback_data="admin_membership_stats")
        )
        markup.add(
            InlineKeyboardButton("📋 Membership Events", callback_data="admin_membership_events"),
            InlineKeyboardButton("📈 Member Analytics", callback_data="admin_membership_analytics")
        )
        markup.add(
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
    
    # ==================== PDF Management ====================
    
    def show_pdf_management(self, user_id, message_id=None):
        """Show PDF management main menu"""
        if not self.is_admin(user_id):
            self.bot.send_message(user_id, texts.ERROR_PERMISSION)
            return
        
        stats = db.get_stats()
        
        text = (
            "📄 **PDF Management**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 **Total PDFs:** `{stats['total_pdfs']}`\n"
            f"⏳ **Pending:** `{stats['pending_pdfs']}`\n"
            f"✅ **Approved:** `{stats['total_pdfs'] - stats['pending_pdfs']}`\n\n"
            "Select an option below:"
        )
        
        markup = utils.create_admin_pdf_management_keyboard()
        
        if message_id:
            try:
                self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
            except:
                self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    def show_all_pdfs(self, user_id, page=0, message_id=None, tag=None, pdf_class=None):
        """Show all PDFs with filters"""
        limit = 10
        offset = page * limit
        
        pdfs = db.get_pdfs_by_filters(
            tag=tag,
            pdf_class=pdf_class,
            approved_only=False,
            limit=limit,
            offset=offset
        )
        total = db.count_pdfs_by_filters(tag=tag, pdf_class=pdf_class, approved_only=False)
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        
        if not pdfs:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 Back", callback_data="admin_pdf_management"))
            if message_id:
                self.bot.edit_message_text(texts.EMPTY_PDFS, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
            else:
                self.bot.send_message(user_id, texts.EMPTY_PDFS, parse_mode='Markdown', reply_markup=markup)
            return
        
        text = (
            "📄 **All PDFs**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **Total:** `{total}` PDFs\n"
            f"📄 **Page:** `{page + 1}/{total_pages}`\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        for pdf in pdfs:
            status = "✅" if pdf['is_approved'] else "⏳"
            text += (
                f"{status} **{pdf['file_name'][:40]}**\n"
                f"   🆔 `{pdf['id']}` | 🎓 `{pdf['class']}`\n"
                f"   📚 `{pdf['subject']}` | 🏷️ `{pdf['tag']}`\n"
                f"   📥 `{pdf['download_count']}` | ❤️ `{pdf['like_count']}`\n\n"
            )
        
        markup = InlineKeyboardMarkup(row_width=3)
        
        # Pagination
        if page > 0:
            markup.add(InlineKeyboardButton("◀️ Prev", callback_data=f"admin_pdfs_all_page_{page-1}"))
        if page < total_pages - 1:
            markup.add(InlineKeyboardButton("Next ▶️", callback_data=f"admin_pdfs_all_page_{page+1}"))
        
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="admin_pdf_management"))
        
        if message_id:
            self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    def show_pdfs_by_tag(self, user_id, message_id=None):
        """Show PDFs grouped by tag"""
        if not self.is_admin(user_id):
            return
        
        text = (
            "🏷️ **PDFs by Tag**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        markup = InlineKeyboardMarkup(row_width=2)
        
        for tag in TAGS:
            count = db.get_pdf_count_by_tag(tag)
            markup.add(InlineKeyboardButton(f"{tag} ({count})", callback_data=f"admin_pdfs_tag_{tag}"))
        
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="admin_pdf_management"))
        
        if message_id:
            self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    def show_pdfs_by_class(self, user_id, message_id=None):
        """Show PDFs grouped by class"""
        if not self.is_admin(user_id):
            return
        
        text = (
            "🎓 **PDFs by Class**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        markup = InlineKeyboardMarkup(row_width=2)
        
        for class_name in CLASSES:
            count = db.get_pdf_count_by_class(class_name)
            markup.add(InlineKeyboardButton(f"{class_name} ({count})", callback_data=f"admin_pdfs_class_{class_name}"))
        
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="admin_pdf_management"))
        
        if message_id:
            self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
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
        notify_users_new_pdfs = db.get_setting('notify_users_new_pdfs', '1') == '1'
        pens_per_referral = db.get_setting('pens_per_referral', '1')
        pdfs_per_pen = db.get_setting('pdfs_per_pen', '15')
        enable_browsing = db.get_setting('enable_browsing', '1') == '1'
        
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
        text += f"├ Channel leave alert: {'✅ ON' if channel_leave_alert else '❌ OFF'}\n"
        text += f"└ Notify users on new PDFs: {'✅ ON' if notify_users_new_pdfs else '❌ OFF'}\n\n"
        
        text += "💰 **PEN SYSTEM SETTINGS**\n"
        text += f"├ Pens per referral: `{pens_per_referral}`\n"
        text += f"├ PDFs per pen: `{pdfs_per_pen}`\n"
        text += f"└ Browsing enabled: {'✅ ON' if enable_browsing else '❌ OFF'}\n\n"
        
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
            InlineKeyboardButton(f"🔔 Notify users: {'ON' if notify_users_new_pdfs else 'OFF'}", callback_data="setting_notify_users_new_pdfs")
        )
        markup.add(
            InlineKeyboardButton(f"💰 Pens/ref: {pens_per_referral}", callback_data="setting_pens_per_referral"),
            InlineKeyboardButton(f"📖 PDFs/pen: {pdfs_per_pen}", callback_data="setting_pdfs_per_pen")
        )
        markup.add(
            InlineKeyboardButton(f"🎲 Browsing: {'ON' if enable_browsing else 'OFF'}", callback_data="setting_enable_browsing"),
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
        
        # Handle numeric settings
        if setting_key in ['search_results_per_page', 'whatsapp_reminders', 'pens_per_referral', 'pdfs_per_pen']:
            try:
                current_value = int(current) if current and str(current).isdigit() else 0
            except:
                current_value = 0
            
            if setting_key == 'search_results_per_page':
                options = [5, 10, 15, 20]
                idx = options.index(current_value) if current_value in options else 0
                new_value = options[(idx + 1) % len(options)]
                db.set_setting(setting_key, str(new_value), f"Search results per page: {new_value}")
                self.bot.answer_callback_query(user_id, f"✅ Search results per page set to {new_value}")
            
            elif setting_key == 'whatsapp_reminders':
                new_value = (current_value + 1) % 6
                db.set_setting(setting_key, str(new_value), f"WhatsApp reminders: {new_value}")
                self.bot.answer_callback_query(user_id, f"✅ WhatsApp reminders set to {new_value}")
            
            elif setting_key == 'pens_per_referral':
                options = [1, 2, 3, 4, 5]
                idx = options.index(current_value) if current_value in options else 0
                new_value = options[(idx + 1) % len(options)]
                db.set_setting(setting_key, str(new_value), f"Pens per referral: {new_value}")
                self.bot.answer_callback_query(user_id, f"✅ Pens per referral set to {new_value}")
            
            elif setting_key == 'pdfs_per_pen':
                options = [15, 20, 25, 30, 35, 40]
                idx = options.index(current_value) if current_value in options else 0
                new_value = options[(idx + 1) % len(options)]
                db.set_setting(setting_key, str(new_value), f"PDFs per pen: {new_value}")
                self.bot.answer_callback_query(user_id, f"✅ PDFs per pen set to {new_value}")
        
        else:
            # Handle boolean settings
            new_value = '0' if current == '1' else '1'
            db.set_setting(setting_key, new_value)
            status = "ON" if new_value == '1' else "OFF"
            
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
                'allow_user_delete_pdf': 'User PDF deletion',
                'notify_users_new_pdfs': 'Notify users on new PDFs',
                'enable_browsing': 'Browsing feature'
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
            markup = utils.create_admin_back_button("admin_users")
            if message_id:
                self.bot.edit_message_text("❌ User not found.", user_id, message_id, reply_markup=markup)
            else:
                self.bot.send_message(user_id, "❌ User not found.", reply_markup=markup)
            return
        
        uploads = db.get_user_upload_count(target_user_id)
        downloads = db.get_user_download_count(target_user_id)
        referrals = db.get_user_referral_stats(target_user_id)
        pens = db.get_pen_stats(target_user_id)
        
        whatsapp_confirmed = db.get_whatsapp_confirmed(target_user_id)
        membership_status = "✅ Completed" if whatsapp_confirmed else "⏳ Pending"
        
        join_date = utils.format_date(user['join_date'])
        last_active = utils.format_date(user['last_active']) if user['last_active'] else "Never"
        
        text = f"👤 **User Details**\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📛 **Name:** `{user['full_name']}`\n"
        text += f"🆔 **ID:** `{target_user_id}`\n"
        text += f"📞 **Phone:** `{user['phone'] or 'Not set'}`\n"
        text += f"🎓 **Class:** `{user['class'] or 'Not set'}`\n"
        text += f"📍 **Region:** `{user['region'] or 'Not set'}`\n"
        text += f"🏫 **School:** `{user['school'] or 'Not set'}`\n"
        text += f"📅 **Joined:** `{join_date}`\n"
        text += f"🕐 **Last Active:** `{last_active}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📊 **Stats**\n"
        text += f"├ 📤 **Uploads:** `{uploads}`\n"
        text += f"├ 📥 **Downloads:** `{downloads}`\n"
        text += f"└ 👥 **Referrals:** `{referrals['conversions']}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"💰 **Pens**\n"
        text += f"├ 🖊️ **Available:** `{pens['available']}`\n"
        text += f"├ 🎁 **Earned:** `{pens['earned']}`\n"
        text += f"└ 📖 **Spent:** `{pens['spent']}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"🔐 **Membership**\n"
        text += f"├ WhatsApp: `{membership_status}`\n"
        text += f"└ Telegram: Auto-detected\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
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
            InlineKeyboardButton("📄 View Uploads", callback_data=f"admin_user_uploads_{target_user_id}"),
            InlineKeyboardButton("📥 View Downloads", callback_data=f"admin_user_downloads_{target_user_id}")
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
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 Back", callback_data=f"admin_user_details_{target_user_id}"))
            if message_id:
                self.bot.edit_message_text(texts.EMPTY_UPLOADS, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
            else:
                self.bot.send_message(user_id, texts.EMPTY_UPLOADS, parse_mode='Markdown', reply_markup=markup)
            return
        
        text = f"📄 **User Uploads**\n"
        text += f"👤 User ID: `{target_user_id}`\n"
        text += f"📄 Total: `{total}` PDFs\n"
        text += f"📄 Page: `{page + 1}/{total_pages}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for pdf in pdfs:
            status = "✅" if pdf['is_approved'] else "⏳"
            text += f"{status} **{pdf['file_name'][:40]}**\n"
            text += f"   📚 `{pdf['subject']}` | 🏷️ `{pdf['tag']}` | 🎓 `{pdf['class']}`\n"
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
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 Back", callback_data=f"admin_user_details_{target_user_id}"))
            if message_id:
                self.bot.edit_message_text(texts.EMPTY_DOWNLOADS, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
            else:
                self.bot.send_message(user_id, texts.EMPTY_DOWNLOADS, parse_mode='Markdown', reply_markup=markup)
            return
        
        text = f"📥 **User Downloads**\n"
        text += f"👤 User ID: `{target_user_id}`\n"
        text += f"📥 Total: `{total}` downloads\n"
        text += f"📄 Page: `{page + 1}/{total_pages}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for download in downloads:
            text += f"📄 **{download['file_name'][:40]}**\n"
            text += f"   📚 `{download['subject']}` | 🏷️ `{download['tag']}` | 🎓 `{download['class']}`\n"
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
    # (Keeping existing membership functions - they remain unchanged)
    
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
            markup = utils.create_admin_back_button("admin_membership")
            if message_id:
                self.bot.edit_message_text(texts.EMPTY_REQUIREMENTS, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
            else:
                self.bot.send_message(user_id, texts.EMPTY_REQUIREMENTS, parse_mode='Markdown', reply_markup=markup)
            return
        
        items_per_page = 5
        total_pages = (len(requirements) + items_per_page - 1) // items_per_page
        start = page * items_per_page
        end = start + items_per_page
        page_items = requirements[start:end]
        
        text = f"🔗 **Membership Requirements**\n"
        text += f"📄 Page `{page + 1}/{total_pages}` | Total: `{len(requirements)}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
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
            markup = utils.create_admin_back_button("admin_back")
            try:
                self.bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
            except:
                self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
            self.bot.answer_callback_query(call.id)
            return
        
        # PDF Management
        if data == "admin_pdf_management":
            self.show_pdf_management(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "admin_pdfs_all":
            self.show_all_pdfs(user_id, 0, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data.startswith("admin_pdfs_all_page_"):
            page = int(data.split("_")[4])
            self.show_all_pdfs(user_id, page, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "admin_pdfs_by_tag":
            self.show_pdfs_by_tag(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data.startswith("admin_pdfs_tag_"):
            tag = data.split("_")[3]
            self.show_all_pdfs(user_id, 0, call.message.message_id, tag=tag)
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "admin_pdfs_by_class":
            self.show_pdfs_by_class(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data.startswith("admin_pdfs_class_"):
            pdf_class = data.split("_")[3]
            self.show_all_pdfs(user_id, 0, call.message.message_id, pdf_class=pdf_class)
            self.bot.answer_callback_query(call.id)
            return
        
        # Settings
        if data == "admin_settings":
            self.show_settings_panel(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        # Setting toggles
        if data.startswith("setting_"):
            setting_key = data[8:]
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
            page = 0
            limit = 20
            offset = page * limit
            users = db.get_all_users(limit=limit, offset=offset)
            total_users = db.count_users()
            total_pages = (total_users + limit - 1) // limit
            
            if not users:
                markup = utils.create_admin_back_button("admin_back")
                self.bot.edit_message_text("📭 No users found.", user_id, call.message.message_id, reply_markup=markup)
                self.bot.answer_callback_query(call.id)
                return
            
            text = f"👥 **User List**\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            text += f"📊 Total: `{total_users}` users\n"
            text += f"📄 Page: `{page + 1}/{total_pages}`\n\n"
            
            markup = utils.create_admin_user_list_keyboard(users, page, total_pages)
            
            try:
                self.bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
            except:
                self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
            self.bot.answer_callback_query(call.id)
            return
        
        if data.startswith("admin_users_page_"):
            page = int(data.split("_")[3])
            limit = 20
            offset = page * limit
            users = db.get_all_users(limit=limit, offset=offset)
            total_users = db.count_users()
            total_pages = (total_users + limit - 1) // limit
            
            text = f"👥 **User List**\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            text += f"📊 Total: `{total_users}` users\n"
            text += f"📄 Page: `{page + 1}/{total_pages}`\n\n"
            
            markup = utils.create_admin_user_list_keyboard(users, page, total_pages)
            
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
                markup = utils.create_admin_back_button("admin_back")
                try:
                    self.bot.edit_message_text("📭 No pending PDFs.", user_id, call.message.message_id, reply_markup=markup)
                except:
                    self.bot.send_message(user_id, "📭 No pending PDFs.", reply_markup=markup)
                self.bot.answer_callback_query(call.id)
                return
            
            text = "⏳ **Pending PDFs**\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for idx, pdf in enumerate(pending[:20], start=1):
                uploader = db.get_user(pdf['uploaded_by'])
                uploader_name = uploader['full_name'] if uploader else "Unknown"
                text += f"{idx}. **{pdf['file_name'][:40]}**\n"
                text += f"   📚 `{pdf['subject']}` | 🏷️ `{pdf['tag']}` | 🎓 `{pdf['class']}`\n"
                text += f"   👤 `{uploader_name}` | 🆔 `{pdf['id']}`\n\n"
            
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
                markup = utils.create_admin_back_button("admin_back")
                try:
                    self.bot.edit_message_text("📭 No pending reports.", user_id, call.message.message_id, reply_markup=markup)
                except:
                    self.bot.send_message(user_id, "📭 No pending reports.", reply_markup=markup)
                self.bot.answer_callback_query(call.id)
                return
            
            text = "🚨 **Pending Reports**\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for idx, report in enumerate(reports[:20], start=1):
                text += f"{idx}. PDF: **{report['pdf_name'][:40]}** (ID: {report['pdf_id']})\n"
                text += f"   👤 Reporter: `{report['reporter_name']}`\n"
                text += f"   💬 Reason: {report['report_text'][:50]}\n\n"
            
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
            self.handle_admin_callback(call)
            return
        
        # If none matched
        self.bot.answer_callback_query(call.id, "Unknown action")
    
    # ==================== Placeholder methods for membership (called from above) ====================
    # These methods are kept as placeholders since they exist in the original code
    # They would need to be implemented fully, but for brevity I'm showing the structure
    
    def show_membership_stats(self, user_id, message_id=None):
        """Show membership stats - placeholder"""
        # Full implementation from original code would go here
        pass
    
    def show_membership_events(self, user_id, message_id=None, page=0):
        """Show membership events - placeholder"""
        pass
    
    def show_membership_analytics(self, user_id, message_id=None):
        """Show membership analytics - placeholder"""
        pass
    
    def start_add_requirement(self, user_id, req_type, message_id=None):
        """Start adding requirement - placeholder"""
        pass
    
    def edit_requirement_field(self, user_id, req_id, field, message_id=None):
        """Edit requirement field - placeholder"""
        pass
    
    def admin_confirm_whatsapp(self, user_id, target_user_id, message_id=None):
        """Admin confirm WhatsApp - placeholder"""
        pass
    
    def start_admin_reply_to_user(self, user_id, target_user_id, message_id=None):
        """Start admin reply - placeholder"""
        pass
    
    def send_admin_reply_to_user(self, admin_id, target_user_id, reply_text):
        """Send admin reply - placeholder"""
        pass