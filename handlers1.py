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
    
    def check_all_memberships(self, user_id):
        """Check if user meets all membership requirements and track membership"""
        requirements = db.get_requirements(active_only=True)
        
        if not requirements:
            return True, None
        
        all_met = True
        missing_req = None
        
        for req in requirements:
            is_member = False
            
            if req['type'] == 'telegram':
                is_member = utils.is_telegram_member(self.bot, user_id, req['link'])
            else:  # whatsapp
                is_member = db.is_whatsapp_verified(user_id, req['id'])
            
            # Record membership status for tracking
            db.record_membership(user_id, req['id'], is_member)
            
            if not is_member:
                all_met = False
                missing_req = req
                break
        
        return all_met, missing_req
    
    # ==================== New Membership System Methods ====================
    def get_all_membership_status(self, user_id):
        """Get status of all membership requirements (Telegram auto-detected)"""
        requirements = db.get_requirements(active_only=True)
        
        if not requirements:
            return [], 0, 0
        
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
                    'description': req.get('description')
                })
            else:  # whatsapp
                is_verified = db.get_whatsapp_confirmed(user_id)
                whatsapp_reqs.append({
                    'id': req['id'],
                    'name': req['name'],
                    'link': req['link'],
                    'is_member': is_verified,
                    'description': req.get('description')
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
        
        text = "🔐 *MEMBERSHIP REQUIREMENTS*\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Progress bar
        percent = int((status['total_joined'] / status['total_required']) * 100)
        bar_length = 10
        filled = int(bar_length * percent / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        text += f"*Progress:* `{bar}` {status['total_joined']}/{status['total_required']} ({percent}%)\n\n"
        
        # Telegram Channels
        if status['telegram']:
            text += "📢 *TELEGRAM CHANNELS/GROUPS* (Auto-detected)\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for req in status['telegram']:
                if req['is_member']:
                    text += f"✅ *{req['name']}* - Joined\n"
                else:
                    text += f"❌ *{req['name']}* - Not joined\n"
                    text += f"   🔗 `{req['link']}`\n"
            text += "\n"
        
        # WhatsApp Groups
        if status['whatsapp']:
            text += "💬 *WHATSAPP GROUPS* (Confirm after joining)\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for req in status['whatsapp']:
                if req['is_member']:
                    text += f"✅ *{req['name']}* - Confirmed\n"
                else:
                    text += f"❌ *{req['name']}* - Not confirmed\n"
                    text += f"   🔗 `{req['link']}`\n"
            text += "\n"
        
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        if status['all_joined']:
            text += "🎉 *Congratulations!* You've joined all required communities!\n"
            text += "Click the button below to continue to the main menu.\n\n"
        else:
            text += "⚠️ *Please join all required channels/groups above* to access the bot.\n"
            text += "For WhatsApp groups, click 'Confirm' after joining.\n\n"
        
        return text
    
    def create_membership_keyboard(self, status):
        """Create keyboard for membership requirements"""
        markup = InlineKeyboardMarkup(row_width=2)
        
        # Add buttons for Telegram channels (auto-detect, just join links)
        for req in status['telegram']:
            if not req['is_member']:
                # Format link properly
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
                # Add join link and confirm button
                markup.add(
                    InlineKeyboardButton(f"💬 Join {req['name'][:15]}", url=req['link']),
                    InlineKeyboardButton(f"✅ Confirm {req['name'][:10]}", callback_data=f"confirm_whatsapp_{req['id']}")
                )
        
        # Refresh button
        markup.add(InlineKeyboardButton("🔄 Refresh Status", callback_data="refresh_membership"))
        
        # Continue button if all joined
        if status['all_joined']:
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
                # Message deleted or error, send new
        
        # Send new message
        msg = self.bot.send_message(
            user_id, text,
            parse_mode='Markdown', reply_markup=markup
        )
        db.set_user_membership_message(user_id, msg.message_id)
    
    def complete_membership(self, user_id):
        """Complete membership and show welcome message"""
        # Delete membership message
        stored_message_id = db.get_user_membership_message(user_id)
        if stored_message_id:
            try:
                self.bot.delete_message(user_id, stored_message_id)
            except:
                pass
        
        # Clear membership message ID
        db.set_user_membership_message(user_id, None)
        
        # Show welcome message
        user = db.get_user(user_id)
        welcome_text = (
            f"🎉 *WELCOME TO ARDAYDA BOT!* 🎉\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Thank you for joining all our communities, *{user['full_name'].split()[0] if user['full_name'] else 'User'}*!\n\n"
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
        
        if DEBUG:
            print(f"🎉 Membership completed for user {user_id}") 

    def require_membership(self, func):
        """Decorator to check membership AFTER user is registered"""
        def wrapper(message_or_call, *args, **kwargs):
            # Get user_id from message or call
            if hasattr(message_or_call, 'from_user'):
                user_id = message_or_call.from_user.id
            else:
                user_id = message_or_call.message.from_user.id
            
            # Check if user is registered
            user = db.get_user(user_id)
            if not user:
                # User not registered, let them register first
                return func(message_or_call, *args, **kwargs)
            
            # Check all memberships
            all_met, missing = self.check_all_memberships(user_id)
            
            if not all_met:
                if DEBUG:
                    print(f"🔒 User {user_id} missing membership: {missing['name'] if missing else 'Unknown'}")
                
                # Send membership required message
                if missing:
                    self.send_membership_required_message(user_id, missing)
                return
            
            # User passed membership check, execute original function
            return func(message_or_call, *args, **kwargs)
        
        return wrapper
    
    def send_membership_required_message(self, user_id, requirement):
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
            markup = InlineKeyboardMarkup(row_width=1)
            # Format the link
            link = requirement['link']
            if link.startswith('@'):
                link = f"https://t.me/{link[1:]}"
            
            markup.add(
                InlineKeyboardButton("✅ I've Joined", callback_data=f"verify_telegram_{requirement['id']}"),
                InlineKeyboardButton("📢 Join Channel/Group", url=link)
            )
        else:  # whatsapp
            text += "After joining the WhatsApp group, click the button below to verify."
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("📱 Join WhatsApp Group", url=requirement['link']),
                InlineKeyboardButton("✅ Verify", callback_data=f"verify_whatsapp_{requirement['id']}")
            )
        
        self.bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
    
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
                        date=get_current_time().strftime("%Y-%m-%d %H:%M"),
                        total=total
                    ),
                    parse_mode='Markdown'
                )
            except:
                pass
    
    # ==================== Command Handlers ====================
    
    def restore_command(self, message):
        """Clear user state and return to main menu"""
        user_id = message.from_user.id
        db.clear_user_state(user_id)
        
        if DEBUG:
            print(f"🔄 User {user_id} used /restore - state cleared")
        
        self.bot.send_message(
            user_id,
            "✅ *State Restored!*\n\nYou've been returned to the main menu.",
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
            
            # Check membership for existing user
            all_met, missing = self.check_all_memberships(user_id)
            if not all_met:
                self.send_membership_required_message(user_id, missing)
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

        # New user registration
        referred_by = None
        if start_param and start_param.startswith('ref_'):
            referrer_id = start_param.split('_')[1]
            referrer = db.get_user(referrer_id)
            if referrer and referrer['user_id'] != user_id:
                referred_by = referrer['user_id']
                self.bot.send_message(referrer_id, "**🚸 Someone Used Your Referral Link**", parse_mode='Markdown')
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
        """Handle PDF document uploads"""
        user_id = message.from_user.id
        user = db.get_user(user_id)
        
        if user and user['is_banned']:
            self.bot.send_message(user_id, texts.ACCOUNT_SUSPENDED)
            return
        
        if not user:
            self.bot.send_message(user_id, "❌ Please register first using /start")
            return
        
        # Check membership before upload
        all_met, missing = self.check_all_memberships(user_id)
        if not all_met:
            self.send_membership_required_message(user_id, missing)
            return
        
        current_state, data = db.get_user_state(user_id)
        
        if current_state == 'upload' and data and data.get('step') == 'waiting_for_file':
            self.handle_upload_pdf(message, data)
        else:
            # Check if it's a PDF
            if message.document.mime_type != 'application/pdf':
                self.bot.send_message(
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
            
            self.bot.send_message(
                user_id,
                f"📄 *Document Received:* `{message.document.file_name}`\n\n"
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
        
        # Update last active for registered users
        if user and not user['is_banned']:
            db.update_user_activity(user_id)

        current_state, data = db.get_user_state(user_id)
        
        if DEBUG:
            print(f"📨 Message from {user_id}: {message.text if message.text else '[non-text]'}, state={current_state}")
        
        # Handle admin flows (these don't need membership check)
        if current_state == 'add_requirement' and self.admin_instance:
            self.admin_instance.process_add_requirement(user_id, message)
            return
        
        if current_state == 'edit_requirement' and self.admin_instance:
            self.admin_instance.process_edit_requirement(user_id, message)
            return
        
        # Handle reply to admin state
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
            
            # Send reply to admin
            admin_id = data.get('admin_id')
            if admin_id:
                if self.send_reply_to_admin(user_id, admin_id, message.text):
                    db.clear_user_state(user_id)
                    self.bot.send_message(
                        user_id,
                        "✅ *Reply Sent!*\n\nYour message has been sent to the admin.\n\nThey will respond shortly.",
                        parse_mode='Markdown',
                        reply_markup=utils.create_main_menu_keyboard(user_id)
                    )
                else:
                    self.bot.send_message(
                        user_id,
                        "❌ *Failed to Send*\n\nCould not send your reply. Please try again later.",
                        parse_mode='Markdown',
                        reply_markup=utils.create_main_menu_keyboard(user_id)
                    )
            return
  
        # Handle admin reply to user state
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
            
            # Send admin reply to user
            target_user_id = data.get('target_user_id')
            if target_user_id and self.admin_instance:
                if self.admin_instance.send_admin_reply_to_user(user_id, target_user_id, message.text):
                    db.clear_user_state(user_id)
                    self.bot.send_message(
                        user_id,
                        f"✅ *Reply Sent!*\n\nYour reply has been sent to user `{target_user_id}`.",
                        parse_mode='Markdown',
                        reply_markup=utils.create_main_menu_keyboard(user_id)
                    )
                else:
                    self.bot.send_message(
                        user_id,
                        "❌ *Failed to Send*\n\nCould not send your reply.",
                        parse_mode='Markdown',
                        reply_markup=utils.create_main_menu_keyboard(user_id)
                    )
            return
        
        # Handle registration flow (no membership check needed)
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
        
        # For registered users, check membership BEFORE any action
        if user and not user['is_banned']:
            all_met, missing = self.check_all_memberships(user_id)
            if not all_met:
                self.send_membership_required_message(user_id, missing)
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
        
        location_info = f"📍 *Region:* `{region}`"
        
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
                        date=get_current_time().strftime("%Y-%m-%d %H:%M")
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
        
        location_info = f"📍 *Region:* `{region}`\n\n🏫 *School:* `{school}`"
        
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
                        date=get_current_time().strftime("%Y-%m-%d %H:%M")
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
            reply_markup=utils.create_subject_keyboard()
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
        
        self.bot.send_message(
            user_id,
            msg,
            parse_mode='Markdown',
            reply_markup=utils.create_main_menu_keyboard(user_id)
        )
        
        for admin_id in ADMIN_IDS:
            try:
                self.bot.send_message(
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
                self.bot.edit_message_reply_markup(user_id, message_id, reply_markup=None)
            except:
                pass
    
    # ==================== Search Flow ====================
    
    def start_search(self, user_id):
        user = db.get_user(user_id)
        if not user:
            self.bot.send_message(user_id, texts.NOT_REGISTERED)
            return
        
        # Clear any existing search state first
        db.clear_user_state(user_id)
        
        # Set fresh search state
        db.set_user_state(user_id, 'search', {'step': 'subject'})
        
        if DEBUG:
            print(f"🔍 Search started by user {user_id}, state set to search/subject")
        
        self.bot.send_message(
            user_id,
            texts.SEARCH_START,
            parse_mode='Markdown',
            reply_markup=utils.create_subject_keyboard()
        )
    
    def handle_search_subject_callback(self, call):
        user_id = call.from_user.id
        subject = call.data.split('_')[2]
        
        # Get current state to verify
        current_state, data = db.get_user_state(user_id)
        
        if DEBUG:
            print(f"📚 Search subject callback - user: {user_id}, subject: {subject}, state: {current_state}")
        
        # Check if user is in search mode
        if current_state != 'search':
            self.bot.answer_callback_query(call.id, "Session expired. Please start a new search.", show_alert=True)
            return
        
        # Update state with subject
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
        
        # Validate state
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
        
        # Save search criteria and go to results
        db.set_user_state(user_id, 'search', {
            'subject': subject,
            'tag': tag,
            'step': 'results',
            'page': 0
        })
        
        self.show_search_results(user_id, call.message.message_id)
        self.bot.answer_callback_query(call.id)
    
    def show_search_results(self, user_id, message_id=None):
        current_state, data = db.get_user_state(user_id)
        
        if DEBUG:
            print(f"🔍 Showing search results - user: {user_id}, state: {current_state}, data: {data}")
        
        # Validate state
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
        limit = 5
        offset = page * limit
        
        if DEBUG:
            print(f"   Searching: subject={subject}, tag={tag}, page={page}")
        
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
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data="search_prev"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data="search_next"))
        if nav_buttons:
            markup.row(*nav_buttons)
        
        # PDF list buttons
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
        
        # Validate state
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
            # Clear search state and start fresh
            db.clear_user_state(user_id)
            self.bot.answer_callback_query(call.id, "Starting new search...")
            self.start_search(user_id)
            try:
                self.bot.delete_message(user_id, call.message.message_id)
            except:
                pass
            return
        
        # Save updated page number
        db.set_user_state(user_id, 'search', data)
        
        # Refresh results
        self.show_search_results(user_id, call.message.message_id)
        self.bot.answer_callback_query(call.id)

    
    def handle_search_state(self, message, data):
        """Handle search state when user sends text"""
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
                    caption=f"📄 *{pdf['file_name']}*\n\n📚 *Subject:* {pdf['subject']}\n🏷️ *Tag:* {pdf['tag']}",
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
                self.bot.send_message(
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
            self.bot.send_message(
                user_id,
                "🔗 *Share Your Referral Link*\n\n"
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
                "📚 *Shared PDF*\n\nPlease register first to view this PDF.",
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
        
        # Get admin info
        admin = db.get_user(user_id)
        admin_name = admin['full_name'] if admin else f"Admin {user_id}"
        
        # Format broadcast with admin indicator
        broadcast_message = (
            f"📢 *ANNOUNCEMENT FROM ADMIN*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{broadcast_text}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Sent by:* {admin_name}\n"
            f"📅 *Date:* {get_current_time().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"_To reply, click the button below_"
        )
        
        # Create reply button for users to respond to admin
        reply_markup = InlineKeyboardMarkup()
        reply_markup.add(InlineKeyboardButton(
            "💬 Reply to Admin",
            callback_data=f"reply_to_admin_{user_id}"
        ))
        
        users = db.get_all_users()
        success_count = 0
        failed_count = 0
        
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
        
        # Send confirmation to admin
        self.bot.send_message(
            user_id,
            f"✅ *Broadcast Sent!*\n\n"
            f"📊 *Statistics:*\n"
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
        
        # Execute SQL
        result = db.execute_sql(sql)
        
        # Format result for display
        if isinstance(result, list):
            if len(result) == 0:
                result_str = "✅ Query executed. No rows returned."
            else:
                # Format rows nicely
                rows = []
                for row in result[:20]:  # Limit to 20 rows
                    if isinstance(row, sqlite3.Row):
                        rows.append(dict(row))
                    else:
                        rows.append(row)
                result_str = f"📊 *Results:* ({len(result)} rows)\n\n```\n"
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
        """Start the process for user to reply to admin"""
        if DEBUG:
            print(f"💬 User {user_id} starting reply to admin {admin_id}")
        
        # Store reply context
        db.set_user_state(user_id, 'reply_to_admin', {
            'admin_id': admin_id,
            'step': 'waiting_for_message'
        })
        
        self.bot.send_message(
            user_id,
            "💬 *Reply to Admin*\n\n"
            "Please type your message below.\n\n"
            "The admin will receive your message with your user info.\n\n"
            "Type *Cancel* to cancel.",
            parse_mode='Markdown',
            reply_markup=utils.create_cancel_keyboard()
        )
        
        if message_id:
            try:
                self.bot.delete_message(user_id, message_id)
            except:
                pass
    
    def send_reply_to_admin(self, user_id, admin_id, reply_text):
        """Send user's reply to admin with user info"""
        user = db.get_user(user_id)
        if not user:
            return False
        
        user_name = user['full_name'] or f"User {user_id}"
        user_class = user['class'] or "Not set"
        user_region = user['region'] or "Not set"
        
        # Format reply message for admin
        admin_message = (
            f"💬 *REPLY FROM USER*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📝 *Message:*\n{reply_text}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *User:* {user_name}\n"
            f"🆔 *ID:* `{user_id}`\n"
            f"🎓 *Class:* {user_class}\n"
            f"📍 *Region:* {user_region}\n"
            f"📅 *Date:* {get_current_time().strftime('%Y-%m-%d %H:%M')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"_Use the buttons below to reply back to this user_"
        )
        
        # Create reply button for admin to respond back
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
        
        # Update last active for registered users
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
        
        # Handle confirm upload
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
        
        # Handle share referral
        if data == "share_referral":
            self.show_referral_share(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        if data == "copy_referral_link":
            referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
            self.bot.answer_callback_query(call.id, "Link copied! Share it with friends.", show_alert=True)
            self.bot.send_message(
                user_id,
                f"🔗 *Your Referral Link*\n\n`{referral_link}`\n\nSend this link to your friends!",
                parse_mode='Markdown'
            )
            return
        
        if data == "back_to_profile":
            self.show_profile(user_id)
            self.bot.delete_message(user_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        # Handle registration callbacks
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
        
        # Handle upload callbacks
        if data.startswith('subject_'):
            self.handle_subject_callback(call)
            return
        
        if data.startswith('tag_'):
            self.handle_tag_callback(call)
            return
        
        # Handle search callbacks
        if data.startswith('search_subject_'):
            self.handle_search_subject_callback(call)
            return
        
        if data.startswith('search_tag_'):
            self.handle_search_tag_callback(call)
            return
        
        if data in ["search_next", "search_prev", "search_new"]:
            self.handle_search_navigation(call)
            return
        
        # Handle PDF action callbacks
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
        
        # Handle admin callbacks
        if (data.startswith('admin_') or data.startswith('membership_')) and self.admin_instance:
            if self.is_admin(user_id):
                self.admin_instance.handle_admin_callback(call)
            else:
                self.bot.answer_callback_query(call.id, texts.ERROR_PERMISSION)
            return
        
        # Handle reply to admin from user
        if data.startswith("reply_to_admin_"):
            admin_id = int(data.split("_")[3])
            self.start_reply_to_admin(user_id, admin_id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
            return
        
        # Handle admin reply to user (routed to admin_instance)
        if data.startswith("admin_reply_user_"):
            if self.is_admin(user_id) and self.admin_instance:
                target_user_id = int(data.split("_")[3])
                self.admin_instance.start_admin_reply_to_user(user_id, target_user_id, call.message.message_id)
                self.bot.answer_callback_query(call.id)
            else:
                self.bot.answer_callback_query(call.id, texts.ERROR_PERMISSION)
            return
        
        # Handle membership verification
        if data.startswith('verify_telegram_') or data.startswith('verify_whatsapp_'):
            if self.admin_instance:
                self.admin_instance.handle_admin_callback(call)
            return
        
        self.bot.answer_callback_query(call.id, "Unknown action")