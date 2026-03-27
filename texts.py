# telegram_pdf_bot/texts.py
from config import TAGS, CLASSES, SUBJECTS

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
BUTTON_BROWSE = "📚 Browse PDFs"
BUTTON_PROFILE = "👤 My Profile"
BUTTON_SETTINGS = "⚙️ Settings"
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
BUTTON_ON = "✅ ON"
BUTTON_OFF = "❌ OFF"

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
    "💰 **+1 Pen Added!** You now have {pens} pens to browse PDFs.\n\n"
    "Keep sharing your link to earn more!"
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
    "📄 **File:** `{file_name}`\n"
    "📦 **Size:** `{size}`\n\n"
    "Now let's add some details..."
)

UPLOAD_SELECT_CLASS = (
    "🎓 **Select Class**\n\n"
    "Choose the class this PDF is for:"
)

UPLOAD_SUBJECT = (
    "📚 **Select Subject**\n\n"
    "Choose the subject for this PDF:"
)

UPLOAD_TAG = (
    "🏷️ **Select Tag**\n\n"
    "Choose a tag to categorize this PDF:\n\n"
    "📌 **Tags:**\n"
    "• **Book** - Complete textbooks and reference books\n"
    "• **Exam/Assignment** - Past papers and assignments\n"
    "• **Question/Answer** - Q&A format materials\n"
    "• **Chapters** - Individual chapter materials\n"
    "• **Notes** - Study notes and summaries\n"
    "• **Summary** - Concise summaries\n"
    "• **Chapter Reviews** - Chapter review materials\n"
    "• **Centerlized** - Centralized exams (requires year)\n"
    "• **Unclassified** - Materials without specific classification"
)

UPLOAD_SELECT_YEAR = (
    "📅 **Select Year**\n\n"
    "Choose the year for this Centerlized exam:"
)

UPLOAD_SUCCESS = (
    "🎉 **Upload Successful!**\n\n"
    "📄 **File:** `{file_name}`\n"
    "🎓 **Class:** `{pdf_class}`\n"
    "📚 **Subject:** `{subject}`\n"
    "🏷️ **Tag:** `{tag}`\n"
    "🆔 **ID:** `{pdf_id}`\n\n"
    "**Status:** {status}"
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

SEARCH_SELECT_CLASS = (
    "🎓 **Select Class**\n\n"
    "Choose the class you want to search in:"
)

SEARCH_SELECT_SUBJECT = (
    "📚 **Select Subject**\n\n"
    "Choose the subject to search:"
)

SEARCH_SELECT_TAG = (
    "🏷️ **Select Tag**\n\n"
    "Choose a tag to filter by (or press Skip):"
)

SEARCH_SELECT_YEAR = (
    "📅 **Select Year**\n\n"
    "Choose the year for Centerlized exams:"
)

SEARCH_NO_RESULTS = (
    "😕 **No Results Found**\n\n"
    "No PDFs found for the selected criteria.\n\n"
    "Try different filters or start a new search."
)

SEARCH_RESULTS = (
    "📚 **Search Results**\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🎓 **Class:** `{pdf_class}`\n"
    "📖 **Subject:** `{subject}`\n"
    "🏷️ **Tag:** `{tag}`\n"
    "📄 **Found:** `{total}` PDFs\n"
    "📄 **Page:** `{page}/{total_pages}`\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
)

# ==================== PDF ACTIONS ====================

PDF_VIEW = (
    "📄 **{name}**\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🎓 **Class:** `{pdf_class}`\n"
    "📚 **Subject:** `{subject}`\n"
    "🏷️ **Tag:** `{tag}`\n"
    "👤 **Uploader:** `{uploader}`\n"
    "📅 **Date:** `{date}`\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
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
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "📛 **Name:** `{name}`\n"
    "🆔 **ID:** `{user_id}`\n"
    "📞 **Phone:** `{phone}`\n"
    "🎓 **Class:** `{class_}`\n"
    "📍 **Region:** `{region}`\n"
    "🏫 **School:** `{school}`\n"
    "📅 **Joined:** `{joined}`\n"
    "🕐 **Last Active:** `{last_active}`\n"
    "⏱️ **Member Since:** `{days_joined}` days\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "📊 **Statistics**\n"
    "📤 **Uploads:** `{uploads}`\n"
    "📥 **Downloads:** `{downloads}`\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "💰 **Pens**\n"
    "🖊️ **Available:** `{pens_available}`\n"
    "🎁 **Total Earned:** `{pens_earned}`\n"
    "📖 **Total Spent:** `{pens_spent}`\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🔗 **Referral Program**\n"
    "👥 **Referrals:** `{conversions}`\n"
)

REFERRAL_LINK_TEXT = (
    "\n🔗 **Your Referral Link**\n\n"
    "Share this link with friends:\n"
    "`https://t.me/{bot_username}?start=ref_{user_id}`\n\n"
    "Each referral gives you **+1 Pen** to browse PDFs!"
)

# ==================== SETTINGS ====================

SETTINGS_MENU = (
    "⚙️ **Settings**\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🔔 **New PDF Notifications:** {notification_status}\n\n"
    "When enabled, you'll receive alerts when new educational PDFs are uploaded.\n\n"
    "💡 **Tip:** Click the button below to toggle notifications."
)

SETTINGS_NOTIFICATION_TOGGLED = (
    "✅ **Notifications {status}**\n\n"
    "You will {action} receive alerts when new PDFs are uploaded."
)

# ==================== BROWSING ====================

BROWSING_START = (
    "📚 **PDF Browser**\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "💰 **Pen Balance:** `{pens}` pen(s)\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "Each PDF you view costs **1 pen**.\n"
    "You have {pdfs_per_pen} PDFs per pen available.\n\n"
    "Click **Next** to start browsing!"
)

BROWSING_NO_PENS = (
    "❌ **No Pens Available!**\n\n"
    "You need pens to browse PDFs.\n\n"
    "🔗 **How to get pens:**\n"
    "• Share your referral link with friends\n"
    "• Each new user who registers gives you **+1 pen**\n"
    "• 1 pen = {pdfs_per_pen} PDF views\n\n"
    "Share your referral link from the **Profile** menu!"
)

BROWSING_PDF_DISPLAY = (
    "📚 **PDF Browser**\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "💰 **Pens Remaining:** `{pens}`\n"
    "📖 **Page:** `{current}/{total}`\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "📄 **{name}**\n"
    "🎓 **Class:** `{pdf_class}`\n"
    "📚 **Subject:** `{subject}`\n"
    "🏷️ **Tag:** `{tag}`\n"
    "👤 **Uploader:** `{uploader}`\n"
    "❤️ **Likes:** `{likes}` | 📥 **Downloads:** `{downloads}`\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)

BROWSING_NO_MORE = (
    "📭 **No More PDFs**\n\n"
    "You've viewed all available PDFs in this session.\n\n"
    "💰 **Pens Remaining:** `{pens}`\n\n"
    "Start a new browsing session to see more PDFs!"
)

BROWSING_SESSION_EXPIRED = (
    "⏰ **Session Expired**\n\n"
    "Your browsing session has expired. Start a new session to continue."
)

# ==================== PDF NOTIFICATION ====================

NEW_PDF_NOTIFICATION = (
    "📢 **New PDF Available!**\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "📚 **Subject:** `{subject}`\n"
    "👤 **Uploaded by:** `{uploader_name}`\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🔍 **Click below to search and view this PDF:**"
)

NOTIFICATION_SEARCH_BUTTON = "🔍 Search PDFs"

# ==================== HELP ====================

HELP_TEXT = (
    "❓ **Help Center**\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "**📤 Upload PDF**\n"
    "Share educational materials with the community\n\n"
    "**🔍 Search PDFs**\n"
    "Find PDFs by class, subject, and tag\n\n"
    "**📚 Browse PDFs**\n"
    "Discover random PDFs using pens earned from referrals\n\n"
    "**👤 My Profile**\n"
    "View your stats, pens, and referral link\n\n"
    "**⚙️ Settings**\n"
    "Manage your notification preferences\n\n"
    "**🔗 Referral Program**\n"
    "Invite friends to earn pens for browsing\n\n"
    "**⚠️ Report**\n"
    "Report inappropriate content\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "**Need more help?**\n"
    "Contact our admin team via the button below."
)

# ==================== ADMIN ====================

ADMIN_PANEL = (
    "👑 **Admin Panel**\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "Select an option below:"
)

ADMIN_STATS = (
    "📊 **System Statistics**\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "👥 **Total Users:** `{total_users}`\n"
    "📄 **Total PDFs:** `{total_pdfs}`\n"
    "📥 **Total Downloads:** `{total_downloads}`\n"
    "⏳ **Pending PDFs:** `{pending_pdfs}`\n"
    "🚨 **Pending Reports:** `{total_reports}`\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)

ADMIN_USER_LIST = "👥 **User List**\n\n"
ADMIN_USER_ITEM = "{status}{role} **{name}**\n   ├ ID: `{id}`\n   └ {class_name} @ {school}\n\n"

ADMIN_PDF_PENDING_LIST = "⏳ **Pending PDFs**\n\n"
ADMIN_PDF_PENDING_ITEM = "{number}. **{name}**\n   📚 {subject} | {tag} | 🎓 {pdf_class}\n   👤 {uploader}\n   🆔 `{id}`\n"

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
    "After sending, click the button below to confirm."
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
    "├ 📚 Browse PDFs with Pens\n"
    "├ 👤 Track Your Profile\n"
    "├ ⚙️ Manage Settings\n"
    "└ 🔗 Share Referral Links\n\n"
    "Let's get started!"
)

MEMBERSHIP_REFRESH = "✅ Status refreshed!"
MEMBERSHIP_CONTINUE = "🎉 Welcome to Ardayda Bot!"

# ==================== EMPTY STATES ====================

EMPTY_UPLOADS = "📭 **No Uploads Found**\n\nThis user hasn't uploaded any PDFs yet."
EMPTY_DOWNLOADS = "📭 **No Downloads Found**\n\nThis user hasn't downloaded any PDFs yet."
EMPTY_REQUIREMENTS = "📭 **No Requirements Found**\n\nNo membership requirements have been set up."
EMPTY_REPORTS = "📭 **No Reports Found**\n\nThere are no pending reports."
EMPTY_PDFS = "📭 **No PDFs Found**\n\nNo PDFs match your search criteria."
EMPTY_BROWSING = "📭 **No PDFs Available**\n\nThere are no approved PDFs in the system yet."

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

ERROR_NOT_FOUND = "❌ **Not Found**"
ERROR_PERMISSION = "❌ **Permission Denied** You don't have access to this."
ERROR_GENERIC = "❌ **Error** Please try again later."