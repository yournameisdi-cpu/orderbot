import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import re
from config import EMAILS, POINTS
from database import add_order

def connect_mail(email_addr, password, imap_server):
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_addr, password)
    return mail

def get_unread_emails(mail, folder, sender_filter):
    mail.select(f'"{folder}"')
    status, messages = mail.search(None, f'(UNSEEN FROM "{sender_filter}")')
    if status != 'OK':
        return []
    return messages[0].split()

def parse_email(mail, email_id):
    status, msg_data = mail.fetch(email_id, '(RFC822)')
    if status != 'OK':
        return None

    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)

    subject = decode_header(msg['Subject'])[0][0]
    if isinstance(subject, bytes):
        subject = subject.decode()

    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()

    soup = BeautifulSoup(body, 'html.parser')
    text = soup.get_text()

    return {
        'subject': subject,
        'text': text,
        'uid': email_id.decode() if isinstance(email_id, bytes) else email_id
    }

def extract_order_info(parsed, source):
    text = parsed['text']
    subject = parsed['subject']
    uid = parsed['uid']

    order_number = None
    if source == 'chibis':
        match = re.search(r'Заказ №([\d\-]+)', subject)
        if match:
            order_number = match.group(1)
    elif source == 'yandex':
        match = re.search(r'Номер заказа:\s*([\d\-]+)', text)
        if match:
            order_number = match.group(1)

    if not order_number:
        return None

    short_number = order_number.replace('-', '')[-4:]

    point_name = None
    chat_id = None
    for keyword, (p_name, p_chat_id) in POINTS.items():
        if keyword.lower() in text.lower():
            point_name = p_name
            chat_id = p_chat_id
            break

    if not point_name:
        return None

    amount = None
    if source == 'chibis':
        match = re.search(r'ИТОГО:\s*([\d\s]+)\s*руб', text)
        if match:
            amount = match.group(1).strip()
    elif source == 'yandex':
        match = re.search(r'Сумма заказа:\s*([\d.]+)', text)
        if match:
            amount = match.group(1).strip()

    client = None
    if source == 'chibis':
        match = re.search(r'Имя:\s*(.+)', text)
        if match:
            client = match.group(1).strip()

    return {
        'source': source,
        'order_number': order_number,
        'short_number': short_number,
        'point_name': point_name,
        'chat_id': chat_id,
        'amount': amount,
        'client': client,
        'email_uid': uid
    }

def check_all_emails():
    results = []
    for acc in EMAILS:
        try:
            mail = connect_mail(acc['email'], acc['password'], acc['imap_server'])
            email_ids = get_unread_emails(mail, acc['folder'], acc['sender'])

            for eid in email_ids:
                parsed = parse_email(mail, eid)
                if parsed:
                    info = extract_order_info(parsed, acc['source'])
                    if info:
                        add_order(
                            info['source'],
                            info['order_number'],
                            info['short_number'],
                            info['point_name'],
                            info['chat_id'],
                            info['amount'],
                            info['client'],
                            info['email_uid']
                        )
                        results.append(info)

            mail.logout()
        except Exception as e:
            print(f'Ошибка проверки {acc["email"]}: {e}')
    return results