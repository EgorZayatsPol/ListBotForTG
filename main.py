#7115329705:AAE77wsVH7kd2bpx_i8spH2yjgQBmAn_8Bg

import telebot
from telebot import types
from config import TOKEN, MANAGERS
import csv
import os

bot = telebot.TeleBot(TOKEN)

# Временное хранилище для пользователей, которые проходят опрос
user_data = {}

# Путь к файлу, где хранятся заявки
DATA_FILE = 'data.csv'

# Проверка, существует ли файл. Если нет — создаём с заголовками
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Telegram ID', 'Username', 'Опыт работы', 'Источник', 'Цель заработка'])

# Стартовая команда
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Ответь, на несколько вопросов, чтобы подать заявку.")
    bot.send_message(message.chat.id, "Какой у вас опыт работы? ")
    user_data[message.chat.id] = {'step': 1}

# Обработка всех сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id

    # Если пользователь проходит опрос
    if chat_id in user_data:
        step = user_data[chat_id]['step']

        if step == 1:
            user_data[chat_id]['experience'] = message.text
            bot.send_message(chat_id, "Откуда ты узнал о нашей команде?")
            user_data[chat_id]['step'] = 2

        elif step == 2:
            user_data[chat_id]['source'] = message.text
            bot.send_message(chat_id, "Какова твоя цель для заработка?")
            user_data[chat_id]['step'] = 3

        elif step == 3:
            user_data[chat_id]['goal'] = message.text
            save_application(message)
            bot.send_message(chat_id, "Спасибо! Твоя заявка принята. Скоро с тобой свяжется менеджер.")
            del user_data[chat_id]

    # Команда менеджера на просмотр заявок
    elif message.text == '/application' and message.from_user.id in MANAGERS:
        send_applications_to_manager(message)

# Сохраняем данные в CSV и отправляем заявку менеджерам
def save_application(message):
    data = user_data[message.chat.id]

    # Сохраняем в файл
    with open(DATA_FILE, mode='a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            message.chat.id,
            message.from_user.username or 'нет username',
            data['experience'],
            data['source'],
            data['goal']
        ])

    # Формируем текст заявки
    response = (
        f"🧾 <b>Новая заявка</b>\n"
        f"👤 <b>ID:</b> {message.chat.id}\n"
        f"💬 <b>Username:</b> @{message.from_user.username or 'нет username'}\n"
        f"📌 <b>Опыт:</b> {data['experience']}\n"
        f"📥 <b>Источник:</b> {data['source']}\n"
        f"🎯 <b>Цель:</b> {data['goal']}"
    )

    # Отправляем заявку всем менеджерам
    for manager_id in MANAGERS:
        bot.send_message(manager_id, response, parse_mode='HTML')

# Менеджеру отправляем заявки
def send_applications_to_manager(message):
    with open(DATA_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # пропустить заголовки
        applications = list(reader)

    if not applications:
        bot.send_message(message.chat.id, "Заявок пока нет.")
        return

    for idx, app in enumerate(applications, start=1):
        response = (
            f"🧾 <b>Заявка #{idx}</b>\n"
            f"👤 <b>ID:</b> {app[0]}\n"
            f"💬 <b>Username:</b> @{app[1]}\n"
            f"📌 <b>Опыт:</b> {app[2]}\n"
            f"📥 <b>Источник:</b> {app[3]}\n"
            f"🎯 <b>Цель:</b> {app[4]}"
        )
        bot.send_message(message.chat.id, response, parse_mode='HTML')

print("Бот запущен.")
bot.polling(none_stop=True)
