# config.py

# ========== BOT ==========
BOT_TOKEN = '7499697153:AAFC8Bh1JNWiTKD12cJ47TCyGW0--LRB-Ow'

# ========== ПОЧТА ==========
EMAILS = [
    {
        'email': 'zdorowenko.vladimir@yandex.ru',
        'password': 'cqgsrjfwazqdcxam',
        'imap_server': 'imap.yandex.ru',
        'folder': 'Chibbis',
        'source': 'chibis',
        'sender': 'noreply@chibbis.ru'
    },
    {
        'email': 'corp-zibofud80154@yandex.ru',
        'password': 'idsqjftojgxnrgub',
        'imap_server': 'imap.yandex.ru',
        'folder': 'INBOX',
        'source': 'yandex',
        'sender': 'noreply@eda.yandex.ru'
    }
]

# ========== ТОЧКИ И ГРУППЫ ==========
POINTS = {
    'Лермонтова':  ('Zibo Лермонтова', -1002293060505),
    'Центральная': ('Zibo Центральная', -1002212875554),
    'Строителей':  ('Zibo Строителей', -1001855052567),
}

# ========== НАСТРОЙКИ ==========
CHECK_INTERVAL = 60
REMINDER_AFTER = 3600
REMINDER_REPEAT = 5400
DATABASE_PATH = 'orders.db'