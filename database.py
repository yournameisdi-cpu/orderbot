import sqlite3
from datetime import datetime, timedelta
from config import DATABASE_PATH

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            order_number TEXT,
            short_number TEXT,
            point_name TEXT,
            chat_id INTEGER,
            amount TEXT,
            client TEXT,
            email_uid TEXT UNIQUE,
            received_at DATETIME,
            deadline DATETIME,
            status TEXT DEFAULT 'waiting',
            photo_message_id INTEGER,
            photo_at DATETIME
        )
    ''')
    conn.commit()
    conn.close()

def add_order(source, order_number, short_number, point_name, chat_id, amount, client, email_uid):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    now = datetime.now()
    deadline = now + timedelta(seconds=3600)
    try:
        c.execute('''
            INSERT INTO orders (source, order_number, short_number, point_name, chat_id, amount, client, email_uid, received_at, deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (source, order_number, short_number, point_name, chat_id, amount, client, email_uid, now, deadline))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def get_waiting_orders(point_name=None):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    if point_name:
        c.execute('SELECT * FROM orders WHERE status="waiting" AND point_name=?', (point_name,))
    else:
        c.execute('SELECT * FROM orders WHERE status="waiting"')
    orders = c.fetchall()
    conn.close()
    return orders

def mark_photo_ok(order_id, message_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE orders SET status="photo_ok", photo_message_id=?, photo_at=? WHERE id=?
    ''', (message_id, datetime.now(), order_id))
    conn.commit()
    conn.close()

def get_expired_orders():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE status="waiting" AND deadline < ?', (datetime.now(),))
    orders = c.fetchall()
    conn.close()
    return orders

def get_order_by_short_number(short_number, chat_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT * FROM orders WHERE short_number=? AND chat_id=? AND status="waiting"
        ORDER BY received_at DESC LIMIT 1
    ''', (short_number, chat_id))
    order = c.fetchone()
    conn.close()
    return order