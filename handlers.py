# telegram_pdf_bot/handlers.py
# All message and callback handlers - Class-based structure with fixed membership

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from config import TOKEN, ADMIN_IDS, TAGS, TAGS_REQUIRING_YEAR, YEARS, CLASSES, BOT_USERNAME, REQUIRED_CHANNEL, MAX_FILE_SIZE, DEBUG, ADMIN_WHATSAPP
import database as db
import texts
import utils
import pytz
import sqlite3
import json
from datetime import datetime, timedelta
from utils import get_current_time


class Handlers:
    """Main handlers class for Ardayda Bot"""
    
    def __init__(self, bot):
        """Initialize handlers with bot instance"""
        self.bot = bot
        self.admin_instance = None  # Will be set later to avoid circular import
        
        if DEBUG:
            print("🤖 Initializing Ardayda Bot handlers...")
            print(f"✅ Bot token loaded: {TOKEN[:10]}...")
            print(f"✅ Admin IDs: {ADMIN_IDS}")
            print(f"✅ Debug mode: ON")
        
        # Register all handlers
        self.register_handlers()
    
    def set_admin(self, admin_instance):
        """Set admin instance to avoid circular import"""
        self.admin_instance = admin_instance
    
    def register_handlers(self):
        """Register all message and callback handlers with decorators"""
        
        # ==================== Command Handlers ====================
        
        @self.bot.message_handler(commands=['restore'])
        def restore_command(message):
            self.restore_command(message)
        
        @self.bot.message_handler(commands=['start'])
        def start_command(message):
            self.start_command(message)
        
        @self.bot.message_handler(content_types=['contact'])
        def handle_contact(message):
            self.handle_contact(message)
        
        @self.bot.message_handler(content_types=['document'])
        def handle_document(message):
            self.handle_document(message)
        
        @self.bot.message_handler(func=lambda message: True)
        def handle_messages(message):
            self.handle_messages(message)
        
        # ==================== Callback Handler ====================
        
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callbacks(call):
            self.handle_callbacks(call)
    
    # ==================== Helper Functions ====================
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        return user_id in ADMIN_IDS or (db.get_user(user_id) and db.get_user(user_id)['is_admin'])
    
    def get_user_or_none(self, user_id):
        """Get user or None if banned"""
        user = db.get_user(user_id)
        if user and user['is_banned']:
            self.bot.send_message(user_id, texts.ACCOUNT_SUSPENDED)
            return None
        return user
    
    def show_main_menu(self, user_id):
        """Send the main menu to a registered user."""
        user = db.get_user(user_id)
        if user:
            if DEBUG:
                print(f"📱 Showing main menu to user {user_id} (admin: {user['is_admin']})")
            self.bot.send_message(
                user_id, 
                texts.HOME_WELCOME.format(name=user['full_name'].split()[0] if user['full_name'] else "User"),
                parse_mode='Markdown', 
                reply_markup=utils.create_main_menu_keyboard(user_id)
            )
        else:
            self.bot.send_message(
                user_id, 
                texts.HOME_WELCOME.format(name="User"),
                parse_mode='Markdown', 
                reply_markup=utils.create_main_menu_keyboard(user_id)
            )
    
    # ==================== New Membership System Methods ====================
    
    def get_all_membership_status(self, user_id):
        """Get status of all membership requirements (Telegram auto-detected)"""
        requirements = db.get_requirements(active_only=True)
        
        if not requirements:
            return {
                'telegram': [],
                'whatsapp': [],
                'telegram_joined': 0,
                'whatsapp_joined': 0,
                'total_telegram': 0,
                'total_whatsapp': 0,
                'total_joined': 0,
                'total_required': 0,
                'all_joined': True
            }
        
        telegram_reqs = []
        whatsapp_reqs = []
        telegram_joined = 0
        whatsapp_joined = 0
        
        for req in requirements:
            if req['type'] == 'telegram':
                is_member = utils.is_telegram_member(self.bot, user_id, req['link'])
                if is_member:
                    telegram_joined += 1
                telegram_reqs.append({
                    'id': req['id'],
                    'name': req['name'],
                    'link': req['link'],
                    'is_member': is_member,
                    'description': req['description'] if req['description'] else None
                })
            else:  # whatsapp
                is_verified = db.get_whatsapp_confirmed(user_id)
                whatsapp_reqs.append({
                    'id': req['id'],
                    'name': req['name'],
                    'link': req['link'],
                    'is_member': is_verified,
                    'description': req['description'] if req['description'] else None
                })
                if is_verified:
                    whatsapp_joined += 1
        
        total_telegram = len(telegram_reqs)
        total_whatsapp = len(whatsapp_reqs)
        total_joined = telegram_joined + whatsapp_joined
        total_required = total_telegram + total_whatsapp
        
        return {
            'telegram': telegram_reqs,
            'whatsapp': whatsapp_reqs,
            'telegram_joined': telegram_joined,
            'whatsapp_joined': whatsapp_joined,
            'total_telegram': total_telegram,
            'total_whatsapp': total_whatsapp,
            'total_joined': total_joined,
            'total_required': total_required,
            'all_joined': (total_joined == total_required and total_required > 0) or total_required == 0
        }
    
    def format_membership_message(self, status):
        """Format the membership requirements message"""
        if status['total_required'] == 0:
            return "✅ No membership requirements. You have full access!"
        
        text = "🔐 **MEMBERSHIP REQUIREMENTS**\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Progress bar
        if status['total_required'] > 0:
            percent = int((status['total_joined'] / status['total_required']) * 100)
            bar_length = 10
            filled = int(bar_length * percent / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            text += f"**Progress:** `{bar}` {status['total_joined']}/{status['total_required']} ({percent}%)\n\n"
        
        # Telegram Channels
        if status['telegram']:
            text += "📢 **TELEGRAM CHANNELS/GROUPS** (Auto-detected)\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for req in status['telegram']:
                if req['is_member']:
                    text += f"✅ **{req['name']}** - Joined\n"
                else:
                    text += f"❌ **{req['name']}** - Not joined\n"
                    text += f"   🔗 `{req['link']}`\n"
            text += "\n"
        
        # WhatsApp Groups
        if status['whatsapp']:
            text += "💬 **WHATSAPP GROUPS** (Confirm after joining)\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for req in status['whatsapp']:
                if req['is_member']:
                    text += f"✅ **{req['name']}** - Confirmed\n"
                else:
                    text += f"❌ **{req['name']}** - Not confirmed\n"
                    text += f"   🔗 `{req['link']}`\n"
            text += "\n"
        
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        if status['all_joined']:
            text += "🎉 **Congratulations!** You've joined all required communities!\n"
            text += "Click the button below to continue to the main menu.\n\n"
        else:
            text += "⚠️ **Please join all required channels/groups above** to access the bot.\n"
            text += "For WhatsApp groups, click 'Confirm' after joining.\n\n"
        
        return text
    
    def create_membership_keyboard(self, status):
        """Create keyboard for membership requirements"""
        markup = InlineKeyboardMarkup(row_width=2)
        
        # Add buttons for Telegram channels (auto-detect, just join links)
        for req in status['telegram']:
            if not req['is_member']:
                link = req['link']
                if link.startswith('@'):
                    link = f"https://t.me/{link[1:]}"
                elif not link.startswith('http'):
                    link = f"https://t.me/{link}"
                
                markup.add(InlineKeyboardButton(
                    f"📢 Join {req['name'][:20]}",
                    url=link
                ))
        
        # Add buttons for WhatsApp groups
        for req in status['whatsapp']:
            if not req['is_member']:
                markup.add(
                    InlineKeyboardButton(f"💬 Join {req['name'][:15]}", url=req['link']),
                    InlineKeyboardButton(f"✅ Confirm {req['name'][:10]}", callback_data=f"confirm_whatsapp_{req['id']}")
                )
        
        # Refresh button
        markup.add(InlineKeyboardButton("🔄 Refresh Status", callback_data="refresh_membership"))
        
        # Continue button if all joined
        if status['all_joined'] and status['total_required'] > 0:
            markup.add(InlineKeyboardButton("🎉 Continue to Main Menu", callback_data="membership_complete"))
        
        return markup
    
    def show_membership_requirements(self, user_id, message_id=None):
        """Show or update membership requirements message"""
        status = self.get_all_membership_status(user_id)
        text = self.format_membership_message(status)
        markup = self.create_membership_keyboard(status)
        
        stored_message_id = db.get_user_membership_message(user_id)
        
        # Try to edit existing message
        if stored_message_id:
            try:
                self.bot.edit_message_text(
                    text, user_id, stored_message_id,
                    parse_mode='Markdown', reply_markup=markup
                )
                return
            except Exception as e:
                if DEBUG:
                    print(f"   Could not edit message, sending new: {e}")
        
        # Send new message
        msg = self.bot.send_message(
            user_id, text,
            parse_mode='Markdown', reply_markup=markup
        )
        db.set_user_membership_message(user_id, msg.message_id)
    
    def complete_membership(self, user_id):
        """Complete membership and show welcome message"""
        # Check for pending PDF after membership
        state, pending_data = db.get_user_state(user_id)
        pending_pdf = None
        if state == 'pending_pdf_after_membership' and pending_data:
            pending_pdf = pending_data.get('pdf_id')
            db.clear_user_state(user_id)
        
        # Delete membership message
        stored_message_id = db.get_user_membership_message(user_id)
        if stored_message_id:
            try:
                self.bot.delete_message(user_id, stored_message_id)
            except:
                pass
        
        db.set_user_membership_message(user_id, None)
        
        # Show welcome message
        user = db.get_user(user_id)
        welcome_text = (
            f"🎉 **WELCOME TO ARDAYDA BOT!** 🎉\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Thank you for joining all our communities, **{user['full_name'].split()[0] if user['full_name'] else 'User'}**!\n\n"
            f"✅ You now have full access to:\n"
            f"├ 📤 Upload PDFs\n"
            f"├ 🔍 Search Educational Materials\n"
            f"├ 👤 Track Your Profile\n"
            f"└ 🔗 Share Referral Links\n\n"
            f"Let's get started!"
        )
        
        self.bot.send_message(
            user_id, welcome_text,
            parse_mode='Markdown',
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )
        
        # Show pending PDF if any
        if pending_pdf:
            self.handle_pdf_share(user_id, pending_pdf)
        
        if DEBUG:
            print(f"🎉 Membership completed for user {user_id}")
    
    def check_all_memberships(self, user_id):
        """Check if user meets all membership requirements and update status"""
        requirements = db.get_requirements(active_only=True)
        
        if not requirements:
            return True, None
        
        all_met = True
        missing_req = None
        status = self.get_all_membership_status(user_id)
        
        if status['all_joined']:
            return True, None
        
        for req in requirements:
            if req['type'] == 'telegram':
                is_member = utils.is_telegram_member(self.bot, user_id, req['link'])
                db.record_membership(user_id, req['id'], is_member)
                
                if not is_member:
                    all_met = False
                    missing_req = req
                    break
            else:
                is_confirmed = db.get_whatsapp_confirmed(user_id)
                if not is_confirmed:
                    all_met = False
                    missing_req = req
                    break
        
        return all_met, missing_req
    
    def require_membership(self, func):
        """Decorator to check membership AFTER user is registered"""
        def wrapper(message_or_call, *args, **kwargs):
            if hasattr(message_or_call, 'from_user'):
                user_id = message_or_call.from_user.id
            else:
                user_id = message_or_call.message.from_user.id
            
            user = db.get_user(user_id)
            if not user:
                return func(message_or_call, *args, **kwargs)
            
            all_met, missing = self.check_all_memberships(user_id)
            
            if not all_met:
                if DEBUG:
                    print(f"🔒 User {user_id} missing membership")
                self.show_membership_requirements(user_id)
                return
            
            return func(message_or_call, *args, **kwargs)
        
        return wrapper
    
    def send_membership_required_message(self, user_id, requirement):
        """Legacy method - replaced by show_membership_requirements"""
        self.show_membership_requirements(user_id)
    
    def notify_referrer(self, referrer_id, new_user_id, new_user_name):
        """Notify the referrer that someone used their link"""
        referrer = db.get_user(referrer_id)
        if not referrer:
            return
        
        stats = db.get_user_referral_stats(referrer_id)
        total = stats['conversions']
        
        try:
            self.bot.send_message(
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
                self.bot.send_message(
                    admin_id,
                    texts.ADMIN_REFERRAL_NOTIFICATION.format(
                        referrer_name=referrer['full_name'],
                        referrer_id=referrer_id,
                        new_user_name=new_user_name,
                        new_user_id=new_user_id,
                        date=get_current_time().strftime("%Y-%m-%d %I:%M %p"),
                        total=total
                    ),
                    parse_mode='Markdown'
                )
            except:
                pass
    
    # ==================== Command Handlers ====================
    
    def restore_command(self, message):
        user_id = message.from_user.id
        db.clear_user_state(user_id)
        
        if DEBUG:
            print(f"🔄 User {user_id} used /restore - state cleared")
        
        self.bot.send_message(
            user_id,
            "✅ **State Restored!**\n\nYou've been returned to the main menu.",
            parse_mode='Markdown',
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )
    
    def start_command(self, message):
        user_id = message.from_user.id
        args = message.text.split()
        start_param = args[1] if len(args) > 1 else None
        
        if DEBUG:
            print(f"🚀 /start from user {user_id}, param: {start_param}")

        user = db.get_user(user_id)
        
        if user and not user['is_banned']:
            if DEBUG:
                print(f"👤 Existing user {user_id} logged in")
            
            all_met, missing = self.check_all_memberships(user_id)
            if not all_met:
                self.show_membership_requirements(user_id)
                return
            
            if start_param and start_param.startswith('pdf_'):
                pdf_id = start_param.split('_')[1]
                self.handle_pdf_share(user_id, pdf_id)
            elif start_param and start_param.startswith('ref_'):
                self.bot.send_message(
                    user_id, 
                    "✅ You are already registered!\n\nUse the menu below to explore.",
                    reply_markup=utils.create_main_menu_keyboard(user_id)
                )
            else:
                self.show_main_menu(user_id)
            return

        # New user registration - handle both ref and pdf links as referrals
        referred_by = None
        pending_pdf = None

        if start_param:
            if start_param.startswith('ref_'):
                referrer_id = start_param.split('_')[1]
                referrer = db.get_user(referrer_id)
                if referrer and referrer['user_id'] != user_id:
                    referred_by = referrer['user_id']
                    self.bot.send_message(referrer_id, "**🚸 Someone Used Your Referral Link**", parse_mode='Markdown')
                    if DEBUG:
                        print(f"🔗 New user {user_id} referred by {referrer_id}")
            
            elif start_param.startswith('pdf_'):
                # PDF share link - extract PDF ID and check for referral in extended format
                parts = start_param.split('_')
                pending_pdf = parts[1]
                
                # Check if referral is embedded (format: pdf_123_ref_456)
                if len(parts) >= 4 and parts[2] == 'ref':
                    referrer_id = parts[3]
                    referrer = db.get_user(referrer_id)
                    if referrer and referrer['user_id'] != user_id:
                        referred_by = referrer['user_id']
                        self.bot.send_message(referrer_id, "**🚸 Someone Used Your PDF Share Link as Referral!**", parse_mode='Markdown')
                        if DEBUG:
                            print(f"🔗 New user {user_id} referred by {referrer_id} via PDF link")

        db.set_user_state(user_id, 'register', {
            'step': 'name',
            'referred_by': referred_by,
            'pending_pdf': pending_pdf
        })
        
        self.bot.send_message(
            user_id, 
            texts.REG_NAME, 
            parse_mode='Markdown'
        )
        
        if DEBUG:
            print(f"📝 New registration started for user {user_id}")
    
    def handle_contact(self, message):
        user_id = message.from_user.id
        current_state, data = db.get_user_state(user_id)
        
        if current_state == 'register' and data and data.get('step') == 'phone':
            phone = message.contact.phone_number
            data['phone'] = phone
            data['step'] = 'region'
            db.set_user_state(user_id, 'register', data)
            
            if DEBUG:
                print(f"📞 Phone received for user {user_id}: {phone}")
            
            self.bot.send_message(
                user_id, 
                texts.REG_REGION, 
                parse_mode='Markdown',
                reply_markup=utils.create_region_keyboard()
            )
    
    def handle_document(self, message):
        user_id = message.from_user.id
        user = db.get_user(user_id)
        
        if user and user['is_banned']:
            self.bot.send_message(user_id, texts.ACCOUNT_SUSPENDED)
            return
        
        if not user:
            self.bot.send_message(user_id, "❌ Please register first using /start")
            return
        
        all_met, missing = self.check_all_memberships(user_id)
        if not all_met:
            self.show_membership_requirements(user_id)
            return
        
        current_state, data = db.get_user_state(user_id)
        
        if current_state == 'upload' and data and data.get('step') == 'waiting_for_file':
            self.handle_upload_pdf(message, data)
        else:
            if message.document.mime_type != 'application/pdf':
                self.bot.send_message(
                    user_id,
                    "❌ Please send a valid **PDF document**.\n\nSend /cancel to cancel.",
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
            
            self.bot.send_message(
                user_id,
                f"📄 **Document Received:** `{message.document.file_name}`\n\n"
                f"Do you want to upload this as a PDF?\n\n"
                f"📦 Size: {utils.format_file_size(message.document.file_size)}",
                parse_mode='Markdown',
                reply_markup=markup
            )
    
    def handle_messages(self, message):
        user_id = message.from_user.id
        user = db.get_user(user_id)
        
        if user and user['is_banned']:
            self.bot.send_message(user_id, texts.ACCOUNT_SUSPENDED)
            return
        
        if user and not user['is_banned']:
            db.update_user_activity(user_id)

        current_state, data = db.get_user_state(user_id)
        
        if DEBUG:
            print(f"📨 Message from {user_id}: {message.text if message.text else '[non-text]'}, state={current_state}")
        
        # Handle admin flows
        if current_state == 'add_requirement' and self.admin_instance:
            self.admin_instance.process_add_requirement(user_id, message)
            return
        
        if current_state == 'edit_requirement' and self.admin_instance:
            self.admin_instance.process_edit_requirement(user_id, message)
            return
        
        # Handle reply to admin
        if current_state == 'reply_to_admin':
            if message.text and message.text.lower() == texts.BUTTON_CANCEL.lower():
                db.clear_user_state(user_id)
                self.bot.send_message(
                    user_id, 
                    texts.CANCELLED, 
                    parse_mode='Markdown',
                    reply_markup=utils.create_main_menu_keyboard(user_id)
                )
                return
            
            admin_id = data.get('admin_id')
            if admin_id:
                if self.send_reply_to_admin(user_id, admin_id, message.text):
                    db.clear_user_state(user_id)
                    self.bot.send_message(
                        user_id,
                        "✅ **Reply Sent!**\n\nYour message has been sent to the admin.\n\nThey will respond shortly.",
                        parse_mode='Markdown',
                        reply_markup=utils.create_main_menu_keyboard(user_id)
                    )
                else:
                    self.bot.send_message(
                        user_id,
                        "❌ **Failed to Send**\n\nCould not send your reply. Please try again later.",
                        parse_mode='Markdown',
                        reply_markup=utils.create_main_menu_keyboard(user_id)
                    )
            return
  
        # Handle admin reply to user
        if current_state == 'admin_reply_user':
            if message.text and message.text.lower() == texts.BUTTON_CANCEL.lower():
                db.clear_user_state(user_id)
                self.bot.send_message(
                    user_id, 
                    texts.CANCELLED, 
                    parse_mode='Markdown',
                    reply_markup=utils.create_main_menu_keyboard(user_id)
                )
                return
            
            target_user_id = data.get('target_user_id')
            if target_user_id and self.admin_instance:
                if self.admin_instance.send_admin_reply_to_user(user_id, target_user_id, message.text):
                    db.clear_user_state(user_id)
                    self.bot.send_message(
                        user_id,
                        f"✅ **Reply Sent!**\n\nYour reply has been sent to user `{target_user_id}`.",
                        parse_mode='Markdown',
                        reply_markup=utils.create_main_menu_keyboard(user_id)
                    )
                else:
                    self.bot.send_message(
                        user_id,
                        "❌ **Failed to Send**\n\nCould not send your reply.",
                        parse_mode='Markdown',
                        reply_markup=utils.create_main_menu_keyboard(user_id)
                    )
            return
        
        # Handle registration
        if current_state == 'register':
            self.handle_registration(message, data)
            return
        
        # Handle cancel
        if message.text and message.text.lower() == texts.BUTTON_CANCEL.lower():
            db.clear_user_state(user_id)
            self.bot.send_message(
                user_id, 
                texts.CANCELLED, 
                parse_mode='Markdown',
                reply_markup=utils.create_main_menu_keyboard(user_id)
            )
            return
        
        # For registered users, check membership
        if user and not user['is_banned']:
            all_met, missing = self.check_all_memberships(user_id)
            if not all_met:
                self.show_membership_requirements(user_id)
                return
        
        # Handle other states
        if current_state == 'upload':
            if data and data.get('step') == 'waiting_for_file':
                if message.document and message.document.mime_type == 'application/pdf':
                    self.handle_upload_pdf(message, data)
                else:
                    self.bot.send_message(
                        user_id,
                        texts.UPLOAD_INVALID_FILE,
                        parse_mode='Markdown',
                        reply_markup=utils.create_cancel_keyboard()
                    )
            else:
                db.clear_user_state(user_id)
                self.bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard(user_id))
        
        elif current_state == 'search':
            self.handle_search_state(message, data)
        
        elif current_state == 'report':
            self.handle_report_state(message, data)
        
        elif current_state == 'admin_broadcast':
            self.handle_admin_broadcast(message, data)
        
        elif current_state == 'admin_sql':
            self.handle_admin_sql(message, data)
        
        else:
            # Main menu buttons
            if message.text == texts.BUTTON_UPLOAD:
                self.start_upload(user_id)
            elif message.text == texts.BUTTON_SEARCH:
                self.start_search(user_id)
            elif message.text == texts.BUTTON_PROFILE:
                self.show_profile(user_id)
            elif message.text == texts.BUTTON_HELP:
                self.show_help(user_id)
            elif message.text == texts.BUTTON_ADMIN and self.is_admin(user_id) and self.admin_instance:
                self.admin_instance.show_admin_panel(user_id)
            else:
                self.bot.send_message(
                    user_id, 
                    texts.UNKNOWN_INPUT, 
                    parse_mode='Markdown',
                    reply_markup=utils.create_main_menu_keyboard(user_id)
                )
    
    # ==================== Registration Flow ====================
    
    def handle_registration(self, message, data):
        user_id = message.from_user.id
        step = data.get('step')
        
        if step == 'name':
            full_name = message.text.strip()
            parts = full_name.split()
            if len(parts) < 2:
                self.bot.send_message(
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
            
            self.bot.send_message(
                user_id, 
                texts.REG_PHONE, 
                parse_mode='Markdown',
                reply_markup=markup
            )
        
        elif step == 'manual_region':
            self.handle_manual_region_input(message, data)
        
        elif step == 'manual_school':
            self.handle_manual_school_input(message, data)
        
        elif step == 'phone':
            phone = message.text.strip()
            if not any(c.isdigit() for c in phone) or len(phone) < 8:
                self.bot.send_message(
                    user_id, 
                    "❌ Invalid phone number. Please use the contact button or enter a valid number.",
                    reply_markup=utils.create_cancel_keyboard()
                )
                return
            
            data['phone'] = phone
            data['step'] = 'region'
            db.set_user_state(user_id, 'register', data)
            
            self.bot.send_message(
                user_id, 
                texts.REG_REGION, 
                parse_mode='Markdown',
                reply_markup=utils.create_region_keyboard()
            )
    
    def handle_manual_region_input(self, message, data):
        user_id = message.from_user.id
        region = message.text.strip()
        
        if region.lower() == texts.BUTTON_CANCEL.lower():
            db.clear_user_state(user_id)
            self.bot.send_message(
                user_id, 
                texts.CANCELLED, 
                parse_mode='Markdown',
                reply_markup=utils.create_main_menu_keyboard(user_id)
            )
            return
        
        if DEBUG:
            print(f"✏️ Manual region entered by {user_id}: {region}")
        
        location_info = f"📍 **Region:** `{region}`"
        
        for admin_id in ADMIN_IDS:
            try:
                self.bot.send_message(
                    admin_id, 
                    texts.ADMIN_MANUAL_ENTRY_NOTIFICATION.format(
                        entry_type="REGION",
                        user_name="New User (not registered)",
                        user_id=user_id,
                        user_phone=data.get('phone', 'Not provided'),
                        location_info=location_info,
                        date=get_current_time().strftime("%Y-%m-%d %I:%M %p")
                    ),
                    parse_mode='Markdown'
                )
            except:
                pass
        
        data['region'] = region
        data['step'] = 'school'
        data['schools_page'] = 0
        db.set_user_state(user_id, 'register', data)
        
        self.show_schools_page(user_id, region, 0)
    
    def handle_manual_school_input(self, message, data):
        user_id = message.from_user.id
        school = message.text.strip()
        region = data.get('region')
        
        if school.lower() == texts.BUTTON_CANCEL.lower():
            data['step'] = 'school'
            data['schools_page'] = 0
            db.set_user_state(user_id, 'register', data)
            self.show_schools_page(user_id, region, 0)
            return
        
        if DEBUG:
            print(f"✏️ Manual school entered by {user_id}: {school} in {region}")
        
        location_info = f"📍 **Region:** `{region}`\n\n🏫 **School:** `{school}`"
        
        for admin_id in ADMIN_IDS:
            try:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(
                    "👤 View User", 
                    callback_data=f"admin_user_details_{user_id}"
                ))
                
                self.bot.send_message(
                    admin_id, 
                    texts.ADMIN_MANUAL_ENTRY_NOTIFICATION.format(
                        entry_type="SCHOOL",
                        user_name="New User (not registered)",
                        user_id=user_id,
                        user_phone=data.get('phone', 'Not provided'),
                        location_info=location_info,
                        date=get_current_time().strftime("%Y-%m-%d %I:%M %p")
                    ),
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            except:
                pass
        
        data['school'] = school
        data['step'] = 'class'
        db.set_user_state(user_id, 'register', data)
        
        self.bot.send_message(
            user_id, 
            texts.REG_CLASS, 
            parse_mode='Markdown',
            reply_markup=utils.create_class_keyboard()
        )
    
    def show_schools_page(self, user_id, region, page, message_id=None):
        schools = texts.form_four_schools_by_region.get(region, [])
        
        if not schools:
            data = db.get_user_state(user_id)[1]
            data['step'] = 'manual_school'
            data['region'] = region
            db.set_user_state(user_id, 'register', data)
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
            
            self.bot.send_message(
                user_id,
                texts.MANUAL_SCHOOL_PROMPT.format(region=region),
                parse_mode='Markdown',
                reply_markup=markup
            )
            return
        
        markup, total_pages = utils.create_schools_keyboard(schools, region, page)
        
        if message_id:
            self.bot.edit_message_text(
                texts.REG_SCHOOL.format(region=region),
                user_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        else:
            self.bot.send_message(
                user_id,
                texts.REG_SCHOOL.format(region=region),
                parse_mode='Markdown',
                reply_markup=markup
            )
    
    # ==================== Registration Callback Functions ====================
    
    def handle_region_callback(self, call):
        user_id = call.from_user.id
        current_state, data = db.get_user_state(user_id)
        
        if current_state != 'register':
            self.bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
            return
        
        region = call.data.split('_')[1]
        
        if region not in texts.form_four_schools_by_region:
            data['step'] = 'manual_region'
            db.set_user_state(user_id, 'register', data)
            
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
            
            self.bot.edit_message_text(
                texts.MANUAL_REGION_PROMPT,
                user_id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
            self.bot.answer_callback_query(call.id)
            return
        
        if DEBUG:
            print(f"📍 Region selected by {user_id}: {region}")
        
        data['region'] = region
        data['step'] = 'school'
        data['schools_page'] = 0
        db.set_user_state(user_id, 'register', data)
        
        self.show_schools_page(user_id, region, 0, call.message.message_id)
        self.bot.answer_callback_query(call.id)
    
    def handle_schools_page_callback(self, call):
        user_id = call.from_user.id
        current_state, data = db.get_user_state(user_id)
        
        if current_state != 'register' or data.get('step') != 'school':
            self.bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
            return
        
        parts = call.data.split('_')
        region = parts[2]
        page = int(parts[3])
        data['schools_page'] = page
        db.set_user_state(user_id, 'register', data)
        
        self.show_schools_page(user_id, region, page, call.message.message_id)
        self.bot.answer_callback_query(call.id)
    
    def handle_manual_school_callback(self, call):
        user_id = call.from_user.id
        region = call.data.split('_')[2]
        current_state, data = db.get_user_state(user_id)
        
        if current_state != 'register' or data.get('step') != 'school':
            self.bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
            return
        
        if DEBUG:
            print(f"✏️ Manual school requested by {user_id} for region {region}")
        
        data['step'] = 'manual_school'
        data['region'] = region
        db.set_user_state(user_id, 'register', data)
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
        
        self.bot.edit_message_text(
            texts.MANUAL_SCHOOL_PROMPT.format(region=region),
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
        self.bot.answer_callback_query(call.id)
    
    def handle_manual_region_start(self, call):
        user_id = call.from_user.id
        current_state, data = db.get_user_state(user_id)
        
        if current_state != 'register':
            self.bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
            return
        
        data['step'] = 'manual_region'
        db.set_user_state(user_id, 'register', data)
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
        
        self.bot.edit_message_text(
            texts.MANUAL_REGION_PROMPT,
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
        self.bot.answer_callback_query(call.id)
    
    def handle_school_callback(self, call):
        user_id = call.from_user.id
        current_state, data = db.get_user_state(user_id)
        
        if current_state != 'register' or data.get('step') != 'school':
            self.bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
            return
        
        school = call.data.split('_', 1)[1]
        
        if DEBUG:
            print(f"🏫 School selected by {user_id}: {school}")
        
        data['school'] = school
        data['step'] = 'class'
        db.set_user_state(user_id, 'register', data)
        
        self.bot.edit_message_text(
            texts.REG_CLASS,
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=utils.create_class_keyboard()
        )
        self.bot.answer_callback_query(call.id)
    
    def handle_class_callback(self, call):
        user_id = call.from_user.id
        current_state, data = db.get_user_state(user_id)
        
        if current_state != 'register' or data.get('step') != 'class':
            self.bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
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
            self.notify_referrer(referred_by, user_id, data.get('name'))
        
        pending_pdf = data.get('pending_pdf')
        db.clear_user_state(user_id)
        
        self.bot.edit_message_text(
            texts.REG_SUCCESS,
            user_id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        
        # After registration, check membership requirements FIRST
        all_met, missing = self.check_all_memberships(user_id)
        
        if not all_met:
            # Store pending PDF to show after membership
            if pending_pdf:
                db.set_user_state(user_id, 'pending_pdf_after_membership', {'pdf_id': pending_pdf})
            self.show_membership_requirements(user_id)
        else:
            self.show_main_menu(user_id)
            if pending_pdf:
                self.handle_pdf_share(user_id, pending_pdf)
        
        self.bot.answer_callback_query(call.id)
    
    def handle_back_callback(self, call):
        user_id = call.from_user.id
        current_state, data = db.get_user_state(user_id)
        
        if current_state != 'register':
            self.bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
            return
        
        back_to = call.data.split('_')[1]
        
        if back_to == 'region':
            if DEBUG:
                print(f"🔙 User {user_id} went back to region selection")
            data['step'] = 'region'
            db.set_user_state(user_id, 'register', data)
            
            self.bot.edit_message_text(
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
            self.show_schools_page(user_id, region, 0, call.message.message_id)
        
        self.bot.answer_callback_query(call.id)
    
    # ==================== Upload Flow ====================
    
    def start_upload(self, user_id):
        user = db.get_user(user_id)
        if not user:
            self.bot.send_message(user_id, texts.NOT_REGISTERED)
            return
        
        if DEBUG:
            print(f"📤 Upload started by user {user_id}")
        
        db.set_user_state(user_id, 'upload', {'step': 'waiting_for_file'})
        
        self.bot.send_message(
            user_id,
            texts.UPLOAD_FILE_PROMPT,
            parse_mode='Markdown',
            reply_markup=utils.create_cancel_keyboard()
        )
    
    def handle_upload_pdf(self, message, data):
        user_id = message.from_user.id
        
        if not message.document or message.document.mime_type != 'application/pdf':
            self.bot.send_message(
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
        
        self.bot.send_message(
            user_id,
            texts.UPLOAD_RECEIVED.format(
                file_name=message.document.file_name,
                size=file_size_display
            ),
            parse_mode='Markdown'
        )
        
        self.ask_subject(user_id)
    
    def ask_subject(self, user_id):
        self.bot.send_message(
            user_id,
            texts.UPLOAD_SUBJECT,
            parse_mode='Markdown',
            reply_markup=utils.create_subject_keyboard(for_search=False)
        )
        
        if DEBUG:
            print(f"📚 Asked for subject from user {user_id}")
    
    def handle_subject_callback(self, call):
        user_id = call.from_user.id
        current_state, data = db.get_user_state(user_id)
        
        if current_state != 'upload' or data.get('step') != 'subject':
            self.bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
            return
        
        subject = call.data.split('_')[1]
        data['subject'] = subject
        data['step'] = 'tag'
        db.set_user_state(user_id, 'upload', data)
        
        if DEBUG:
            print(f"📚 Subject selected by {user_id}: {subject}")
        
        self.bot.edit_message_text(
            texts.UPLOAD_TAG,
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=utils.create_tag_keyboard()
        )
        self.bot.answer_callback_query(call.id)
    
    def handle_tag_callback(self, call):
        user_id = call.from_user.id
        current_state, data = db.get_user_state(user_id)
        
        if current_state != 'upload' or data.get('step') != 'tag':
            self.bot.answer_callback_query(call.id, texts.SESSION_EXPIRED)
            return
        
        tag = call.data.split('_')[1]
        
        if tag == 'skip':
            tag = None
        
        data['tag'] = tag
        data['step'] = 'finish'
        db.set_user_state(user_id, 'upload', data)
        
        if DEBUG:
            print(f"🏷️ Tag selected by {user_id}: {tag}")
        
        self.finish_upload(user_id, call.message.message_id)
        self.bot.answer_callback_query(call.id)
    
    def finish_upload(self, user_id, message_id=None):
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
            self.bot.send_message(user_id, texts.UPLOAD_FAILED, parse_mode='Markdown')
            db.clear_user_state(user_id)
            return
        
        # Check auto-approve setting
        auto_approve = db.get_setting('auto_approve_pdfs', '0') == '1'
        is_approved = 1 if auto_approve else 0
        
        pdf_id = db.add_pdf(
            file_id=file_id,
            file_name=file_name,
            user_id=user_id,
            subject=subject,
            tag=tag,
            exam_year=None
        )
        
        if auto_approve:
            db.approve_pdf(pdf_id)
        
        db.clear_user_state(user_id)
        
        if DEBUG:
            print(f"✅ PDF uploaded by {user_id}: {file_name} (ID: {pdf_id})")
        
        status = "✅ Approved" if auto_approve else "⏳ Pending Approval"
        msg = texts.UPLOAD_SUCCESS.format(
            file_name=file_name,
            subject=subject,
            tag=tag or "None",
            pdf_id=pdf_id
        ) + f"\n\n**Status:** {status}"
        
        self.bot.send_message(
            user_id,
            msg,
            parse_mode='Markdown',
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )
        
        # Notify admins if setting enabled
        notify_admins = db.get_setting('notify_admin_on_upload', '1') == '1'
        if notify_admins:
            for admin_id in ADMIN_IDS:
                try:
                    self.bot.send_message(
                        admin_id,
                        f"📄 **New PDF Upload**\n\n"
                        f"📄 **File:** `{file_name}`\n"
                        f"👤 **User:** `{user_id}`\n"
                        f"📚 **Subject:** `{subject}`\n"
                        f"🏷️ **Tag:** `{tag or 'None'}`\n"
                        f"🆔 **ID:** `{pdf_id}`\n"
                        f"✅ **Auto-approved:** {'Yes' if auto_approve else 'No'}",
                        parse_mode='Markdown'
                    )
                except:
                    pass
        
        if message_id:
            try:
                self.bot.edit_message_reply_markup(user_id, message_id, reply_markup=None)
            except:
                pass
    
    # ==================== Search Flow ====================
    
    def start_search(self, user_id):
        user = db.get_user(user_id)
        if not user:
            self.bot.send_message(user_id, texts.NOT_REGISTERED)
            return
        
        db.clear_user_state(user_id)
        db.set_user_state(user_id, 'search', {'step': 'subject'})
        
        if DEBUG:
            print(f"🔍 Search started by user {user_id}")
        
        self.bot.send_message(
            user_id,
            texts.SEARCH_START,
            parse_mode='Markdown',
            reply_markup=utils.create_subject_keyboard(for_search=True)
        )
    
    def handle_search_subject_callback(self, call):
        user_id = call.from_user.id
        subject = call.data.split('_')[2]
        
        current_state, data = db.get_user_state(user_id)
        
        if DEBUG:
            print(f"📚 Search subject callback - user: {user_id}, subject: {subject}, state: {current_state}")
        
        if current_state != 'search':
            self.bot.answer_callback_query(call.id, "Session expired. Please start a new search.", show_alert=True)
            return
        
        db.set_user_state(user_id, 'search', {'subject': subject, 'step': 'tag'})
        
        if DEBUG:
            print(f"   State updated: step=tag, subject={subject}")
        
        self.bot.edit_message_text(
            texts.SEARCH_SUBJECT_SELECTED.format(subject=subject),
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=utils.create_search_tag_keyboard()
        )
        self.bot.answer_callback_query(call.id)

    def handle_search_tag_callback(self, call):
        user_id = call.from_user.id
        current_state, data = db.get_user_state(user_id)
        
        if DEBUG:
            print(f"🏷️ Search tag callback - user: {user_id}, state: {current_state}, data: {data}")
        
        if current_state != 'search':
            self.bot.answer_callback_query(call.id, "Session expired. Please start a new search.", show_alert=True)
            return
        
        if not data or data.get('step') != 'tag':
            self.bot.answer_callback_query(call.id, "Please select a subject first.", show_alert=True)
            return
        
        tag = call.data.split('_')[2]
        if tag == 'skip':
            tag = None
        
        subject = data.get('subject')
        
        if DEBUG:
            print(f"   Subject: {subject}, Tag: {tag}")
        
        # Get results per page setting
        results_per_page = int(db.get_setting('search_results_per_page', '5'))
        
        db.set_user_state(user_id, 'search', {
            'subject': subject,
            'tag': tag,
            'step': 'results',
            'page': 0,
            'limit': results_per_page
        })
        
        self.show_search_results(user_id, call.message.message_id)
        self.bot.answer_callback_query(call.id)
    
    def show_search_results(self, user_id, message_id=None):
        current_state, data = db.get_user_state(user_id)
        
        if DEBUG:
            print(f"🔍 Showing search results - user: {user_id}, state: {current_state}, data: {data}")
        
        if not current_state or current_state != 'search':
            self.bot.send_message(
                user_id,
                "🔍 Please start a new search using the Search button.",
                parse_mode='Markdown',
                reply_markup=utils.create_main_menu_keyboard(user_id)
            )
            return
        
        if data.get('step') != 'results':
            self.bot.send_message(
                user_id,
                "Please select a subject and tag first.",
                parse_mode='Markdown'
            )
            self.start_search(user_id)
            return
        
        subject = data.get('subject')
        tag = data.get('tag')
        page = data.get('page', 0)
        limit = data.get('limit', 5)
        offset = page * limit
        
        if DEBUG:
            print(f"   Searching: subject={subject}, tag={tag}, page={page}, limit={limit}")
        
        total = db.count_pdfs_by_filters(subject=subject, tag=tag)
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        
        if total == 0:
            db.clear_user_state(user_id)
            self.bot.send_message(
                user_id,
                texts.SEARCH_NO_RESULTS,
                parse_mode='Markdown',
                reply_markup=utils.create_main_menu_keyboard(user_id)
            )
            return
        
        pdfs = db.get_pdfs_by_filters(subject=subject, tag=tag, limit=limit, offset=offset)
        
        # Check show uploader setting
        show_uploader = db.get_setting('show_uploader_in_search', '1') == '1'
        
        text = texts.SEARCH_RESULTS.format(
            subject=subject,
            tag=tag or "All",
            total=total,
            page=page + 1,
            total_pages=total_pages
        )
        
        for idx, pdf in enumerate(pdfs, start=1):
            emoji = utils.get_pdf_emoji(pdf['tag'])
            text += f"{emoji} **{pdf['file_name'][:40]}**\n"
            text += f"   📚 `{pdf['subject']}` | 🏷️ `{pdf['tag']}`\n"
            if show_uploader:
                uploader = db.get_user(pdf['uploaded_by'])
                uploader_name = uploader['full_name'] if uploader else "Unknown"
                text += f"   👤 `{uploader_name}`\n"
            text += f"   ❤️ `{pdf['like_count']}` likes | 📥 `{pdf['download_count']}` downloads\n"
            text += f"   🆔 `{pdf['id']}`\n\n"
        
        markup = InlineKeyboardMarkup(row_width=2)
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data="search_prev"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data="search_next"))
        if nav_buttons:
            markup.row(*nav_buttons)
        
        for pdf in pdfs:
            markup.add(InlineKeyboardButton(
                f"{utils.get_pdf_emoji(pdf['tag'])} {pdf['file_name'][:30]}",
                callback_data=f"view_{pdf['id']}"
            ))
        
        markup.add(InlineKeyboardButton("🔄 New Search", callback_data="search_new"))
        markup.add(InlineKeyboardButton(texts.BUTTON_CANCEL, callback_data="cancel"))
        
        if message_id:
            try:
                self.bot.edit_message_text(text, user_id, message_id, parse_mode='Markdown', reply_markup=markup)
            except Exception as e:
                if DEBUG:
                    print(f"   Edit failed, sending new message: {e}")
                self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
        else:
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)

    def handle_search_navigation(self, call):
        user_id = call.from_user.id
        current_state, data = db.get_user_state(user_id)
        
        if DEBUG:
            print(f"🔍 Search navigation - user: {user_id}, action: {call.data}, state: {current_state}")
        
        if current_state != 'search':
            self.bot.answer_callback_query(call.id, "Session expired. Please start a new search.", show_alert=True)
            return
        
        if not data or data.get('step') != 'results':
            self.bot.answer_callback_query(call.id, "No active search. Please start a new search.", show_alert=True)
            return
        
        action = call.data
        
        if action == "search_next":
            data['page'] = data.get('page', 0) + 1
            if DEBUG:
                print(f"   Next page: {data['page']}")
        elif action == "search_prev":
            data['page'] = max(0, data.get('page', 0) - 1)
            if DEBUG:
                print(f"   Prev page: {data['page']}")
        elif action == "search_new":
            db.clear_user_state(user_id)
            self.bot.answer_callback_query(call.id, "Starting new search...")
            self.start_search(user_id)
            try:
                self.bot.delete_message(user_id, call.message.message_id)
            except:
                pass
            return
        
        db.set_user_state(user_id, 'search', data)
        self.show_search_results(user_id, call.message.message_id)
        self.bot.answer_callback_query(call.id)

    
    def handle_search_state(self, message, data):
        user_id = message.from_user.id
        self.bot.send_message(
            user_id,
            "🔍 Please use the buttons to search.\n\nSend /cancel to cancel.",
            parse_mode='Markdown',
            reply_markup=utils.create_cancel_keyboard()
        )
    
    # ==================== PDF View Actions ====================
    
    def handle_view_pdf_callback(self, call):
        user_id = call.from_user.id
        pdf_id = int(call.data.split('_')[1])
        pdf = db.get_pdf(pdf_id)
        
        if not pdf:
            self.bot.answer_callback_query(call.id, texts.ERROR_NOT_FOUND)
            return
        
        if not pdf['is_approved'] and not self.is_admin(user_id) and pdf['uploaded_by'] != user_id:
            self.bot.answer_callback_query(call.id, "⏳ This PDF is pending approval.")
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
        
        markup = utils.create_pdf_action_buttons(pdf_id, user_id, self.is_admin(user_id))
        
        self.bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
        self.bot.answer_callback_query(call.id)
    
    def handle_download_callback(self, call):
        user_id = call.from_user.id
        pdf_id = int(call.data.split('_')[1])
        pdf = db.get_pdf(pdf_id)
        
        if not pdf:
            self.bot.answer_callback_query(call.id, texts.ERROR_NOT_FOUND)
            return
        
        if pdf['file_id']:
            try:
                self.bot.send_document(
                    user_id, 
                    pdf['file_id'], 
                    caption=f"📄 **{pdf['file_name']}**\n\n📚 **Subject:** {pdf['subject']}\n🏷️ **Tag:** {pdf['tag']}",
                    parse_mode='Markdown'
                )
                db.increment_download(pdf_id, user_id)
                
                if DEBUG:
                    print(f"📥 PDF downloaded by {user_id}: {pdf['file_name']} (ID: {pdf_id})")
                
                self.bot.answer_callback_query(call.id, texts.PDF_DOWNLOAD_STARTED)
            except Exception as e:
                if DEBUG:
                    print(f"❌ Download failed for {user_id}: {e}")
                self.bot.answer_callback_query(call.id, texts.PDF_DOWNLOAD_FAILED)
        else:
            self.bot.answer_callback_query(call.id, "❌ File not available.")
    
    def handle_like_callback(self, call):
        user_id = call.from_user.id
        action, pdf_id = call.data.split('_')
        pdf_id = int(pdf_id)
        
        if action == 'like':
            if db.like_pdf(pdf_id, user_id):
                if DEBUG:
                    print(f"❤️ PDF liked by {user_id}: {pdf_id}")
                self.bot.answer_callback_query(call.id, texts.PDF_LIKED)
            else:
                self.bot.answer_callback_query(call.id, "❤️ You already liked this.")
        else:
            db.unlike_pdf(pdf_id, user_id)
            if DEBUG:
                print(f"💔 PDF unliked by {user_id}: {pdf_id}")
            self.bot.answer_callback_query(call.id, texts.PDF_UNLIKED)
        
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
            
            markup = utils.create_pdf_action_buttons(pdf_id, user_id, self.is_admin(user_id))
            
            try:
                self.bot.edit_message_text(text, user_id, call.message.message_id, parse_mode='Markdown', reply_markup=markup)
            except:
                pass
    
    def handle_report_callback(self, call):
        user_id = call.from_user.id
        pdf_id = int(call.data.split('_')[1])
        
        db.set_user_state(user_id, 'report', {'pdf_id': pdf_id})
        
        self.bot.send_message(
            user_id,
            texts.PDF_REPORT_PROMPT,
            parse_mode='Markdown',
            reply_markup=utils.create_cancel_keyboard()
        )
        self.bot.answer_callback_query(call.id)
    
    def handle_share_callback(self, call):
        user_id = call.from_user.id
        pdf_id = int(call.data.split('_')[1])
        
        markup = utils.create_share_buttons(pdf_id, user_id)
        
        self.bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=markup)
        self.bot.answer_callback_query(call.id)
    
    def handle_report_state(self, message, data):
        user_id = message.from_user.id
        pdf_id = data['pdf_id']
        report_text = message.text
        
        if report_text.lower() == texts.BUTTON_CANCEL.lower():
            db.clear_user_state(user_id)
            self.bot.send_message(user_id, texts.CANCELLED, reply_markup=utils.create_main_menu_keyboard(user_id))
            return
        
        db.add_report(pdf_id, user_id, report_text)
        
        if DEBUG:
            print(f"⚠️ Report submitted by {user_id} for PDF {pdf_id}: {report_text[:50]}...")
        
        pdf = db.get_pdf(pdf_id)
        if pdf:
            uploader = db.get_user(pdf['uploaded_by'])
            if uploader:
                try:
                    self.bot.send_message(
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
                markup = InlineKeyboardMarkup()
                markup.add(
                    InlineKeyboardButton("👁️ View PDF", callback_data=f"view_{pdf_id}")
                )
                
                self.bot.send_message(
                    admin_id,
                    texts.REPORT_NOTIFY_ADMIN.format(
                        pdf_name=pdf['file_name'],
                        pdf_id=pdf_id,
                        uploader=uploader['full_name'] if uploader else "Unknown",
                        reporter=message.from_user.full_name or message.from_user.first_name,
                        reason=report_text
                    ),
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            except:
                pass
        
        db.clear_user_state(user_id)
        
        self.bot.send_message(
            user_id,
            texts.PDF_REPORT_SENT,
            parse_mode='Markdown',
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )
    
    # ==================== Profile ====================
    
    def show_profile(self, user_id):
        user = db.get_user(user_id)
        if not user:
            self.bot.send_message(user_id, texts.NOT_REGISTERED)
            return
        
        db.update_user_activity(user_id)
        
        uploads_count = db.get_user_upload_count(user_id)
        downloads_count = db.get_user_download_count(user_id)
        stats = db.get_user_referral_stats(user_id)
        
        now = utils.get_current_time()
        
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
        
        self.bot.send_message(
            user_id,
            text,
            parse_mode='Markdown',
            reply_markup=utils.create_profile_buttons(user_id)
        )
        
        if DEBUG:
            print(f"👤 Profile viewed by user {user_id}")
    
    def show_referral_share(self, user_id, message_id=None):
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
            self.bot.edit_message_text(
                "🔗 **Share Your Referral Link**\n\n"
                "Share this link with your friends and classmates:\n\n"
                f"`{referral_link}`\n\n"
                "When they register using your link, you'll get credit! 🎉",
                user_id,
                message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )
        else:
            self.bot.send_message(
                user_id,
                "🔗 **Share Your Referral Link**\n\n"
                f"`{referral_link}`\n\n"
                "Share this link with your friends!",
                parse_mode='Markdown',
                reply_markup=markup
            )
    
    # ==================== Help ====================
    
    def show_help(self, user_id):
        markup = utils.create_help_buttons()
        
        self.bot.send_message(
            user_id,
            texts.HELP_TEXT,
            parse_mode='Markdown',
            reply_markup=markup
        )
    
    # ==================== Shared PDF Link Handler ====================
    
    def handle_pdf_share(self, user_id, pdf_id):
        pdf = db.get_pdf(pdf_id)
        if not pdf:
            self.bot.send_message(user_id, "❌ PDF not found.")
            return
        
        user = db.get_user(user_id)
        if not user:
            db.set_user_state(user_id, 'register', {'step': 'name', 'pending_pdf': pdf_id})
            self.bot.send_message(
                user_id,
                "📚 **Shared PDF**\n\nPlease register first to view this PDF.",
                parse_mode='Markdown',
                reply_markup=utils.create_cancel_keyboard()
            )
            self.bot.send_message(user_id, texts.REG_NAME, parse_mode='Markdown')
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
            markup = utils.create_pdf_action_buttons(pdf_id, user_id, self.is_admin(user_id))
            self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
    # ==================== Admin Broadcast & SQL ====================
    
    def handle_admin_broadcast(self, message, data):
        user_id = message.from_user.id
        broadcast_text = message.text
        
        if broadcast_text.lower() == texts.BUTTON_CANCEL.lower():
            db.clear_user_state(user_id)
            self.bot.send_message(
                user_id, 
                texts.CANCELLED, 
                parse_mode='Markdown',
                reply_markup=utils.create_main_menu_keyboard(user_id)
            )
            return
        
        admin = db.get_user(user_id)
        show_admin_name = db.get_setting('show_admin_name_in_broadcast', '1') == '1'
        admin_name = admin['full_name'] if admin and show_admin_name else ""
        
        broadcast_message = (
            f"📢 **ANNOUNCEMENT**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{broadcast_text}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
        )
        
        if show_admin_name and admin_name:
            broadcast_message += f"👤 **Sent by:** {admin_name}\n"
        
        broadcast_message += f"📅 **Date:** {get_current_time().strftime('%Y-%m-%d %I:%M %p')}\n\n"
        broadcast_message += f"_To reply, click the button below_"
        
        reply_markup = InlineKeyboardMarkup()
        reply_markup.add(InlineKeyboardButton(
            "💬 Reply to Admin",
            callback_data=f"reply_to_admin_{user_id}"
        ))
        
        users = db.get_all_users()
        success_count = 0
        failed_count = 0
        
        broadcast_enabled = db.get_setting('broadcast_enabled', '1') == '1'
        if not broadcast_enabled:
            self.bot.send_message(user_id, "❌ Broadcast is disabled by admin settings.")
            return
        
        for user in users:
            try:
                self.bot.send_message(
                    user['user_id'], 
                    broadcast_message, 
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                success_count += 1
            except Exception as e:
                if DEBUG:
                    print(f"   Failed to send to {user['user_id']}: {e}")
                failed_count += 1
        
        db.clear_user_state(user_id)
        
        if DEBUG:
            print(f"📢 Broadcast sent by admin {user_id}: {success_count} success, {failed_count} failed")
        
        self.bot.send_message(
            user_id,
            f"✅ **Broadcast Sent!**\n\n"
            f"📊 **Statistics:**\n"
            f"├ ✅ Sent to: `{success_count}` users\n"
            f"└ ❌ Failed: `{failed_count}` users",
            parse_mode='Markdown',
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )
    
    
    def handle_admin_sql(self, message, data):
        user_id = message.from_user.id
        sql = message.text.strip()
        
        if DEBUG:
            print(f"🔧 SQL executed by admin {user_id}: {sql[:100]}...")
        
        if sql.lower() == texts.BUTTON_CANCEL.lower():
            db.clear_user_state(user_id)
            self.bot.send_message(
                user_id, 
                texts.CANCELLED, 
                parse_mode='Markdown',
                reply_markup=utils.create_main_menu_keyboard(user_id)
            )
            return
        
        result = db.execute_sql(sql)
        
        if isinstance(result, list):
            if len(result) == 0:
                result_str = "✅ Query executed. No rows returned."
            else:
                rows = []
                for row in result[:20]:
                    if isinstance(row, sqlite3.Row):
                        rows.append(dict(row))
                    else:
                        rows.append(row)
                result_str = f"📊 **Results:** ({len(result)} rows)\n\n```\n"
                import json
                result_str += json.dumps(rows, indent=2, default=str)[:3500]
                result_str += "\n```"
                if len(result) > 20:
                    result_str += f"\n\n*Showing first 20 of {len(result)} rows.*"
        else:
            result_str = f"✅ {result}"
        
        if len(result_str) > 4000:
            result_str = result_str[:4000] + "\n\n... (truncated)"
        
        db.clear_user_state(user_id)
        
        self.bot.send_message(
            user_id,
            texts.ADMIN_SQL_RESULT.format(result=result_str),
            parse_mode='Markdown',
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )
    
    def start_reply_to_admin(self, user_id, admin_id, message_id=None):
        if DEBUG:
            print(f"💬 User {user_id} starting reply to admin {admin_id}")
        
        db.set_user_state(user_id, 'reply_to_admin', {
            'admin_id': admin_id,
            'step': 'waiting_for_message'
        })
        
        self.bot.send_message(
            user_id,
            "💬 **Reply to Admin**\n\n"
            "Please type your message below.\n\n"
            "The admin will receive your message with your user info.\n\n"
            "Type **Cancel** to cancel.",
            parse_mode='Markdown',
            reply_markup=utils.create_cancel_keyboard()
        )
        
        if message_id:
            try:
                self.bot.delete_message(user_id, message_id)
            except:
                pass
    
    def send_reply_to_admin(self, user_id, admin_id, reply_text):
        user = db.get_user(user_id)
        if not user:
            return False
        
        user_name = user['full_name'] or f"User {user_id}"
        user_class = user['class'] or "Not set"
        user_region = user['region'] or "Not set"
        
        admin_message = (
            f"💬 **REPLY FROM USER**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📝 **Message:**\n{reply_text}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **User:** {user_name}\n"
            f"🆔 **ID:** `{user_id}`\n"
            f"🎓 **Class:** {user_class}\n"
            f"📍 **Region:** {user_region}\n"
            f"📅 **Date:** {get_current_time().strftime('%Y-%m-%d %I:%M %p')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"_Use the buttons below to reply back to this user_"
        )
        
        reply_markup = InlineKeyboardMarkup()
        reply_markup.add(
            InlineKeyboardButton("📝 Reply to User", callback_data=f"admin_reply_user_{user_id}"),
            InlineKeyboardButton("👤 View User", callback_data=f"admin_user_details_{user_id}")
        )
        
        try:
            self.bot.send_message(
                admin_id,
                admin_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return True
        except Exception as e:
            if DEBUG:
                print(f"❌ Failed to send reply to admin {admin_id}: {e}")
            return False
    
    # ==================== Callback Handler Router ====================
    
    def handle_callbacks(self, call):
        user_id = call.from_user.id
        user = db.get_user(user_id)
        data = call.data
        
        if DEBUG:
            print(f"📞 Callback from {user_id}: {data}")
        
        if user and not user['is_banned']:
            db.update_user_activity(user_id)
        
        if data == "ignore":
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "cancel":
            db.clear_user_state(user_id)
            self.bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=None)
            self.bot.send_message(
                user_id,
                texts.CANCELLED,
                parse_mode='Markdown',
                reply_markup=utils.create_main_menu_keyboard(user_id)
            )
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "confirm_upload":
            current_state, pending_data = db.get_user_state(user_id)
            if current_state == 'pending_upload' and pending_data:
                db.set_user_state(user_id, 'upload', {
                    'step': 'subject',
                    'file_id': pending_data['file_id'],
                    'file_name': pending_data['file_name']
                })
                self.ask_subject(user_id)
                self.bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=None)
                self.bot.answer_callback_query(call.id, "Let's add details for your PDF!")
            else:
                self.bot.answer_callback_query(call.id, "Session expired. Please start again.")
            return
        
        if data == "share_referral":
            self.show_referral_share(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "copy_referral_link":
            referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
            self.bot.answer_callback_query(call.id, "Link copied! Share it with friends.", show_alert=True)
            self.bot.send_message(
                user_id,
                f"🔗 **Your Referral Link**\n\n`{referral_link}`\n\nSend this link to your friends!",
                parse_mode='Markdown'
            )
            return
        
        if data == "back_to_profile":
            self.show_profile(user_id)
            self.bot.delete_message(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        # Registration callbacks
        if data.startswith('region_'):
            self.handle_region_callback(call)
            return
        
        if data.startswith('schools_page_'):
            self.handle_schools_page_callback(call)
            return
        
        if data.startswith('manual_school_'):
            self.handle_manual_school_callback(call)
            return
        
        if data.startswith('school_'):
            self.handle_school_callback(call)
            return
        
        if data.startswith('class_'):
            self.handle_class_callback(call)
            return
        
        if data.startswith('back_'):
            self.handle_back_callback(call)
            return
        
        if data == 'manual_region_start':
            self.handle_manual_region_start(call)
            return
        
        # Upload callbacks
        if data.startswith('subject_'):
            self.handle_subject_callback(call)
            return
        
        if data.startswith('tag_'):
            self.handle_tag_callback(call)
            return
        
        # Search callbacks
        if data.startswith('search_subject_'):
            self.handle_search_subject_callback(call)
            return
        
        if data.startswith('search_tag_'):
            self.handle_search_tag_callback(call)
            return
        
        if data in ["search_next", "search_prev", "search_new"]:
            self.handle_search_navigation(call)
            return
        
        # PDF action callbacks
        if data.startswith('view_'):
            self.handle_view_pdf_callback(call)
            return
        
        if data.startswith('download_'):
            self.handle_download_callback(call)
            return
        
        if data.startswith('like_') or data.startswith('unlike_'):
            self.handle_like_callback(call)
            return
        
        if data.startswith('report_'):
            self.handle_report_callback(call)
            return
        
        if data.startswith('share_'):
            self.handle_share_callback(call)
            return
        
        # Delete PDF callbacks
        if data.startswith("delete_"):
            pdf_id = int(data.split("_")[1])
            if self.admin_instance:
                self.admin_instance.delete_pdf(user_id, pdf_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data.startswith("confirm_delete_"):
            pdf_id = int(data.split("_")[2])
            if self.admin_instance:
                self.admin_instance.confirm_delete_pdf(user_id, pdf_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        # Membership callbacks
        if data == "refresh_membership":
            self.show_membership_requirements(user_id)
            self.bot.answer_callback_query(call.id, "✅ Status refreshed!")
            return
        
        if data == "membership_complete":
            self.complete_membership(user_id)
            self.bot.answer_callback_query(call.id, "🎉 Welcome to Ardayda Bot!")
            return
        
        if data.startswith("confirm_whatsapp_"):
            req_id = int(data.split("_")[2])
            db.set_whatsapp_confirmed(user_id, True)
            db.log_membership_event(user_id, req_id, 'confirm_whatsapp')
            self.show_membership_requirements(user_id)
            
            status = self.get_all_membership_status(user_id)
            if status['all_joined']:
                self.bot.answer_callback_query(call.id, "✅ All requirements completed! Click Continue to proceed.")
            else:
                self.bot.answer_callback_query(call.id, "✅ WhatsApp confirmed! Join remaining channels to continue.")
            return
        
        # Admin callbacks
        if (data.startswith('admin_') or data.startswith('membership_')) and self.admin_instance:
            if self.is_admin(user_id):
                self.admin_instance.handle_admin_callback(call)
            else:
                self.bot.answer_callback_query(call.id, texts.ERROR_PERMISSION)
            return
        
        # Reply to admin
        if data.startswith("reply_to_admin_"):
            admin_id = int(data.split("_")[3])
            self.start_reply_to_admin(user_id, admin_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        # Admin reply to user
        if data.startswith("admin_reply_user_"):
            if self.is_admin(user_id) and self.admin_instance:
                target_user_id = int(data.split("_")[3])
                self.admin_instance.start_admin_reply_to_user(user_id, target_user_id, call.message.message_id)
                self.bot.answer_callback_query(call.id)
            else:
                self.bot.answer_callback_query(call.id, texts.ERROR_PERMISSION)
            return
        
        # Legacy membership verification
        if data.startswith('verify_telegram_') or data.startswith('verify_whatsapp_'):
            if self.admin_instance:
                self.admin_instance.handle_admin_callback(call)
            return
        
        self.bot.answer_callback_query(call.id, "Unknown action")