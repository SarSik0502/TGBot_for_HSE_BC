import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
import psycopg2
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime

""" 
Код подключеатся к БД в которой есть таблица newtable, которая состоит из 2 колонок - id и date:
    В id мы записываем id-пользователя(уникальные значения)
    В date мы записываем дату и время последнего вызова любой команды
Данный код проверял через своего бота на собственной БД рзвернутом на сервере. Вам, для проверки, следует подклчить свою БД, на своем боте
Кнопки: "О клубе", "Контакты" и "Ближайшие мероприятия" добавлены для проверки записи последних обновлений в БД при вызове разных команд
"""

BOT_TOKEN = "" #токен бота

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
storage = MemoryStorage()

# Функция для сохранения или обновления данных в БД
def save_or_update_db(user_id, timestamp):
    conn = psycopg2.connect(
        #Добавляете свои данные, для подключения к БД
        dbname='',
        user='',
        password='',
        host='',
        port=''
    )
    cursor = conn.cursor()
    upsert_query = """
       INSERT INTO newtable (id, date)
       VALUES (%s, %s)
       ON CONFLICT (id) 
       DO UPDATE SET date = EXCLUDED.date
    """
    cursor.execute(upsert_query, (user_id, timestamp))
    conn.commit()

    cursor.close()
    conn.close()

# Функция для подсчета записей в таблице
def count_records_in_table():
    conn = psycopg2.connect(
        # Добавляете свои данные, для подключения к БД
        dbname='',
        user='',
        password='',
        host='',
        port=''
    )
    cursor = conn.cursor()
    count_query = "SELECT COUNT(*) FROM newtable"
    cursor.execute(count_query)
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    timestamp = datetime.now()
    save_or_update_db(user_id, timestamp)
    list = [[KeyboardButton(text="О клубе"), KeyboardButton(text="Контакты"),
             KeyboardButton(text="Ближайшие мероприятия")]]
    keyboard = ReplyKeyboardMarkup(keyboard=list, resize_keyboard=True)
    await message.answer(
        f"Здравствуйте, {message.from_user.first_name}!\n"
        "Выберите одну из команд ниже:",
        reply_markup=keyboard
    )

# Обработчик команды /admin
@dp.message(Command("admin"))
async def admin_info(message: types.Message):
    count = count_records_in_table()
    await message.answer(f"Количество пользователей: {count}")

# Обработчик нажатия кнопки "О клубе"
@dp.message(F.text == "О клубе")
async def about_club(message: types.Message):
    user_id = message.from_user.id
    timestamp = datetime.now()
    save_or_update_db(user_id, timestamp)
    await message.answer("Информация о клубе: ...")

# Обработчик нажатия кнопки "Контакты"
@dp.message(F.text == "Контакты")
async def contacts(message: types.Message):
    user_id = message.from_user.id
    timestamp = datetime.now()
    save_or_update_db(user_id, timestamp)
    await message.answer("Контакты клуба: ...")

# Обработчик нажатия кнопки "Ближайшее мероприятие"
@dp.message(F.text == "Ближайшие мероприятия")
async def next_event(message: types.Message):
    user_id = message.from_user.id
    timestamp = datetime.now()
    save_or_update_db(user_id, timestamp)
    await message.answer("Ближайшее мероприятие: ...")


# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
