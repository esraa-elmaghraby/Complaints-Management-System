import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = 'complaints_management.db'

def get_db_connection():
    return sqlite3.connect(DB_NAME)

def initialize_db(conn):
    cursor = conn.cursor()

    # جدول الشكاوى
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'In Progress',
            created_at TEXT NOT NULL
        )
    """)

    # جدول التقييمات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            rating INTEGER,
            comments TEXT,
            FOREIGN KEY(complaint_id) REFERENCES complaints(id)
        )
    """)

    # جدول المديرين بدون first_login، هنضيفه بعدين لو ناقص
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    # نتأكد إن عمود first_login موجود، ولو مش موجود نضيفه
    update_admins_schema_if_needed(conn)

def update_admins_schema_if_needed(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(admins)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'first_login' not in columns:
        cursor.execute("ALTER TABLE admins ADD COLUMN first_login INTEGER DEFAULT 1")
        conn.commit()

def authenticate(username, password, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
    admin = cursor.fetchone()
    if admin and check_password_hash(admin[2], password):
        return True, bool(admin[3])  # admin[3] هو first_login
    return False, False

def create_default_admin(conn, username, password):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
    existing_admin = cursor.fetchone()
    
    if not existing_admin:
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO admins (username, password, first_login) VALUES (?, ?, 1)", (username, hashed_password))
        conn.commit()

def change_password(username, old_password, new_password, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
    admin = cursor.fetchone()
    
    if admin and check_password_hash(admin[2], old_password):
        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE admins SET password = ? WHERE username = ?", (hashed_password, username))
        conn.commit()
        return True
    return False

def load_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints")
    return cursor.fetchall()
