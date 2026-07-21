import asyncio
import re
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, CHECK_INTERVAL, POINTS
from database import init_db, get_order_by_short_number, mark_photo_ok, get_expired_orders
from mail_parser import check_all_emails

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat_id

    if chat_id not in [p[1] for p in POINTS.values()]:
        return

    if not message.photo:
        return

    caption = message.caption or ''
    match = re.search(r'\b(\d{4})\b', caption)
    if not match:
        return

    short_number = match.group(1)
    order = get_order_by_short_number(short_number, chat_id)

    if order:
        mark_photo_ok(order[0], message.message_id)
        await message.set_reaction('👍')
        print(f'Заказ {short_number} подтверждён в {order[3]}')

async def check_reminders(context: ContextTypes.DEFAULT_TYPE):
    expired = get_expired_orders()
    for order in expired:
        chat_id = order[5]
        short_number = order[3]
        point_name = order[4]
        source = order[1]

        await context.bot.send_message(
            chat_id=chat_id,
            text=f'⚠️ Заказ от {"Чибис" if source == "chibis" else "Яндекс.Еды"} '
                 f'№...{short_number} без фото уже более часа!\n'
                 f'Точка: {point_name}\n'
                 f'Отправьте фото заказа с номером {short_number}.'
        )

async def check_mail_loop():
    while True:
        new_orders = check_all_emails()
        if new_orders:
            for order in new_orders:
                print(f'Новый заказ: {order["source"]} №{order["short_number"]} → {order["point_name"]}')
        await asyncio.sleep(CHECK_INTERVAL)

def main():
    init_db()
    print('База данных готова')

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.GROUPS, handle_group_message))

    job_queue = app.job_queue
    job_queue.run_repeating(check_reminders, interval=300, first=10)

    loop = asyncio.get_event_loop()
    loop.create_task(check_mail_loop())

    print('Бот запущен')
    app.run_polling()

if __name__ == '__main__':
    main()