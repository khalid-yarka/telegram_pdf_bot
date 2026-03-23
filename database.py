# telegram_pdf_bot/database.py
# SQLite3 database operations with timezone support (Somalia)

import sqlite3
import json
import os
from contextlib import contextmanager
from config import DATABASE_PATH, DEBUG
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
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                phone TEXT,
                region TEXT,
                school TEXT,
                class TEXT,
                join_date TIMESTAMP,
                is_banned BOOLEAN DEFAULT 0,
                is_admin BOOLEAN DEFAULT 0,
                referred_by INTEGER,
                FOREIGN KEY (referred_by) REFERENCES users(user_id)
            )
        ''')
        
        # PDFs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pdfs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT,
                file_name TEXT,
                uploaded_by INTEGER,
                upload_date TIMESTAMP,
                subject TEXT,
                tag TEXT,
                exam_year INTEGER,
                download_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                is_approved BOOLEAN DEFAULT 0,
                source TEXT,
                FOREIGN KEY (uploaded_by) REFERENCES users(user_id)
            )
        ''')
        
        # User likes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_likes (
                user_id INTEGER,
                pdf_id INTEGER,
                PRIMARY KEY (user_id, pdf_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (pdf_id) REFERENCES pdfs(id)
            )
        ''')
        
        # Downloads log
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
        
        # User state table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_state (
                user_id INTEGER PRIMARY KEY,
                state TEXT,
                data TEXT,
                updated_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Reports table
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
        
        if DEBUG:
            print("✅ Database tables created/verified successfully")

# --- User functions ---
def add_user(user_id, full_name, phone=None, region=None, school=None, class_name=None, referred_by=None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users 
            (user_id, full_name, phone, region, school, class, join_date, is_banned, is_admin, referred_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?)
        ''', (user_id, full_name, phone, region, school, class_name, get_current_time(), referred_by))
        if phone or region or school or class_name:
            cursor.execute('''
                UPDATE users SET
                    phone = COALESCE(?, phone),
                    region = COALESCE(?, region),
                    school = COALESCE(?, school),
                    class = COALESCE(?, class)
                WHERE user_id = ?
            ''', (phone, region, school, class_name, user_id))
        
        if DEBUG:
            print(f"📝 User added/updated: {user_id} - {full_name}")

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
            cursor.execute('SELECT * FROM users LIMIT ? OFFSET ?', (limit, offset))
        else:
            cursor.execute('SELECT * FROM users')
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

# --- PDF functions ---
def add_pdf(file_id, file_name, user_id, subject, tag, exam_year=None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pdfs 
            (file_id, file_name, uploaded_by, upload_date, subject, tag, exam_year, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (file_id, file_name, user_id, get_current_time(), subject, tag, exam_year, 'upload'))
        pdf_id = cursor.lastrowid
        if DEBUG:
            print(f"📄 PDF added: ID={pdf_id}, Name={file_name}, User={user_id}")
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

def get_pdfs_by_filters(subject=None, tag=None, exam_year=None, uploaded_by=None, approved_only=True, limit=10, offset=0):
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

def count_pdfs_by_filters(subject=None, tag=None, exam_year=None, uploaded_by=None, approved_only=True):
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

# --- State functions ---
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

# --- Report functions ---
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

# --- Statistics ---
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

# --- SQL execution for admin ---
def execute_sql(sql):
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            if sql.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                conn.commit()
                return f"Executed. Rows affected: {cursor.rowcount}"
        except Exception as e:
            return f"Error: {e}"