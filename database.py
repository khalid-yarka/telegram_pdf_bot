# telegram_pdf_bot/database.py
# SQLite3 database operations with timezone support (Somalia)
# Updated with clean tag system (Unclassified only)

import sqlite3
import json
import os
from contextlib import contextmanager
from config import DATABASE_PATH, DEBUG, DEFAULT_SETTINGS
from utils import get_current_time

# Ensure instance directory exists
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    if DEBUG:
        print(f"📁 Database path: {DATABASE_PATH}")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # ==================== USERS TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                phone TEXT,
                region TEXT,
                school TEXT,
                class TEXT,
                join_date TIMESTAMP,
                last_active TIMESTAMP,
                is_banned BOOLEAN DEFAULT 0,
                is_admin BOOLEAN DEFAULT 0,
                referred_by INTEGER,
                referral_notified BOOLEAN DEFAULT 0,
                FOREIGN KEY (referred_by) REFERENCES users(user_id)
            )
        ''')
        
        # Add missing columns if needed
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'last_active' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN last_active TIMESTAMP')
        if 'referral_notified' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN referral_notified BOOLEAN DEFAULT 0')
        
        # ==================== PDFS TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pdfs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT,
                file_name TEXT,
                uploaded_by INTEGER,
                upload_date TIMESTAMP,
                subject TEXT,
                tag TEXT,
                class TEXT,
                exam_year INTEGER,
                download_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                is_approved BOOLEAN DEFAULT 0,
                source TEXT,
                FOREIGN KEY (uploaded_by) REFERENCES users(user_id)
            )
        ''')
        
        # Add class column if missing
        cursor.execute("PRAGMA table_info(pdfs)")
        pdf_columns = [col[1] for col in cursor.fetchall()]
        if 'class' not in pdf_columns:
            cursor.execute('ALTER TABLE pdfs ADD COLUMN class TEXT')
        
        # ==================== USER LIKES TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_likes (
                user_id INTEGER,
                pdf_id INTEGER,
                PRIMARY KEY (user_id, pdf_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (pdf_id) REFERENCES pdfs(id)
            )
        ''')
        
        # ==================== DOWNLOADS LOG TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pdf_id INTEGER,
                user_id INTEGER,
                download_date TIMESTAMP,
                FOREIGN KEY (pdf_id) REFERENCES pdfs(id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # ==================== USER STATE TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_state (
                user_id INTEGER PRIMARY KEY,
                state TEXT,
                data TEXT,
                updated_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # ==================== REPORTS TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pdf_id INTEGER,
                reported_by INTEGER,
                report_text TEXT,
                report_date TIMESTAMP,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (pdf_id) REFERENCES pdfs(id),
                FOREIGN KEY (reported_by) REFERENCES users(user_id)
            )
        ''')
        
        # ==================== REQUIREMENTS TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                link TEXT NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES users(user_id)
            )
        ''')
        
        # ==================== WHATSAPP VERIFICATIONS TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whatsapp_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                requirement_id INTEGER,
                verified_at TIMESTAMP,
                verification_code TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (requirement_id) REFERENCES requirements(id)
            )
        ''')
        
        # ==================== MEMBERSHIPS TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memberships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                requirement_id INTEGER,
                joined_at TIMESTAMP,
                last_checked TIMESTAMP,
                is_member BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (requirement_id) REFERENCES requirements(id),
                UNIQUE(user_id, requirement_id)
            )
        ''')
        
        # ==================== USER MEMBERSHIP TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_membership (
                user_id INTEGER PRIMARY KEY,
                membership_message_id INTEGER,
                whatsapp_reminder_count INTEGER DEFAULT 0,
                whatsapp_confirmed BOOLEAN DEFAULT 0,
                telegram_confirmed BOOLEAN DEFAULT 0,
                last_checked TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # ==================== MEMBERSHIP EVENTS TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS membership_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                requirement_id INTEGER,
                event_type TEXT,
                event_date TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (requirement_id) REFERENCES requirements(id)
            )
        ''')
        
        # ==================== BOT SETTINGS TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE,
                setting_value TEXT,
                description TEXT,
                updated_at TIMESTAMP,
                updated_by INTEGER,
                FOREIGN KEY (updated_by) REFERENCES users(user_id)
            )
        ''')
        
        # ==================== USER SETTINGS TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                new_pdf_notifications BOOLEAN DEFAULT 1,
                updated_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # ==================== USER PENS TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_pens (
                user_id INTEGER PRIMARY KEY,
                pens_available INTEGER DEFAULT 0,
                total_earned INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                last_updated TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # ==================== BROWSING HISTORY TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS browsing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                pdf_id INTEGER,
                viewed_at TIMESTAMP,
                pen_spent INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (pdf_id) REFERENCES pdfs(id) ON DELETE CASCADE
            )
        ''')
        
        # ==================== BROWSING SESSIONS TABLE ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS browsing_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                current_pdf_index INTEGER DEFAULT 0,
                viewed_pdfs TEXT,
                created_at TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Insert default settings if they don't exist
        for key, value in DEFAULT_SETTINGS.items():
            cursor.execute('''
                INSERT OR IGNORE INTO bot_settings (setting_key, setting_value, description, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (key, value, f"Default setting for {key}", get_current_time()))
        
        if DEBUG:
            print("✅ Database tables created/verified successfully")
            print(f"📊 Default settings initialized: {len(DEFAULT_SETTINGS)} settings")

# ==================== USER FUNCTIONS ====================

def add_user(user_id, full_name, phone=None, region=None, school=None, class_name=None, referred_by=None):
    """Add or update user, returns referred_by for notification"""
    current_time = get_current_time()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        existing = cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE users SET
                    full_name = COALESCE(?, full_name),
                    phone = COALESCE(?, phone),
                    region = COALESCE(?, region),
                    school = COALESCE(?, school),
                    class = COALESCE(?, class),
                    last_active = ?
                WHERE user_id = ?
            ''', (full_name, phone, region, school, class_name, current_time, user_id))
            
            if DEBUG:
                print(f"📝 User updated: {user_id} - {full_name}")
            return None
        
        cursor.execute('''
            INSERT INTO users 
            (user_id, full_name, phone, region, school, class, join_date, last_active, is_banned, is_admin, referred_by, referral_notified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, 0)
        ''', (user_id, full_name, phone, region, school, class_name, current_time, current_time, referred_by))
        
        # Initialize user settings
        cursor.execute('''
            INSERT OR IGNORE INTO user_settings (user_id, new_pdf_notifications, updated_at)
            VALUES (?, 1, ?)
        ''', (user_id, current_time))
        
        # Initialize user pens
        cursor.execute('''
            INSERT OR IGNORE INTO user_pens (user_id, pens_available, total_earned, total_spent, last_updated)
            VALUES (?, 0, 0, 0, ?)
        ''', (user_id, current_time))
        
        if DEBUG:
            print(f"📝 New user added: {user_id} - {full_name}")
            if referred_by:
                print(f"🔗 Referred by: {referred_by}")
        
        return referred_by

def update_user_activity(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_active = ? WHERE user_id = ?', (get_current_time(), user_id))

def get_user(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return cursor.fetchone()

def user_exists(user_id):
    return get_user(user_id) is not None

def update_user_phone(user_id, phone):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET phone = ? WHERE user_id = ?', (phone, user_id))

def update_user_region_school_class(user_id, region, school, class_name):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET region = ?, school = ?, class = ? WHERE user_id = ?', 
                       (region, school, class_name, user_id))

def ban_user(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
        if DEBUG:
            print(f"🚫 User banned: {user_id}")

def unban_user(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
        if DEBUG:
            print(f"✅ User unbanned: {user_id}")

def set_admin(user_id, is_admin=True):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_admin = ? WHERE user_id = ?', (1 if is_admin else 0, user_id))
        if DEBUG:
            print(f"👑 Admin status updated for {user_id}: {is_admin}")

def get_all_users(limit=None, offset=0):
    with get_db() as conn:
        cursor = conn.cursor()
        if limit:
            cursor.execute('SELECT * FROM users ORDER BY join_date DESC LIMIT ? OFFSET ?', (limit, offset))
        else:
            cursor.execute('SELECT * FROM users ORDER BY join_date DESC')
        return cursor.fetchall()

def count_users():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        return cursor.fetchone()[0]

def get_user_download_count(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM downloads WHERE user_id = ?', (user_id,))
        return cursor.fetchone()[0]

def get_user_upload_count(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM pdfs WHERE uploaded_by = ? AND is_approved = 1', (user_id,))
        return cursor.fetchone()[0]

def get_user_referral_stats(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE referred_by = ?', (user_id,))
        conversions = cursor.fetchone()[0]
        return {'conversions': conversions}

def mark_referral_notified(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET referral_notified = 1 WHERE user_id = ?', (user_id,))

def get_referrer_notification_status(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT referral_notified FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return row['referral_notified'] == 1 if row else False

# ==================== PDF FUNCTIONS ====================

def add_pdf(file_id, file_name, user_id, subject, tag, pdf_class, exam_year=None):
    """Add a new PDF with class information"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pdfs 
            (file_id, file_name, uploaded_by, upload_date, subject, tag, class, exam_year, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (file_id, file_name, user_id, get_current_time(), subject, tag, pdf_class, exam_year, 'upload'))
        pdf_id = cursor.lastrowid
        if DEBUG:
            print(f"📄 PDF added: ID={pdf_id}, Name={file_name}, User={user_id}, Class={pdf_class}, Tag={tag}")
        return pdf_id

def approve_pdf(pdf_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE pdfs SET is_approved = 1 WHERE id = ?', (pdf_id,))
        if DEBUG:
            print(f"✅ PDF approved: {pdf_id}")

def delete_pdf(pdf_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM pdfs WHERE id = ?', (pdf_id,))
        cursor.execute('DELETE FROM user_likes WHERE pdf_id = ?', (pdf_id,))
        cursor.execute('DELETE FROM downloads WHERE pdf_id = ?', (pdf_id,))
        cursor.execute('DELETE FROM reports WHERE pdf_id = ?', (pdf_id,))
        cursor.execute('DELETE FROM browsing_history WHERE pdf_id = ?', (pdf_id,))
        if DEBUG:
            print(f"🗑️ PDF deleted: {pdf_id}")

def get_pdf(pdf_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pdfs WHERE id = ?', (pdf_id,))
        return cursor.fetchone()

def get_unapproved_pdfs():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pdfs WHERE is_approved = 0 ORDER BY upload_date DESC')
        return cursor.fetchall()

def get_pdfs_by_filters(subject=None, tag=None, pdf_class=None, exam_year=None, uploaded_by=None, approved_only=True, limit=10, offset=0):
    """Get PDFs with filters including class"""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM pdfs WHERE 1=1"
        params = []
        
        if subject:
            query += " AND subject = ?"
            params.append(subject)
        if tag:
            query += " AND tag = ?"
            params.append(tag)
        if pdf_class:
            query += " AND class = ?"
            params.append(pdf_class)
        if exam_year:
            query += " AND exam_year = ?"
            params.append(exam_year)
        if uploaded_by:
            query += " AND uploaded_by = ?"
            params.append(uploaded_by)
        if approved_only:
            query += " AND is_approved = 1"
        
        query += " ORDER BY upload_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        cursor.execute(query, params)
        return cursor.fetchall()

def count_pdfs_by_filters(subject=None, tag=None, pdf_class=None, exam_year=None, uploaded_by=None, approved_only=True):
    """Count PDFs with filters including class"""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM pdfs WHERE 1=1"
        params = []
        
        if subject:
            query += " AND subject = ?"
            params.append(subject)
        if tag:
            query += " AND tag = ?"
            params.append(tag)
        if pdf_class:
            query += " AND class = ?"
            params.append(pdf_class)
        if exam_year:
            query += " AND exam_year = ?"
            params.append(exam_year)
        if uploaded_by:
            query += " AND uploaded_by = ?"
            params.append(uploaded_by)
        if approved_only:
            query += " AND is_approved = 1"
        
        cursor.execute(query, params)
        return cursor.fetchone()[0]

def get_random_pdfs(limit=1, exclude_ids=None):
    """Get random approved PDFs for browsing"""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM pdfs WHERE is_approved = 1"
        params = []
        
        if exclude_ids and len(exclude_ids) > 0:
            placeholders = ','.join('?' * len(exclude_ids))
            query += f" AND id NOT IN ({placeholders})"
            params.extend(exclude_ids)
        
        query += " ORDER BY RANDOM() LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        return cursor.fetchall()

def increment_download(pdf_id, user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE pdfs SET download_count = download_count + 1 WHERE id = ?', (pdf_id,))
        cursor.execute('INSERT INTO downloads (pdf_id, user_id, download_date) VALUES (?, ?, ?)',
                       (pdf_id, user_id, get_current_time()))
        if DEBUG:
            print(f"📥 Download recorded: PDF={pdf_id}, User={user_id}")

def like_pdf(pdf_id, user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_likes WHERE user_id = ? AND pdf_id = ?', (user_id, pdf_id))
        if cursor.fetchone():
            return False
        cursor.execute('INSERT INTO user_likes (user_id, pdf_id) VALUES (?, ?)', (user_id, pdf_id))
        cursor.execute('UPDATE pdfs SET like_count = like_count + 1 WHERE id = ?', (pdf_id,))
        return True

def unlike_pdf(pdf_id, user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_likes WHERE user_id = ? AND pdf_id = ?', (user_id, pdf_id))
        cursor.execute('UPDATE pdfs SET like_count = like_count - 1 WHERE id = ?', (pdf_id,))

def has_liked(pdf_id, user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_likes WHERE user_id = ? AND pdf_id = ?', (user_id, pdf_id))
        return cursor.fetchone() is not None

# ==================== STATE FUNCTIONS ====================

def set_user_state(user_id, state, data=None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_state (user_id, state, data, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, state, json.dumps(data) if data else None, get_current_time()))

def get_user_state(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT state, data FROM user_state WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            return row['state'], json.loads(row['data']) if row['data'] else None
        return None, None

def clear_user_state(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_state WHERE user_id = ?', (user_id,))

# ==================== REPORT FUNCTIONS ====================

def add_report(pdf_id, reported_by, report_text):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reports (pdf_id, reported_by, report_text, report_date)
            VALUES (?, ?, ?, ?)
        ''', (pdf_id, reported_by, report_text, get_current_time()))
        report_id = cursor.lastrowid
        if DEBUG:
            print(f"⚠️ Report added: ID={report_id}, PDF={pdf_id}, User={reported_by}")
        return report_id

def get_pending_reports():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.full_name as reporter_name, p.file_name as pdf_name
            FROM reports r
            JOIN users u ON r.reported_by = u.user_id
            JOIN pdfs p ON r.pdf_id = p.id
            WHERE r.status = 'pending'
            ORDER BY r.report_date DESC
        ''')
        return cursor.fetchall()

def resolve_report(report_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE reports SET status = ? WHERE id = ?', ('resolved', report_id))
        if DEBUG:
            print(f"✅ Report resolved: {report_id}")

# ==================== MEMBERSHIP FUNCTIONS ====================

def add_requirement(name, req_type, link, description, created_by):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requirements (name, type, link, description, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, req_type, link, description, get_current_time(), created_by))
        req_id = cursor.lastrowid
        if DEBUG:
            print(f"➕ Requirement added: {name} ({req_type})")
        return req_id

def get_requirements(active_only=True):
    with get_db() as conn:
        cursor = conn.cursor()
        if active_only:
            cursor.execute('SELECT * FROM requirements WHERE is_active = 1 ORDER BY id')
        else:
            cursor.execute('SELECT * FROM requirements ORDER BY id')
        return cursor.fetchall()

def get_requirement(req_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM requirements WHERE id = ?', (req_id,))
        return cursor.fetchone()

def toggle_requirement(req_id, is_active):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE requirements SET is_active = ? WHERE id = ?', (1 if is_active else 0, req_id))
        if DEBUG:
            print(f"🔄 Requirement {req_id} toggled to {is_active}")

def delete_requirement(req_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM requirements WHERE id = ?', (req_id,))
        cursor.execute('DELETE FROM whatsapp_verifications WHERE requirement_id = ?', (req_id,))
        cursor.execute('DELETE FROM memberships WHERE requirement_id = ?', (req_id,))
        if DEBUG:
            print(f"🗑️ Requirement deleted: {req_id}")

def record_membership(user_id, requirement_id, is_member):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO memberships (user_id, requirement_id, joined_at, last_checked, is_member)
            VALUES (?, ?, COALESCE((SELECT joined_at FROM memberships WHERE user_id = ? AND requirement_id = ?), ?), ?, ?)
        ''', (user_id, requirement_id, user_id, requirement_id, get_current_time() if is_member else None, get_current_time(), 1 if is_member else 0))

def get_user_memberships(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, m.is_member, m.joined_at, m.last_checked
            FROM requirements r
            LEFT JOIN memberships m ON r.id = m.requirement_id AND m.user_id = ?
            WHERE r.is_active = 1
        ''', (user_id,))
        return cursor.fetchall()

def is_telegram_member_recorded(user_id, requirement_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT is_member FROM memberships WHERE user_id = ? AND requirement_id = ?', (user_id, requirement_id))
        row = cursor.fetchone()
        return row['is_member'] == 1 if row else False

def add_whatsapp_verification(user_id, requirement_id, verification_code):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO whatsapp_verifications (user_id, requirement_id, verified_at, verification_code)
            VALUES (?, ?, ?, ?)
        ''', (user_id, requirement_id, get_current_time(), verification_code))
        if DEBUG:
            print(f"📱 WhatsApp verification added for user {user_id}, requirement {requirement_id}")

def is_whatsapp_verified(user_id, requirement_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM whatsapp_verifications WHERE user_id = ? AND requirement_id = ?', (user_id, requirement_id))
        return cursor.fetchone() is not None

def get_whatsapp_verification(user_id, requirement_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM whatsapp_verifications WHERE user_id = ? AND requirement_id = ?', (user_id, requirement_id))
        return cursor.fetchone()

def get_all_membership_stats():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.id, r.name, r.type, r.link,
                   COUNT(DISTINCT m.user_id) as members,
                   (SELECT COUNT(*) FROM users) as total_users
            FROM requirements r
            LEFT JOIN memberships m ON r.id = m.requirement_id AND m.is_member = 1
            WHERE r.is_active = 1
            GROUP BY r.id
        ''')
        return cursor.fetchall()

# ==================== STATISTICS ====================

def get_stats():
    with get_db() as conn:
        cursor = conn.cursor()
        total_users = cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        total_pdfs = cursor.execute('SELECT COUNT(*) FROM pdfs WHERE is_approved = 1').fetchone()[0]
        total_downloads = cursor.execute('SELECT SUM(download_count) FROM pdfs').fetchone()[0] or 0
        pending_pdfs = cursor.execute('SELECT COUNT(*) FROM pdfs WHERE is_approved = 0').fetchone()[0]
        total_reports = cursor.execute('SELECT COUNT(*) FROM reports WHERE status = "pending"').fetchone()[0]
        return {
            'total_users': total_users,
            'total_pdfs': total_pdfs,
            'total_downloads': total_downloads,
            'pending_pdfs': pending_pdfs,
            'total_reports': total_reports,
        }

# ==================== MEMBERSHIP TRACKING FUNCTIONS ====================

def set_user_membership_message(user_id, message_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM user_membership WHERE user_id = ?', (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute('''
                UPDATE user_membership 
                SET membership_message_id = ?, last_checked = ?
                WHERE user_id = ?
            ''', (message_id, get_current_time(), user_id))
        else:
            cursor.execute('''
                INSERT INTO user_membership (user_id, membership_message_id, last_checked)
                VALUES (?, ?, ?)
            ''', (user_id, message_id, get_current_time()))

def get_user_membership_message(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT membership_message_id FROM user_membership WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return row['membership_message_id'] if row else None

def set_whatsapp_confirmed(user_id, confirmed=True):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM user_membership WHERE user_id = ?', (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute('''
                UPDATE user_membership 
                SET whatsapp_confirmed = ?, last_checked = ?
                WHERE user_id = ?
            ''', (1 if confirmed else 0, get_current_time(), user_id))
        else:
            cursor.execute('''
                INSERT INTO user_membership (user_id, whatsapp_confirmed, last_checked)
                VALUES (?, ?, ?)
            ''', (user_id, 1 if confirmed else 0, get_current_time()))

def get_whatsapp_confirmed(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT whatsapp_confirmed FROM user_membership WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return row['whatsapp_confirmed'] == 1 if row else False

def increment_whatsapp_reminder(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM user_membership WHERE user_id = ?', (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute('''
                UPDATE user_membership 
                SET whatsapp_reminder_count = whatsapp_reminder_count + 1, last_checked = ?
                WHERE user_id = ?
            ''', (get_current_time(), user_id))
        else:
            cursor.execute('''
                INSERT INTO user_membership (user_id, whatsapp_reminder_count, last_checked)
                VALUES (?, 1, ?)
            ''', (user_id, get_current_time()))

def get_whatsapp_reminder_count(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT whatsapp_reminder_count FROM user_membership WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return row['whatsapp_reminder_count'] if row else 0

def log_membership_event(user_id, requirement_id, event_type):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO membership_events (user_id, requirement_id, event_type, event_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, requirement_id, event_type, get_current_time()))

def get_recent_membership_events(limit=20):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT me.*, u.full_name as user_name, r.name as requirement_name
            FROM membership_events me
            LEFT JOIN users u ON me.user_id = u.user_id
            LEFT JOIN requirements r ON me.requirement_id = r.id
            ORDER BY me.event_date DESC
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

# ==================== SETTINGS FUNCTIONS ====================

def get_setting(key, default=None):
    """Get a setting value from database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT setting_value FROM bot_settings WHERE setting_key = ?', (key,))
        row = cursor.fetchone()
        if row:
            return row['setting_value']
        return default

def set_setting(key, value, description=None, updated_by=None):
    """Set a setting value in database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO bot_settings (setting_key, setting_value, description, updated_at, updated_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (key, value, description, get_current_time(), updated_by))

def get_all_settings():
    """Get all settings"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bot_settings ORDER BY setting_key')
        return cursor.fetchall()

# ==================== USER SETTINGS FUNCTIONS ====================

def get_user_setting(user_id, setting_key, default=True):
    """Get a user's setting value"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if setting_key == 'new_pdf_notifications':
            cursor.execute('SELECT new_pdf_notifications FROM user_settings WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                return row['new_pdf_notifications'] == 1
            return default
        
        return default

def set_user_setting(user_id, setting_key, value):
    """Set a user's setting value"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if setting_key == 'new_pdf_notifications':
            cursor.execute('''
                INSERT OR REPLACE INTO user_settings (user_id, new_pdf_notifications, updated_at)
                VALUES (?, ?, ?)
            ''', (user_id, 1 if value else 0, get_current_time()))
            return True
        
        return False

def get_all_users_with_notifications_enabled():
    """Get all users who have notifications enabled"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.user_id, u.full_name
            FROM users u
            JOIN user_settings us ON u.user_id = us.user_id
            WHERE u.is_banned = 0 AND us.new_pdf_notifications = 1
        ''')
        return cursor.fetchall()

# ==================== PENS FUNCTIONS ====================

def add_pen_to_user(user_id, pens=1):
    """Add pens to a user (when they get a referral)"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_pens WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            new_pens = existing['pens_available'] + pens
            new_earned = existing['total_earned'] + pens
            cursor.execute('''
                UPDATE user_pens 
                SET pens_available = ?, total_earned = ?, last_updated = ?
                WHERE user_id = ?
            ''', (new_pens, new_earned, get_current_time(), user_id))
        else:
            cursor.execute('''
                INSERT INTO user_pens (user_id, pens_available, total_earned, total_spent, last_updated)
                VALUES (?, ?, ?, 0, ?)
            ''', (user_id, pens, pens, get_current_time()))
        
        if DEBUG:
            print(f"💰 Added {pens} pen(s) to user {user_id}")
        return True

def get_user_pens(user_id):
    """Get available pens for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT pens_available FROM user_pens WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return row['pens_available'] if row else 0

def deduct_pen(user_id, pens=1):
    """Deduct pens when user browses a PDF"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT pens_available FROM user_pens WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if not row or row['pens_available'] < pens:
            return False
        
        new_pens = row['pens_available'] - pens
        cursor.execute('SELECT total_spent FROM user_pens WHERE user_id = ?', (user_id,))
        spent_row = cursor.fetchone()
        new_spent = (spent_row['total_spent'] if spent_row else 0) + pens
        
        cursor.execute('''
            UPDATE user_pens 
            SET pens_available = ?, total_spent = ?, last_updated = ?
            WHERE user_id = ?
        ''', (new_pens, new_spent, get_current_time(), user_id))
        
        if DEBUG:
            print(f"💰 Deducted {pens} pen(s) from user {user_id}, remaining: {new_pens}")
        return True

def get_pen_stats(user_id):
    """Get pen statistics for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT pens_available, total_earned, total_spent FROM user_pens WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                'available': row['pens_available'],
                'earned': row['total_earned'],
                'spent': row['total_spent']
            }
        return {'available': 0, 'earned': 0, 'spent': 0}

# ==================== BROWSING FUNCTIONS ====================

def create_browsing_session(user_id, viewed_pdfs=None):
    """Create a new browsing session"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Delete old session
        cursor.execute('DELETE FROM browsing_sessions WHERE user_id = ?', (user_id,))
        
        # Create new session with 1 hour expiry
        from datetime import timedelta
        expires_at = get_current_time() + timedelta(hours=1)
        
        cursor.execute('''
            INSERT INTO browsing_sessions (user_id, current_pdf_index, viewed_pdfs, created_at, expires_at)
            VALUES (?, 0, ?, ?, ?)
        ''', (user_id, json.dumps(viewed_pdfs or []), get_current_time(), expires_at))
        
        return True

def get_browsing_session(user_id):
    """Get current browsing session"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM browsing_sessions WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            # Check if expired
            from datetime import datetime
            expires_at = datetime.fromisoformat(row['expires_at']) if isinstance(row['expires_at'], str) else row['expires_at']
            if expires_at < get_current_time():
                cursor.execute('DELETE FROM browsing_sessions WHERE user_id = ?', (user_id,))
                return None
            
            return {
                'id': row['id'],
                'current_pdf_index': row['current_pdf_index'],
                'viewed_pdfs': json.loads(row['viewed_pdfs']) if row['viewed_pdfs'] else [],
                'created_at': row['created_at'],
                'expires_at': row['expires_at']
            }
        return None

def update_browsing_session(user_id, current_index, viewed_pdfs):
    """Update browsing session"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE browsing_sessions 
            SET current_pdf_index = ?, viewed_pdfs = ?
            WHERE user_id = ?
        ''', (current_index, json.dumps(viewed_pdfs), user_id))

def delete_browsing_session(user_id):
    """Delete browsing session"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM browsing_sessions WHERE user_id = ?', (user_id,))

def add_browsing_history(user_id, pdf_id, pen_spent=1):
    """Record a PDF view in browsing history"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO browsing_history (user_id, pdf_id, viewed_at, pen_spent)
            VALUES (?, ?, ?, ?)
        ''', (user_id, pdf_id, get_current_time(), pen_spent))

def get_browsing_history(user_id, limit=50):
    """Get browsing history for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT bh.*, p.file_name, p.subject, p.tag, p.class
            FROM browsing_history bh
            JOIN pdfs p ON bh.pdf_id = p.id
            WHERE bh.user_id = ?
            ORDER BY bh.viewed_at DESC
            LIMIT ?
        ''', (user_id, limit))
        return cursor.fetchall()

# ==================== SQL EXECUTION ====================

def execute_sql(sql):
    """Execute SQL query with safety checks"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            sql_upper = sql.strip().upper()
            allowed_commands = ['SELECT', 'UPDATE', 'INSERT', 'DELETE']
            if not any(sql_upper.startswith(cmd) for cmd in allowed_commands):
                return "⚠️ Only SELECT, UPDATE, INSERT, DELETE queries are allowed."
            
            cursor.execute(sql)
            if sql_upper.startswith('SELECT'):
                return cursor.fetchall()
            else:
                conn.commit()
                return f"Executed. Rows affected: {cursor.rowcount}"
        except Exception as e:
            return f"Error: {e}"