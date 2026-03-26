# telegram_pdf_bot/texts.py
from config import TAGS, CLASSES

# ==================== REGISTRATION ====================

REG_NAME = (
    "📝 **Welcome to Ardayda Bot!**\n\n"
    "Let's get you registered. Please enter your **full name**.\n\n"
    "📌 **Example:** `Mohamed Ahmed Ali`"
)

REG_SUCCESS = (
    "✅ **Registration Completed!**\n\n"
    "🎉 Welcome to Ardayda Educational Platform!\n\n"
    "You can now upload and search educational PDFs using the menu below."
)

REG_REGION = (
    "📍 **Select Your Region**\n\n"
    "Choose your region from the buttons below:"
)

REG_SCHOOL = (
    "🏫 **Select Your School**\n\n"
    "📍 **Region:** `{region}`\n\n"
    "Choose your school from the list:"
)

REG_CLASS = (
    "🎓 **Select Your Class**\n\n"
    "Choose your current class:"
)

REG_PHONE = (
    "📞 **Phone Number**\n\n"
    "Please share your phone number using the button below.\n\n"
    "This helps us verify your account."
)

# School data by region
form_four_schools_by_region = {
    "BARI": [
        "Bandar Qasim", "Bari", "Garisa", "Salahudin", "Ras Asayr Bosaso",
        "Omar bin Abdazis", "Bosaso Public", "Bender Siyaad Qaw", "White Tower",
        "Xalane Bosaso", "Iftiin Bosaso", "Sayid Mohamed Bosaso", "Xamdan",
        "Ganaane", "Dr Ahmed Bosaso", "Iman Nawawi Bosaso", "Ugas Yasin",
        "Imam shafie Bosaso", "Mocalin Jama Bosaso", "Najax", "Biyo kulule Bosaso",
        "Haji Yasin", "Girible", "Mohamed Awale", "Haji Salad", "Carta",
        "Jaamu Maalik", "Eldahir"
    ],
    "NUGAAL": [
        "Imamu Nawawi Garowe F4", "DR. Ahmed Garowe F4", "Awr Culus F4",
        "Sh. Hamid F4", "Nugal F4", "Daawad Garowe F4", "Gambol F4",
        "Al-Xikma Garowe F4", "Al Waxa F4", "Kobciye F4", "Alculum F4",
        "Xar xaar F4", "Dr ahmed Burtinle F4", "Burtinle F4", "Muntada Burtinle F4",
        "Xasbahalle F4", "Sare Qarxis F4", "Sare Eyl F4", "Sare Sinujjil F4",
        "Sare Negeye F4", "Sare Usgure F4", "Sare Yoonbays F4", "Sare Jalam F4"
    ],
    "KARKAAR": [
        "Qoton", "Dhuudo", "Dhudhub", "Humbays", "Qarrasoor", "Hidda",
        "Uurjire", "Sheerbi", "Suldaan Mubarak (Yeka)", "Al-Muntada",
        "Ali Afyare", "Kubo", "Xaaji Aaden", "Xaaji Osman"
    ],
    "MUDUG": [
        "1st August", "Africa", "Dr.Ahmed Galkoio", "A.A.Sharmarke", "Yamays",
        "Ilays galkaoi", "Beyra", "Garsoor", "Omar Samatar", "Haji Ali Bihi",
        "Agoonta Qaran F4", "Al-xigma", "Hala booqad", "Haji Dirie", "Yasin Nor",
        "Sare Bacaaadwayn F4", "Bacadweyn", "Hema", "Barbarshe", "Bursalah",
        "Golden 18+", "Hope", "GECPD Xarlo", "Cagaraan F4", "Sare Garacad",
        "Balli busle F4", "Sare Jarriban", "Sare Galdogob"
    ],
    "HAYLAAN": [
        "Sare Dhahar Public", "Kala-dhac", "Salaxudin-Dhahar", "Buraan",
        "Dalmar Qol", "Damalla Xagarre", "Sare Damalla xagarre", "Sare Shimbiraale"
    ],
    "RAAS CASAYR": [
        "Maxamed Xuseen", "Bareeda", "Caluula", "Xabbob"
    ],
    "SANAAG": [
        "Al Furqan Badhan", "Al-Nuur Badhan", "Al-Rahma Badhan", "Badhan Sec",
        "Farax-cadde", "Hadaftimo", "Yubbe", "Armale", "Rad", "Midigale"
    ]
}

# ==================== BUTTON TEXTS ====================

BUTTON_UPLOAD = "📤 Upload PDF"
BUTTON_SEARCH = "🔍 Search PDFs"
BUTTON_PROFILE = "👤 My Profile"
BUTTON_HELP = "❓ Help"
BUTTON_ADMIN = "👑 Admin Panel"
BUTTON_CANCEL = "❌ Cancel"
BUTTON_BACK = "🔙 Back"
BUTTON_DOWNLOAD = "📥 Download"
BUTTON_LIKE = "❤️ Like"
BUTTON_UNLIKE = "💔 Unlike"
BUTTON_REPORT = "⚠️ Report"
BUTTON_SHARE = "🔗 Share"
BUTTON_SHARE_TELEGRAM = "📱 Share on Telegram"
BUTTON_SHARE_WHATSAPP = "💬 Share on WhatsApp"
BUTTON_CONTACT_ADMIN = "📞 Contact Admin"
BUTTON_NEXT = "▶️ Next"
BUTTON_PREV = "◀️ Prev"
BUTTON_SKIP = "⏭️ Skip"
BUTTON_REGION_NOT_LISTED = "✏️ Region not listed?"
BUTTON_SCHOOL_NOT_LISTED = "✏️ School not listed?"
BUTTON_VERIFY = "✅ Verify"
BUTTON_JOIN = "📢 Join"
BUTTON_JOINED = "✅ I've Joined"
BUTTON_REFRESH = "🔄 Refresh"

# ==================== MANUAL ENTRY ====================

MANUAL_REGION_PROMPT = (
    "✏️ **Enter Region Manually**\n\n"
    "Please type the name of your region.\n\n"
    "📝 **Example:** `Banaadir`, `Woqooyi Galbeed`\n\n"
    "Type **Cancel** to go back."
)

MANUAL_SCHOOL_PROMPT = (
    "✏️ **Enter School Manually**\n\n"
    "📍 **Region:** `{region}`\n\n"
    "Please type the name of your school.\n\n"
    "Type **Cancel** to go back."
)

# ==================== ADMIN NOTIFICATION ====================

ADMIN_MANUAL_ENTRY_NOTIFICATION = (
    "🔔 **⚠️ MISSING {entry_type} REPORT**\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "👤 **User:** `{user_name}`\n"
    "🆔 **ID:** `{user_id}`\n"
    "📞 **Phone:** `{user_phone}`\n\n"
    "{location_info}\n"
    "📅 **Time:** `{date}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "💡 **Action:** Please add this to the database."
)

ADMIN_REFERRAL_NOTIFICATION = (
    "🎉 **New Referral!**\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "👤 **Referrer:** `{referrer_name}`\n"
    "🆔 **Referrer ID:** `{referrer_id}`\n"
    "👤 **New User:** `{new_user_name}`\n"
    "🆔 **New User ID:** `{new_user_id}`\n"
    "📅 **Time:** `{date}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "📊 **Total Referrals:** `{total}`"
)

USER_REFERRAL_NOTIFICATION = (
    "🎉 **Great News!**\n\n"
    "Someone registered using your referral link!\n\n"
    "👤 **New User:** `{new_user_name}`\n"
    "📊 **Total Referrals:** `{total}`\n\n"
    "Keep sharing your link to earn more!"
)

# ==================== SUBJECTS ====================

SUBJECTS = [
    "Math", "Physics", "Chemistry", "Biology", "ICT",
    "Arabic", "Islamic", "English", "Somali", "G.P",
    "Geography", "History", "Agriculture", "Business"
]

# ==================== GENERAL ====================

HOME_WELCOME = (
    "🏠 **Main Menu**\n\n"
    "Welcome back, **{name}!**\n\n"
    "What would you like to do today?"
)

CANCELLED = (
    "❌ **Cancelled**\n\n"
    "Returning to main menu..."
)

SESSION_EXPIRED = (
    "⏰ **Session Expired**\n\n"
    "Please start over from the main menu."
)

UNKNOWN_INPUT = (
    "ℹ️ **Please use the buttons provided**\n\n"
    "If you need help, press the ❓ Help button."
)

NOT_REGISTERED = (
    "❌ **Not Registered**\n\n"
    "Please type /start to register first."
)

ACCOUNT_SUSPENDED = (
    "🚫 **Account Suspended**\n\n"
    "Your account has been suspended. Please contact an admin."
)

# ==================== UPLOAD ====================

UPLOAD_FILE_PROMPT = (
    "📤 **Upload PDF**\n\n"
    "Please send me the PDF file you want to upload.\n\n"
    "📄 **Supported:** PDF files only\n\n"
    "Press **Cancel** to go back."
)

UPLOAD_INVALID_FILE = (
    "❌ **Invalid File**\n\n"
    "Please send a valid **PDF document**.\n\n"
    "Send the PDF file or press **Cancel**."
)

UPLOAD_RECEIVED = (
    "✅ **PDF Received!**\n\n"
    "📄 **File:** `{file_name}`\n\n"
    "Now let's add some details..."
)

UPLOAD_SUBJECT = (
    "📚 **Select Subject**\n\n"
    "Choose the subject for this PDF:"
)

UPLOAD_TAG = (
    "🏷️ **Select Tag**\n\n"
    "Choose a tag to categorize this PDF:"
)

UPLOAD_SUCCESS = (
    "🎉 **Upload Successful!**\n\n"
    "📄 **File:** `{file_name}`\n"
    "📚 **Subject:** `{subject}`\n"
    "🏷️ **Tag:** `{tag}`\n"
    "🆔 **ID:** `{pdf_id}`\n\n"
    "⏳ **Pending Approval**\n"
    "Admins will review your upload soon."
)

UPLOAD_FAILED = (
    "❌ **Upload Failed**\n\n"
    "Something went wrong. Please try again later."
)

# ==================== SEARCH ====================

SEARCH_START = (
    "🔍 **Search PDFs**\n\n"
    "Select a subject to search:"
)

SEARCH_SUBJECT_SELECTED = (
    "🔍 **Subject:** `{subject}`\n\n"
    "Select a tag (optional) or press **Skip**:"
)

SEARCH_NO_RESULTS = (
    "😕 **No Results Found**\n\n"
    "No PDFs found for the selected criteria.\n\n"
    "Try a different subject or tag."
)

SEARCH_RESULTS = (
    "📚 **Search Results**\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "📖 **Subject:** `{subject}`\n"
    "🏷️ **Tag:** `{tag}`\n"
    "📄 **Found:** `{total}` PDFs\n"
    "📄 **Page:** `{page}/{total_pages}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n\n"
)

SEARCH_RESULT_ITEM = (
    "{emoji} **{name}**\n"
    "   📚 `{subject}` | 🏷️ `{tag}`\n"
    "   ❤️ `{likes}` likes | 📥 `{downloads}` downloads\n"
    "   🆔 `{id}`\n\n"
)

# ==================== PDF ACTIONS ====================

PDF_VIEW = (
    "📄 **{name}**\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "📚 **Subject:** `{subject}`\n"
    "🏷️ **Tag:** `{tag}`\n"
    "👤 **Uploader:** `{uploader}`\n"
    "📅 **Date:** `{date}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "📥 **Downloads:** `{downloads}`\n"
    "❤️ **Likes:** `{likes}`\n"
)

PDF_DOWNLOAD_STARTED = "✅ **Download Started!** Check your chat."
PDF_DOWNLOAD_FAILED = "❌ **Download Failed** Please try again."
PDF_LIKED = "❤️ **Liked!**"
PDF_UNLIKED = "💔 **Unliked**"

PDF_REPORT_PROMPT = (
    "⚠️ **Report PDF**\n\n"
    "Please describe why you're reporting this PDF.\n\n"
    "📝 **Examples:**\n"
    "• Wrong content\n"
    "• Duplicate file\n"
    "• Inappropriate material\n\n"
    "Type **Cancel** to cancel."
)

PDF_REPORT_SENT = (
    "✅ **Report Sent!**\n\n"
    "Thank you for helping keep our library clean.\n"
    "Admins will review this shortly."
)

REPORT_NOTIFY_UPLOADER = (
    "⚠️ **Your PDF Has Been Reported**\n\n"
    "📄 **PDF:** `{pdf_name}`\n"
    "👤 **Reporter:** `{reporter}`\n"
    "💬 **Reason:** {reason}\n\n"
    "Admins will review this."
)

REPORT_NOTIFY_ADMIN = (
    "⚠️ **New Report**\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "📄 **PDF:** `{pdf_name}`\n"
    "🆔 **PDF ID:** `{pdf_id}`\n"
    "👤 **Uploader:** `{uploader}`\n"
    "👤 **Reporter:** `{reporter}`\n"
    "💬 **Reason:** {reason}\n"
    "━━━━━━━━━━━━━━━━━━━━━"
)

# ==================== PROFILE ====================

PROFILE_DISPLAY = (
    "👤 **My Profile**\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "📛 **Name:** `{name}`\n"
    "🆔 **ID:** `{user_id}`\n"
    "📞 **Phone:** `{phone}`\n"
    "🎓 **Class:** `{class_}`\n"
    "📍 **Region:** `{region}`\n"
    "🏫 **School:** `{school}`\n"
    "📅 **Joined:** `{joined}`\n"
    "🕐 **Last Active:** `{last_active}`\n"
    "⏱️ **Member Since:** `{days_joined}` days\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "📊 **Statistics**\n"
    "📤 **Uploads:** `{uploads}`\n"
    "📥 **Downloads:** `{downloads}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "🔗 **Referral Program**\n"
    "👥 **Referrals:** `{conversions}`\n"
)

REFERRAL_LINK_TEXT = (
    "\n🔗 **Your Referral Link**\n\n"
    "Share this link with friends:\n"
    "`https://t.me/{bot_username}?start=ref_{user_id}`\n\n"
    "When they register, you'll get credit!"
)

# ==================== HELP ====================

HELP_TEXT = (
    "❓ **Help Center**\n"
    "━━━━━━━━━━━━━━━━━━━━━\n\n"
    "**📤 Upload PDF**\n"
    "Share educational materials with the community\n\n"
    "**🔍 Search PDFs**\n"
    "Find PDFs by subject and tag\n\n"
    "**👤 My Profile**\n"
    "View your stats and referral link\n\n"
    "**🔗 Referral Program**\n"
    "Invite friends and earn recognition\n\n"
    "**⚠️ Report**\n"
    "Report inappropriate content\n\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "**Need more help?**\n"
    "Contact our admin team via the button below."
)

# ==================== ADMIN ====================

ADMIN_PANEL = "👑 **Admin Panel**\n\nSelect an option:"

ADMIN_STATS = (
    "📊 **System Statistics**\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "👥 **Total Users:** `{total_users}`\n"
    "📄 **Total PDFs:** `{total_pdfs}`\n"
    "📥 **Total Downloads:** `{total_downloads}`\n"
    "⏳ **Pending PDFs:** `{pending_pdfs}`\n"
    "🚨 **Pending Reports:** `{total_reports}`\n"
    "━━━━━━━━━━━━━━━━━━━━━"
)

ADMIN_USER_LIST = "👥 **User List**\n\n"
ADMIN_USER_ITEM = "{status}{role} **{name}**\n   ├ ID: `{id}`\n   └ {class_name} @ {school}\n\n"

ADMIN_PDF_PENDING_LIST = "⏳ **Pending PDFs**\n\n"
ADMIN_PDF_PENDING_ITEM = "{number}. **{name}**\n   📚 {subject} | {tag}\n   👤 {uploader}\n   🆔 `{id}`\n"

ADMIN_REPORT_LIST = "🚨 **Pending Reports**\n\n"
ADMIN_REPORT_ITEM = "{number}. PDF: **{pdf_name}** (ID: {pdf_id})\n   👤 {reporter}\n   💬 {reason}\n"

ADMIN_BROADCAST_PROMPT = (
    "📢 **Send Broadcast**\n\n"
    "Type your message to send to all users.\n\n"
    "Type **Cancel** to cancel."
)

ADMIN_BROADCAST_CONFIRM = "✅ **Broadcast Sent!** Sent to `{count}` users."

ADMIN_SQL_PROMPT = (
    "🔧 **SQL Console**\n\n"
    "⚠️ **WARNING:** This can modify data!\n\n"
    "Enter SQL query.\n\n"
    "Type **Cancel** to cancel."
)

ADMIN_SQL_RESULT = "📊 **SQL Result:**\n```\n{result}\n```"

ADMIN_PDF_APPROVE_SUCCESS = "✅ **PDF approved!**"
ADMIN_PDF_DELETE_SUCCESS = "✅ **PDF deleted!**"
ADMIN_REPORT_RESOLVE_SUCCESS = "✅ **Report resolved.**"

# ==================== MEMBERSHIP ====================

MEMBERSHIP_REQUIRED = (
    "🔒 **Membership Required**\n\n"
    "To use this bot, you must join:\n\n"
    "📌 **{name}**\n"
    "🔗 **Type:** `{type}`\n"
    "{description}"
    "🔗 **Link:** `{link}`\n\n"
    "After joining, click the verify button."
)

WHATSAPP_VERIFICATION = (
    "🔐 **WhatsApp Verification**\n\n"
    "To verify you've joined **{name}**, send this code in the WhatsApp group:\n\n"
    "`VERIFY {code}`\n\n"
    "After sending, click the confirmation button."
)

WHATSAPP_VERIFICATION_SUCCESS = "✅ **Verification Successful!** You can now use the bot."
WHATSAPP_VERIFICATION_FAILED = "❌ **Verification Failed** Please try again or contact admin."

# ==================== MEMBERSHIP SYSTEM TEXTS ====================

MEMBERSHIP_TITLE = "🔐 **MEMBERSHIP REQUIREMENTS**"
MEMBERSHIP_PROGRESS = "**Progress:** `{bar}` {joined}/{total} ({percent}%)"
MEMBERSHIP_TELEGRAM_SECTION = "📢 **TELEGRAM CHANNELS/GROUPS** (Auto-detected)"
MEMBERSHIP_WHATSAPP_SECTION = "💬 **WHATSAPP GROUPS** (Confirm after joining)"
MEMBERSHIP_JOINED = "✅ **{name}** - Joined"
MEMBERSHIP_NOT_JOINED = "❌ **{name}** - Not joined"
MEMBERSHIP_CONFIRMED = "✅ **{name}** - Confirmed"
MEMBERSHIP_NOT_CONFIRMED = "❌ **{name}** - Not confirmed"
MEMBERSHIP_LINK_FORMAT = "   🔗 `{link}`"

MEMBERSHIP_COMPLETE = (
    "🎉 **Congratulations!** You've joined all required communities!\n"
    "Click the button below to continue to the main menu."
)

MEMBERSHIP_INCOMPLETE = (
    "⚠️ **Please join all required channels/groups above** to access the bot.\n"
    "For WhatsApp groups, click **Confirm** after joining."
)

MEMBERSHIP_NO_REQUIREMENTS = "✅ No membership requirements. You have full access!"

MEMBERSHIP_WELCOME = (
    "🎉 **WELCOME TO ARDAYDA BOT!** 🎉\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "Thank you for joining all our communities, **{name}**!\n\n"
    "✅ You now have full access to:\n"
    "├ 📤 Upload PDFs\n"
    "├ 🔍 Search Educational Materials\n"
    "├ 👤 Track Your Profile\n"
    "└ 🔗 Share Referral Links\n\n"
    "Let's get started!"
)

MEMBERSHIP_REFRESH = "✅ Status refreshed!"
MEMBERSHIP_CONTINUE = "🎉 Welcome to Ardayda Bot!"

# ==================== MEMBERSHIP BUTTON TEXTS ====================

BUTTON_REFRESH_MEMBERSHIP = "🔄 Refresh Status"
BUTTON_CONTINUE_MEMBERSHIP = "🎉 Continue to Main Menu"
BUTTON_CONFIRM_WHATSAPP = "✅ Confirm {name}"
BUTTON_JOIN_TELEGRAM = "📢 Join {name}"
BUTTON_JOIN_WHATSAPP = "💬 Join {name}"

# ==================== ADMIN MEMBERSHIP TEXTS ====================

ADMIN_MEMBERSHIP_STATS_TITLE = "📊 **MEMBERSHIP STATISTICS**"
ADMIN_MEMBERSHIP_BREAKDOWN = "**REQUIREMENTS BREAKDOWN**"
ADMIN_MEMBERSHIP_OVERALL = "**OVERALL COMPLETION**"
ADMIN_MEMBERSHIP_TELEGRAM_ALL = "├ Telegram All Joined: `{joined}/{total}` ({percent}%)"
ADMIN_MEMBERSHIP_WHATSAPP_ALL = "└ WhatsApp Confirmed: `{confirmed}/{total}` ({percent}%)"

ADMIN_MEMBERSHIP_EVENTS_TITLE = "📋 **MEMBERSHIP EVENTS**"
ADMIN_MEMBERSHIP_EVENT_ITEM = "{icon} **{event_type}**\n├ 👤 User: `{user_name}`\n├ 📢 Requirement: `{req_name}`\n└ 📅 Time: `{date}`"

ADMIN_MEMBERSHIP_ANALYTICS_TITLE = "📈 **MEMBERSHIP ANALYTICS**"
ADMIN_MEMBERSHIP_COMPLETION_RATE = "**COMPLETION RATE**\n└ `{bar}` {percent}%"
ADMIN_MEMBERSHIP_DISTRIBUTION = "**DISTRIBUTION**\n├ ✅ Fully Completed: `{completed}` users\n└ ⏳ Partial/None: `{partial}` users"
ADMIN_MEMBERSHIP_ACTIVITY = "**RECENT ACTIVITY (Last 7 days)**"

ADMIN_CONFIRM_WHATSAPP_SUCCESS = "✅ WhatsApp confirmed for user {user_id}!"

# ==================== MEMBERSHIP ADMIN BUTTONS ====================

BUTTON_ADMIN_MEMBERSHIP_STATS = "📊 Membership Stats"
BUTTON_ADMIN_MEMBERSHIP_EVENTS = "📋 Membership Events"
BUTTON_ADMIN_MEMBERSHIP_ANALYTICS = "📈 Member Analytics"
BUTTON_ADMIN_MEMBERSHIP_LIST = "📋 List All"
BUTTON_ADMIN_MEMBERSHIP_ADD = "➕ Add New"
BUTTON_ADMIN_MEMBERSHIP_EDIT = "✏️ Edit"
BUTTON_ADMIN_MEMBERSHIP_DELETE = "🗑️ Delete"
BUTTON_ADMIN_MEMBERSHIP_TOGGLE = "🔄 Toggle Status"

# ==================== WHATSAPP CONFIRMATION TEXTS ====================

WHATSAPP_CONFIRM_SUCCESS = "✅ WhatsApp confirmed! Join remaining channels to continue."
WHATSAPP_CONFIRM_ALL_COMPLETE = "✅ All requirements completed! Click Continue to proceed."
WHATSAPP_CONFIRM_ALREADY = "✅ You've already confirmed this WhatsApp group."

# ==================== REFRESH TEXTS ====================

REFRESH_MEMBERSHIP_SUCCESS = "✅ Membership status refreshed!"
REFRESH_MEMBERSHIP_FAILED = "❌ Could not refresh. Please try again."

# ==================== ERRORS ====================

ERROR_NOT_FOUND = "❌ **Not Found**"
ERROR_PERMISSION = "❌ **Permission Denied** You don't have access to this."
ERROR_GENERIC = "❌ **Error** Please try again later."

# ==================== ADDITIONAL MEMBERSHIP TEXTS ====================

MEMBERSHIP_NEXT_REQUIREMENT = (
    "**Next Requirement:** {icon} **{name}**\n"
    "🔗 **Link:** `{link}`\n"
    "📝 **About:** {description}\n"
)

WHATSAPP_GROUP_HELP = (
    "💡 **Why join?** This WhatsApp group is where we share updates, study tips, and connect with fellow students.\n"
    "📞 **Admin Contact:** `{admin_whatsapp}` if you have issues joining.\n"
)

TELEGRAM_CHANNEL_HELP = (
    "💡 **Why join?** This channel shares educational resources and important announcements.\n"
)

WHATSAPP_LINK_CONTEXT = (
    "📝 **About this group:** {description}\n"
)

# ==================== BANNED USER TEXT ====================

ACCOUNT_SUSPENDED_WITH_CONTACT = (
    "🚫 **Account Suspended**\n\n"
    "Your account has been suspended. Please contact the admin to resolve this issue.\n\n"
    "📞 **Admin WhatsApp:** `{admin_whatsapp}`\n\n"
    "Click the button below to message the admin."
)

# ==================== PDF APPROVAL TEXTS ====================

PDF_APPROVED_NOTIFICATION = (
    "✅ **Your PDF has been approved!**\n\n"
    "📄 **File:** `{file_name}`\n"
    "🆔 **ID:** `{pdf_id}`\n\n"
    "It is now available for all users to search and download."
)

PDF_APPROVE_BUTTON = "✅ Approve PDF"
PDF_APPROVED_SUCCESS = "✅ PDF approved and now public!"

# ==================== SHARE WITH REFERRAL TEXTS ====================

SHARE_PDF_WITH_REFERRAL = (
    "🔗 **Share this PDF**\n\n"
    "📄 **File:** `{pdf_id}`\n\n"
    "Share this link with your friends:\n\n"
    "`{share_link}`\n\n"
    "When they register using this link, you'll get referral credit! 🎉"
)

# ==================== WHATSAPP REQUIREMENT ADD TEXTS ====================

WHATSAPP_ADD_DESCRIPTION_PROMPT = (
    "💡 **Tip:** Add a description to help users understand the purpose of this WhatsApp group.\n\n"
    "📝 **Example:** 'This group is for sharing study tips and updates. Admin: @username'\n\n"
    "Type `skip` to skip or **Cancel** to cancel."
)

WHATSAPP_DESCRIPTION_EXAMPLE = (
    "This WhatsApp group is for students to share study resources, ask questions, and stay updated on new PDFs."
)

# ==================== ADMIN SETTINGS TEXTS ====================

SETTING_TOGGLED = "✅ {setting_name} turned {status}"
SETTING_UPDATED = "✅ {setting_name} set to {value}"