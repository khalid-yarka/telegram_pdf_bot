# bots/ardayda_bot/text.py

# ---------- REGISTRATION ----------

REG_NAME = (
    "👋 Welcome!\n\n"
    "Please enter your *full name* to complete registration."
)

REG_SUCCESS = (
    "✅ Registration completed successfully.\n\n"
    "You can now upload and search PDFs using the menu below."
)

REG_IN_PROGRESS_BLOCK = (
    "⚠️ Registration is still in progress.\n"
    "Please complete it before using other features."
)

REG_REGION = (
    "📍 *Select Your Region*\n\n"
    "Choose your region from the list below:"
)

REG_SCHOOL = (
    "🏫 *Select Your School*\n\n"
    "📍 *Region:* {region}\n\n"
    "Choose your school from the list below:"
)

REG_CLASS = (
    "🎓 *Select Your Class*\n\n"
    "Choose your class:"
)

REG_PHONE = (
    "📞 *Phone Number*\n\n"
    "Please share your phone number using the button below."
)

# School data by region (used in registration)
form_four_schools_by_region = {
    "BARI": [
        "Bandar Qasim",
        "Bari",
        "Garisa",
        "Salahudin",
        "Ras Asayr Bosaso",
        "Omar bin Abdazis",
        "Bosaso Public",
        "Bender Siyaad Qaw",
        "White Tower",
        "Xalane Bosaso",
        "Iftiin Bosaso",
        "Sayid Mohamed Bosaso",
        "Xamdan",
        "Ganaane",
        "Dr Ahmed Bosaso",
        "Iman Nawawi Bosaso",
        "Ugas Yasin",
        "Imam shafie Bosaso",
        "Mocalin Jama Bosaso",
        "Najax",
        "Biyo kulule Bosaso",
        "Haji Yasin",
        "Girible",
        "Mohamed Awale",
        "Haji Salad",
        "Carta",
        "Jaamu Maalik",
        "Eldahir"
    ],
    "NUGAAL": [
        "Imamu Nawawi Garowe F4",
        "DR. Ahmed Garowe F4",
        "Awr Culus F4",
        "Sh. Hamid F4",
        "Nugal F4",
        "Daawad Garowe F4",
        "Gambol F4",
        "Al-Xikma Garowe F4",
        "Al Waxa F4",
        "Kobciye F4",
        "Alculum F4",
        "Xar xaar F4",
        "Dr ahmed Burtinle F4",
        "Burtinle F4",
        "Muntada Burtinle F4",
        "Xasbahalle F4",
        "Sare Qarxis F4",
        "Sare Eyl F4",
        "Sare Sinujjil F4",
        "Sare Negeye F4",
        "Sare Usgure F4",
        "Sare Yoonbays F4",
        "Sare Jalam F4"
    ],
    "KARKAAR": [
        "Qoton",
        "Dhuudo",
        "Dhudhub",
        "Humbays",
        "Qarrasoor",
        "Hidda",
        "Uurjire",
        "Sheerbi",
        "Suldaan Mubarak (Yeka)",
        "Al-Muntada",
        "Ali Afyare",
        "Kubo",
        "Xaaji Aaden",
        "Xaaji Osman"
    ],
    "MUDUG": [
        "1st August",
        "Africa",
        "Dr.Ahmed Galkoio",
        "A.A.Sharmarke",
        "Yamays",
        "Ilays galkaoi",
        "Beyra",
        "Garsoor",
        "Omar Samatar",
        "Haji Ali Bihi",
        "Agoonta Qaran F4",
        "Al-xigma",
        "Hala booqad",
        "Haji Dirie",
        "Yasin Nor",
        "Sare Bacaaadwayn F4",
        "Bacadweyn",
        "Hema",
        "Barbarshe",
        "Bursalah",
        "Golden 18+",
        "Hope",
        "GECPD Xarlo",
        "Cagaraan F4",
        "Sare Garacad",
        "Balli busle F4",
        "Sare Jarriban",
        "Sare Galdogob"
    ],
    "HAYLAAN": [
        "Sare Dhahar Public",
        "Kala-dhac",
        "Salaxudin-Dhahar",
        "Buraan",
        "Dalmar Qol",
        "Damalla Xagarre",
        "Sare Damalla xagarre",
        "Sare Shimbiraale"
    ],
    "RAAS CASAYR": [
        "Maxamed Xuseen",
        "Bareeda",
        "Caluula",
        "Xabbob"
    ],
    "SANAAG": [
        "Al Furqan Badhan",
        "Al-Nuur Badhan",
        "Al-Rahma Badhan",
        "Badhan Sec",
        "Farax-cadde",
        "Hadaftimo",
        "Yubbe",
        "Armale",
        "Rad",
        "Midigale"
    ]
}

# ==================== MANUAL ENTRY BUTTONS ====================
BUTTON_REGION_NOT_LISTED = "📍 Region not listed? ✏️"
BUTTON_SCHOOL_NOT_LISTED = "🏫 School not listed? ✏️"

# ==================== MANUAL ENTRY TEXTS ====================
MANUAL_REGION_PROMPT = (
    "✏️ *Enter Region Manually*\n\n"
    "Please type the name of your region.\n\n"
    "📝 *Example:* `Banaadir`, `Woqooyi Galbeed`, `Jubbada Hoose`\n\n"
    "Type *Cancel* to go back."
)

MANUAL_SCHOOL_PROMPT = (
    "✏️ *Enter School Manually*\n\n"
    "📍 *Region:* `{region}`\n\n"
    "Please type the name of your school.\n\n"
    "📝 *Example:* `Al-Furqan School`, `Central High School`\n\n"
    "Type *Cancel* to go back."
)

# ==================== ADMIN NOTIFICATION ====================
ADMIN_MANUAL_ENTRY_NOTIFICATION = (
    "🔔 *⚠️ MISSING {entry_type} REPORT ⚠️*\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "📢 *{entry_type} Not Found in Database*\n"
    "━━━━━━━━━━━━━━━━━━━━━\n\n"
    "👤 *User Information*\n"
    "├ *Name:* `{user_name}`\n"
    "├ *User ID:* `{user_id}`\n"
    "└ *Phone:* `{user_phone or 'Not provided'}`\n\n"
    "{location_info}\n"
    "📅 *Date:* `{date}`\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "> Please add this {entry_type_lower} to the database."
)

SUBJECTS = ["Math", "Physics", "Chemistry", "Biology", "ICT", "Arabic", "Islamic", "English", "Somali", "G.P", "Geography", "History", "Agriculture", "Business"]

TAGS = ["Exam", "Notes", "Summary", "Assignment", "Chapter Reviews"]

# ---------- GENERAL ----------

HOME_WELCOME = (
    "🏠 *Main Menu*\n\n"
    "Choose what you want to do:"
)

CANCELLED = (
    "❌ Operation cancelled.\n\n"
    "You are back at the main menu."
)

SESSION_EXPIRED = (
    "⚠️ This session has expired.\n"
    "Please start again from the main menu."
)

CONFLICT_UPLOAD = (
    "⚠️ You are currently uploading a PDF.\n"
    "Finish it or tap ❌ Cancel before doing something else."
)

CONFLICT_SEARCH = (
    "⚠️ You are currently searching.\n"
    "Finish it or tap ❌ Cancel before starting a new action."
)

UNKNOWN_INPUT = (
    "ℹ️ Please use the buttons provided.\n"
    "\n..."
)

CHANNEL_REQUIRED = (
    "🔒 *Channel Membership Required*\n\n"
    "To use this bot, you must join our official channel first.\n\n"
    "Please join the channel below and then click *I've Joined*."
)

CHANNEL_JOIN_BUTTON = "📢 Join Channel"
CHANNEL_CHECK_BUTTON = "✅ I've Joined"

NOT_REGISTERED = "❌ You need to register first. Please type /start to begin."
ACCOUNT_SUSPENDED = "🚫 Your account has been suspended. Please contact an admin."

# ---------- UPLOAD FLOW ----------

UPLOAD_START = (
    "📤 *Upload PDF*\n\n"
    "Please send your PDF file."
)

UPLOAD_INVALID_FILE = (
    "❌ Invalid file.\n"
    "Please send a valid *PDF document*."
)

UPLOAD_TOO_LARGE = (
    "❌ File too large.\n"
    "Maximum size is {max_size}MB."
)

UPLOAD_ALREADY_EXISTS = (
    "⚠️ This PDF already exists in the system.\n"
    "Upload cancelled."
)

UPLOAD_SUBJECT = (
    "📝 *Choose Subject*\n\n"
    "Select the subject for this PDF:"
)

UPLOAD_TAG = (
    "🏷️ *Select Tag*\n\n"
    "Choose a tag for this PDF:"
)

UPLOAD_YEAR_PROMPT = (
    "📅 *Select Year*\n\n"
    "Please select the exam year:"
)

UPLOAD_SUCCESS = (
    "🎉 *Upload Completed!*\n\n"
    "Your PDF has been successfully uploaded.\n"
    "🆔 *PDF ID:* `{pdf_id}`"
)

UPLOAD_FAILED = (
    "❌ Upload failed due to an internal error.\n"
    "Please try again later."
)

# ---------- SEARCH FLOW ----------

SEARCH_START = (
    "🔍 *Search PDFs*\n\n"
    "Select a subject to search:"
)

SEARCH_SUBJECT_SELECTED = (
    "🔍 Subject: *{subject}*\n\n"
    "Now select a tag (optional):"
)

SEARCH_YEAR_PROMPT = (
    "📅 Select year (or skip):"
)

SEARCH_NO_RESULTS = (
    "😕 No PDFs found for the selected criteria."
)

SEARCH_RESULTS = (
    "📚 *Search Results* (Page {page}/{total_pages})\n\n"
)

SEARCH_RESULT_ITEM = (
    "{number}. *{name}*\n"
    "   📚 {subject} | {tag} | ❤️ {likes}\n"
    "   🆔 `{id}`\n"
)

SEARCH_NEW = "🔄 New Search"

# ---------- PDF ACTION ----------

PDF_VIEW = (
    "📄 *{name}*\n\n"
    "📚 *Subject:* {subject}\n"
    "🏷️ *Tag:* {tag}\n"
    "👤 *Uploaded by:* {uploader}\n"
    "📅 *Date:* {date}\n"
    "📥 *Downloads:* {downloads}\n"
    "❤️ *Likes:* {likes}\n"
)

PDF_DOWNLOAD_STARTED = "✅ PDF sent! Check your chat."
PDF_DOWNLOAD_FAILED = "❌ Failed to send PDF."

PDF_LIKED = "❤️ Liked!"
PDF_UNLIKED = "💔 Unliked"

PDF_REPORT_PROMPT = (
    "📢 *Report PDF*\n\n"
    "Please describe why you are reporting this PDF."
)

PDF_REPORT_SENT = "✅ Report sent. Thank you!"

REPORT_NOTIFY_UPLOADER = (
    "⚠️ *Your PDF has been reported*\n\n"
    "PDF: {pdf_name}\n"
    "Reason: {reason}"
)

REPORT_NOTIFY_ADMIN = (
    "⚠️ *New Report*\n\n"
    "PDF: {pdf_name} (ID: {pdf_id})\n"
    "Uploader: {uploader}\n"
    "Reporter: {reporter}\n"
    "Reason: {reason}"
)

# ---------- PROFILE ----------

PROFILE_HEADER = (
    "👤 *Your Profile*\n\n"
)

PROFILE_DISPLAY = (
    "👤 *Profile: {name}*\n\n"
    "📱 User ID: `{user_id}`\n"
    "📞 Phone: {phone}\n"
    "🎓 Class: {class}\n"
    "📍 Region: {region}\n"
    "🏫 School: {school}\n"
    "📅 Joined: {joined}\n\n"
    "📊 *Statistics*\n"
    "📤 Uploads: {uploads}\n"
    "📥 Downloads: {downloads}\n"
)

PROFILE_NO_UPLOADS = (
    "📭 You haven't uploaded any PDFs yet."
)

PROFILE_REFERRAL = (
    "\n🔗 *Referral Program*\n\n"
    "Share your link:\n"
    "`https://t.me/{bot_username}?start=ref_{user_id}`\n\n"
    "✅ Referrals: {conversions}"
)

# ---------- HELP ----------

HELP_TEXT = (
    "❓ *Bot Help*\n\n"
    "*Commands:*\n"
    "/start - Main menu\n"
    "/help - Show this help\n\n"
    "*Features:*\n"
    "📤 *Upload PDF* - Share educational materials\n"
    "🔍 *Search PDFs* - Find PDFs by subject\n"
    "👤 *Profile* - View your stats\n"
    "🔗 *Referral* - Invite friends\n"
)

# ---------- ADMIN ----------

ADMIN_PANEL = "👑 *Admin Panel*\n\nSelect an option:"

ADMIN_STATS = (
    "📊 *System Statistics*\n\n"
    "👥 Users: {total_users}\n"
    "📄 PDFs: {total_pdfs}\n"
    "📥 Downloads: {total_downloads}\n"
    "⏳ Pending: {pending_pdfs}\n"
    "🚨 Reports: {total_reports}"
)

ADMIN_USER_LIST = "👥 *User List*\n\n"
ADMIN_USER_ITEM = "{status}{role} *{name}*\n   ├ ID: `{id}`\n   └ {class} @ {school}\n\n"

ADMIN_PDF_PENDING_LIST = "⏳ *Pending PDFs*\n\n"
ADMIN_PDF_PENDING_ITEM = "{number}. *{name}*\n   📚 {subject} | {tag}\n   👤 {uploader}\n   🆔 `{id}`\n"

ADMIN_REPORT_LIST = "🚨 *Pending Reports*\n\n"
ADMIN_REPORT_ITEM = "{number}. PDF: *{pdf_name}* (ID: {pdf_id})\n   👤 {reporter}\n   💬 {reason}\n"

ADMIN_BROADCAST_PROMPT = "📢 *Send Broadcast*\n\nType your message:"
ADMIN_BROADCAST_CONFIRM = "✅ Broadcast sent to {count} users."

ADMIN_SQL_PROMPT = "🔧 *SQL Console*\n\nEnter SQL query:"
ADMIN_SQL_RESULT = "```\n{result}\n```"

ADMIN_PDF_APPROVE_SUCCESS = "✅ PDF approved!"
ADMIN_PDF_DELETE_SUCCESS = "✅ PDF deleted!"
ADMIN_REPORT_RESOLVE_SUCCESS = "✅ Report resolved."

# Add this line in the UPLOAD FLOW TEXTS section
UPLOAD_FILE_PROMPT = "📤 *Upload PDF via File*\n\nPlease send me the PDF file you want to upload."
# ---------- BUTTONS ----------

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
BUTTON_NEXT = "▶️ Next"
BUTTON_PREV = "◀️ Prev"
BUTTON_SKIP = "⏭️ Skip"
BUTTON_FILE = "📄 Upload File"

# ---------- ERRORS ----------

ERROR_NOT_FOUND = "❌ Not found."
ERROR_SESSION_EXPIRED = "⚠️ Session expired. Please start over."
ERROR_PERMISSION = "❌ You do not have permission."
ERROR_GENERIC = "❌ An error occurred. Please try again later."