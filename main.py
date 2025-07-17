import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters.command import Command
from aiogram.filters import command
from aiogram.filters.command import CommandObject
from aiogram import F
from aiogram.types import FSInputFile 
import requests
import aiosqlite
import re
import random
import time
import aiohttp
import logging
import sqlite3



TOKEN = "7812877820:AAHwGo92qc6Ji2YaloQB80AX9cvnwuMA7A8"

BOT_LINK = 'https://t.me/wallistarsbot'
API_KEY = "0003448041858122acc42b042ab2a14c7a0a880f488435620adcc6db96f6cf13"


bot = Bot(TOKEN)
dp = Dispatcher()

user_id = 0
chat_id = ''
referrer_id = 0


async def init_db():
    global user_id
    
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Создаем таблицу, если она еще не существует
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                stars INTEGER DEFAULT 0,
                referrals INTEGER DEFAULT 0,
                tasks_completed INTEGER DEFAULT 0,
                referrer INTEGER,
                last_reward_time INTEGER DEFAULT 0
            )
        """)
        
        await db.commit()

        # Проверяем, есть ли столбец referrer
        await cursor.execute("PRAGMA table_info(users)")
        columns = await cursor.fetchall()
        column_names = [column[1] for column in columns]

        # Если столбца referrer нет, добавляем его
        if 'referrer' not in column_names:
            await cursor.execute("ALTER TABLE users ADD COLUMN referrer INTEGER")
            await db.commit()


@dp.message(CommandStart())
async def start(message: types.Message):
    global chat_id
    global user_id
    global referrer_id
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    args = message.text.split()
    if len(args) == 1:
        referrer_id = None
    else:
        referrer_id = args[1]  # Получаем ID реферера


    
    await request_op(user_id, chat_id)
    
async def start_two(message: types.Message):

    #btn1 = InlineKeyboardButton(text='✨ Кликер', callback_data='clicker')
    btn2 = InlineKeyboardButton(text='⭐ Заработать звёзды', callback_data='work_stars')
    btn3 = InlineKeyboardButton(text='👤 Профиль', callback_data='profile')
    btn4 = InlineKeyboardButton(text='💰 Вывод звёзд', callback_data='send_stars')
    btn5 = InlineKeyboardButton(text='🎰 Рулетка', callback_data='ruletka')
    btn6 = InlineKeyboardButton(text='📚 Инструкция', callback_data='instrykciya')
    btn7 = InlineKeyboardButton(text='📝 Задания', callback_data='quest')
            
    #row_one = [btn1]
    row_two = [btn2]
    row_fre = [btn3, btn4]
    row_fho = [btn5, btn6]
    row_five = [btn7]
    rows = [row_two, row_fre, row_fho, row_five]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
    photo = FSInputFile("Video/Glavnaya.mp4")
    await bot.send_animation(chat_id, photo, caption='1️⃣ Получи свою личную ссылку — жми «⭐️ Заработать звезды»\n2️⃣ Приглашай друзей — 3⭐️ за каждого!\n\n✅ Дополнительно:\n<blockquote>— Ежедневные награды и промокоды (Профиль)\n— Выполняй задания\n— Крути рулетку и удвой баланс!\n— Участвуй в конкурсе на топ</blockquote>\n\n🔻 Главное меню', reply_markup=markup, parse_mode='html')
            
 
@dp.callback_query(F.data == 'clicker')
async def calldata(call: CallbackQuery):
    pass
    
    
@dp.callback_query(F.data == 'profile')
async def calldata(call: CallbackQuery):
    await call.message.delete()
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()

    if user_data:
        
        btn1 = InlineKeyboardButton(text='💳 Промокод', callback_data='promo')
        btn2 = InlineKeyboardButton(text='💫 Звёзды другу', callback_data='stars_friend')
        btn3 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
        
        row_one = [btn1, btn2]
        row_two = [btn3]
        rows = [row_one, row_two]
        markup = InlineKeyboardMarkup(inline_keyboard=rows)
        
        stars, referrals, tasks_completed = user_data
        # Отправляем сообщение с актуальной информацией
        photo = FSInputFile("Video/Profile.mp4")
        await bot.send_animation(call.from_user.id, photo, caption=f"✨ <b>Профиль\n──────────────\n👤 Имя: {call.from_user.username}\n🆔 ID: {call.from_user.id}\n──────────────</b>\n👥 Всего друзей: {referrals}\n💰 Баланс: {stars} ⭐️\n\n<i>⬇️  Используй кнопки ниже, чтобы ввести промокод, или отправить звезды на баланс друга</i>", parse_mode='html', reply_markup=markup)

    else:
        await bot.send_message(call.from_user.id, "❌ Пользователь не найден.")
    

@dp.callback_query(F.data == 'promo')
async def calldata(call: CallbackQuery):
    
    await bot.send_message(call.from_user.id, 'База активных промокодов ещё не создана!\nСледите за нашими новостями что бы узнать о новинках первым.')  

@dp.callback_query(F.data == 'stars_friend')
async def calldata(call: CallbackQuery):
    
    await bot.send_message(call.from_user.id, '❌ У вас не хватает звёзд что бы отправить их другу!\n- Минимальное количество 50🌟')  

@dp.callback_query(F.data == 'send_stars')
async def calldata(call: CallbackQuery):
    await call.message.delete()
    
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
    
    stars, referrals, tasks_completed = user_data
    
    btn1 = InlineKeyboardButton(text='15 ⭐ (🧸)', callback_data='send_bear')
    btn2 = InlineKeyboardButton(text='15 ⭐ (💝)', callback_data='send_heart')
    btn3 = InlineKeyboardButton(text='25 ⭐ (🌹)', callback_data='send_rose')
    btn4 = InlineKeyboardButton(text='25 ⭐ (🎁)', callback_data='send_gift')
    btn5 = InlineKeyboardButton(text='50 ⭐ (🍾)', callback_data='send_champagne')
    btn6 = InlineKeyboardButton(text='50 ⭐ (💐)', callback_data='send_flowers')
    btn7 = InlineKeyboardButton(text='50 ⭐ (🚀)', callback_data='send_rocket')
    btn8 = InlineKeyboardButton(text='50 ⭐ (🎂)', callback_data='send_cake')
    btn9 = InlineKeyboardButton(text='100 ⭐ (🏆)', callback_data='send_cup')
    btn10 = InlineKeyboardButton(text='100 ⭐ (💍)', callback_data='send_ring')
    btn11 = InlineKeyboardButton(text='100 ⭐ (💎)', callback_data='send_diamond')
    btn12 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
    
    
    row_one = [btn1, btn2]
    row_two = [btn3, btn4]
    row_fre = [btn5, btn6]
    row_fho = [btn7, btn8]
    row_five = [btn9, btn10]
    row_six = [btn11]
    row_seven = [btn12]
    rows = [row_one, row_two, row_fre, row_fho, row_five, row_six, row_seven]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)

    photo = FSInputFile("Photo/Vivod.png")
    await bot.send_photo(call.from_user.id, photo, caption=f'💰<b>Баланс:</b> {stars} ⭐️\n\n<b>‼️Для вывода требуется:</b>\n— минимум 5 приглашенных друзей, активировавших бота\n— Быть подписанным на наш канал\n\n<blockquote>✅ Моментальный автоматический вывод!</blockquote>\n\n<b>Выбери количество звезд и подарок, которым ты хочешь их получить:</b>', parse_mode='html', reply_markup=markup)  
    

@dp.callback_query(F.data == 'send_bear')
async def calldata(call: CallbackQuery):
    
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 15:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE users SET stars = stars - 15 WHERE user_id = ?", (user_id,))
            await db.commit()
            
            user_name = call.from_user.username
            
            btn1 = InlineKeyboardButton(text='Перейти', url=f'https://t.me/{user_name}')
            row_one = [btn1]
            rows = [row_one]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            await bot.send_message(chat_id=5890667637, text=f'❗<b> НОВЫЙ ВЫВОД </b>❗\n\n<b>------------------------------</b>\n👤 <b>Пользователь:</b> {user_name}\n🆔 <b>Пользователя:</b> {user_id}\n💸 <b>Вывод</b> 15⭐️ (🧸)\n<b>-------------------------- ----</b>', parse_mode='html', reply_markup=markup)
            await bot.send_message(call.from_user.id, '✓ Подарок успешно отправлен, ожидайте получение!')
    else:
        await bot.send_message(call.from_user.id, '❌ У вас не хватает звёзд!')

@dp.callback_query(F.data == 'send_heart')
async def calldata(call: CallbackQuery):
    
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 15:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE users SET stars = stars - 15 WHERE user_id = ?", (user_id,))
            await db.commit()
            
            user_name = call.from_user.username
            
            btn1 = InlineKeyboardButton(text='Перейти', url=f'https://t.me/{user_name}')
            row_one = [btn1]
            rows = [row_one]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            await bot.send_message(chat_id=5890667637, text=f'❗<b> НОВЫЙ ВЫВОД </b>❗\n\n<b>------------------------------</b>\n👤 <b>Пользователь:</b> {user_name}\n🆔 <b>Пользователя:</b> {user_id}\n💸 <b>Вывод</b> 15⭐️ (💝)\n<b>-------------------------- ----</b>', parse_mode='html', reply_markup=markup)
            await bot.send_message(call.from_user.id, '✓ Подарок успешно отправлен, ожидайте получение!')
    else:
        await bot.send_message(call.from_user.id, '❌ У вас не хватает звёзд!')

@dp.callback_query(F.data == 'send_rose')
async def calldata(call: CallbackQuery):
    
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 25:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE users SET stars = stars - 25 WHERE user_id = ?", (user_id,))
            await db.commit()
            
            user_name = call.from_user.username
            
            btn1 = InlineKeyboardButton(text='Перейти', url=f'https://t.me/{user_name}')
            row_one = [btn1]
            rows = [row_one]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            await bot.send_message(chat_id=5890667637, text=f'❗<b> НОВЫЙ ВЫВОД </b>❗\n\n<b>------------------------------</b>\n👤 <b>Пользователь:</b> {user_name}\n🆔 <b>Пользователя:</b> {user_id}\n💸 <b>Вывод</b> 25⭐️ (🌹)\n<b>-------------------------- ----</b>', parse_mode='html', reply_markup=markup)
            await bot.send_message(call.from_user.id, '✓ Подарок успешно отправлен, ожидайте получение!')
    else:
        await bot.send_message(call.from_user.id, '❌ У вас не хватает звёзд!')
        
@dp.callback_query(F.data == 'send_gift')
async def calldata(call: CallbackQuery):
    
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 25:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE users SET stars = stars - 25 WHERE user_id = ?", (user_id,))
            await db.commit()
            
            user_name = call.from_user.username
            
            btn1 = InlineKeyboardButton(text='Перейти', url=f'https://t.me/{user_name}')
            row_one = [btn1]
            rows = [row_one]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            await bot.send_message(chat_id=5890667637, text=f'❗<b> НОВЫЙ ВЫВОД </b>❗\n\n<b>------------------------------</b>\n👤 <b>Пользователь:</b> {user_name}\n🆔 <b>Пользователя:</b> {user_id}\n💸 <b>Вывод</b> 25⭐️ (🎁)\n<b>-------------------------- ----</b>', parse_mode='html', reply_markup=markup)
            await bot.send_message(call.from_user.id, '✓ Подарок успешно отправлен, ожидайте получение!')
    else:
        await bot.send_message(call.from_user.id, '❌ У вас не хватает звёзд!')

@dp.callback_query(F.data == 'send_champagne')
async def calldata(call: CallbackQuery):
    
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 50:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE users SET stars = stars - 50 WHERE user_id = ?", (user_id,))
            await db.commit()
            
            user_name = call.from_user.username
            
            btn1 = InlineKeyboardButton(text='Перейти', url=f'https://t.me/{user_name}')
            row_one = [btn1]
            rows = [row_one]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            await bot.send_message(chat_id=5890667637, text=f'❗<b> НОВЫЙ ВЫВОД </b>❗\n\n<b>------------------------------</b>\n👤 <b>Пользователь:</b> {user_name}\n🆔 <b>Пользователя:</b> {user_id}\n💸 <b>Вывод</b> 50⭐️ (🍾)\n<b>-------------------------- ----</b>', parse_mode='html', reply_markup=markup)
            await bot.send_message(call.from_user.id, '✓ Подарок успешно отправлен, ожидайте получение!')
    else:
        await bot.send_message(call.from_user.id, '❌ У вас не хватает звёзд!')


@dp.callback_query(F.data == 'send_flowers')
async def calldata(call: CallbackQuery):
    
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 50:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE users SET stars = stars - 50 WHERE user_id = ?", (user_id,))
            await db.commit()
            
            user_name = call.from_user.username
            
            btn1 = InlineKeyboardButton(text='Перейти', url=f'https://t.me/{user_name}')
            row_one = [btn1]
            rows = [row_one]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            await bot.send_message(chat_id=5890667637, text=f'❗<b> НОВЫЙ ВЫВОД </b>❗\n\n<b>------------------------------</b>\n👤 <b>Пользователь:</b> {user_name}\n🆔 <b>Пользователя:</b> {user_id}\n💸 <b>Вывод</b> 50⭐️ (💐)\n<b>-------------------------- ----</b>', parse_mode='html', reply_markup=markup)
            await bot.send_message(call.from_user.id, '✓ Подарок успешно отправлен, ожидайте получение!')
    else:
        await bot.send_message(call.from_user.id, '❌ У вас не хватает звёзд!')
        

@dp.callback_query(F.data == 'send_rocket')
async def calldata(call: CallbackQuery):
    
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 50:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE users SET stars = stars - 50 WHERE user_id = ?", (user_id,))
            await db.commit()
            
            user_name = call.from_user.username
            
            btn1 = InlineKeyboardButton(text='Перейти', url=f'https://t.me/{user_name}')
            row_one = [btn1]
            rows = [row_one]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            await bot.send_message(chat_id=5890667637, text=f'❗<b> НОВЫЙ ВЫВОД </b>❗\n\n<b>------------------------------</b>\n👤 <b>Пользователь:</b> {user_name}\n🆔 <b>Пользователя:</b> {user_id}\n💸 <b>Вывод</b> 50⭐️ (🚀)\n<b>-------------------------- ----</b>', parse_mode='html', reply_markup=markup)
            await bot.send_message(call.from_user.id, '✓ Подарок успешно отправлен, ожидайте получение!')
    else:
        await bot.send_message(call.from_user.id, '❌ У вас не хватает звёзд!')
        
@dp.callback_query(F.data == 'send_cake')
async def calldata(call: CallbackQuery):
    
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 50:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE users SET stars = stars - 50 WHERE user_id = ?", (user_id,))
            await db.commit()
            
            user_name = call.from_user.username
            
            btn1 = InlineKeyboardButton(text='Перейти', url=f'https://t.me/{user_name}')
            row_one = [btn1]
            rows = [row_one]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            await bot.send_message(chat_id=5890667637, text=f'❗<b> НОВЫЙ ВЫВОД </b>❗\n\n<b>------------------------------</b>\n👤 <b>Пользователь:</b> {user_name}\n🆔 <b>Пользователя:</b> {user_id}\n💸 <b>Вывод</b> 50⭐️ (🎂)\n<b>-------------------------- ----</b>', parse_mode='html', reply_markup=markup)
            await bot.send_message(call.from_user.id, '✓ Подарок успешно отправлен, ожидайте получение!')
    else:
        await bot.send_message(call.from_user.id, '❌ У вас не хватает звёзд!')
        
@dp.callback_query(F.data == 'send_cup')
async def calldata(call: CallbackQuery):
    
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 100:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE users SET stars = stars - 100 WHERE user_id = ?", (user_id,))
            await db.commit()
            
            user_name = call.from_user.username
            
            btn1 = InlineKeyboardButton(text='Перейти', url=f'https://t.me/{user_name}')
            row_one = [btn1]
            rows = [row_one]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            await bot.send_message(chat_id=5890667637, text=f'❗<b> НОВЫЙ ВЫВОД </b>❗\n\n<b>------------------------------</b>\n👤 <b>Пользователь:</b> {user_name}\n🆔 <b>Пользователя:</b> {user_id}\n💸 <b>Вывод</b> 100⭐️ (🏆)\n<b>-------------------------- ----</b>', parse_mode='html', reply_markup=markup)
            await bot.send_message(call.from_user.id, '✓ Подарок успешно отправлен, ожидайте получение!')
    else:
        await bot.send_message(call.from_user.id, '❌ У вас не хватает звёзд!')
        
@dp.callback_query(F.data == 'send_ring')
async def calldata(call: CallbackQuery):
    
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 100:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE users SET stars = stars - 100 WHERE user_id = ?", (user_id,))
            await db.commit()
            
            user_name = call.from_user.username
            
            btn1 = InlineKeyboardButton(text='Перейти', url=f'https://t.me/{user_name}')
            row_one = [btn1]
            rows = [row_one]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            await bot.send_message(chat_id=5890667637, text=f'❗<b> НОВЫЙ ВЫВОД </b>❗\n\n<b>------------------------------</b>\n👤 <b>Пользователь:</b> {user_name}\n🆔 <b>Пользователя:</b> {user_id}\n💸 <b>Вывод</b> 100⭐️ (💍)\n<b>-------------------------- ----</b>', parse_mode='html', reply_markup=markup)
            await bot.send_message(call.from_user.id, '✓ Подарок успешно отправлен, ожидайте получение!')
    else:
        await bot.send_message(call.from_user.id, '❌ У вас не хватает звёзд!')
        
@dp.callback_query(F.data == 'send_diamond')
async def calldata(call: CallbackQuery):
    
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 100:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE users SET stars = stars - 100 WHERE user_id = ?", (user_id,))
            await db.commit()
            
            user_name = call.from_user.username
            
            btn1 = InlineKeyboardButton(text='Перейти', url=f'https://t.me/{user_name}')
            row_one = [btn1]
            rows = [row_one]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            await bot.send_message(chat_id=5890667637, text=f'❗<b> НОВЫЙ ВЫВОД </b>❗\n\n<b>------------------------------</b>\n👤 <b>Пользователь:</b> {user_name}\n🆔 <b>Пользователя:</b> {user_id}\n💸 <b>Вывод</b> 100⭐️ (💎)\n<b>-------------------------- ----</b>', parse_mode='html', reply_markup=markup)
            await bot.send_message(call.from_user.id, '✓ Подарок успешно отправлен, ожидайте получение!')
    else:
        await bot.send_message(call.from_user.id, '❌ У вас не хватает звёзд!')


@dp.callback_query(F.data == 'instrykciya')
async def calldata(call: CallbackQuery):
    await call.message.delete()
    
    btn1 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
    row_one = [btn1]
    rows = [row_one]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    
    photo = FSInputFile("Photo/Instrykcia.png")
    await bot.send_photo(call.from_user.id, photo, caption='<b>📌 Как набрать много переходов по ссылке?</b>\n<blockquote>• Отправь её друзьям в личные сообщения 🧍‍♂️🧍‍♀️\n• Поделись ссылкой в истории и в своем ТГ или в Telegram-канале 📣\n• Оставь её в комментариях или чатах 🗨️\n• Распространяй ссылку в соцсетях: TikTok, Instagram, WhatsApp и других 🌍</blockquote>\n\n<b>🤩 Способы, которыми можно заработать до 1000 звёзд в день:</b>\n\n<b>1️⃣ Первый способ:</b>\n<blockquote>1. Заходим в TikTok или Лайк\n2. Ищем видео по запросам: звёзды телеграм, подарки телеграм, тг старсы и т.п.\n3. Оставляем в комментариях текст типа: Дарю подарки/звезды, пишите в тг @вашюзер\n4. Отправляете свою личную ссылку тем, кто пишет\n5. Ждём и выводим звезды 💰</blockquote>\n\n<b>2️⃣ Второй способ:</b>\n<blockquote>1. Заходим в бот знакомств @leomatchbot\n2. Делаем анкету женского пола\n3. Лайкаем всех подряд и параллельно ждём пока нас пролайкают 💞\n4. Переходим со всеми в ЛС и пишем: Привет, помоги мне пожалуйста заработать звёзды. Перейди и активируй бота по моей ссылке: «твоя ссылка»\n5. Ждём и выводим звёзды 🌟</blockquote>', parse_mode='html', reply_markup=markup)


@dp.callback_query(F.data == 'ruletka')
async def calldata(call: CallbackQuery):
    await call.message.delete()
    
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
    
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    stars, referrals, tasks_completed = user_data
    
    
    btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
    btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
    btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
    btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
    btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
    btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
    btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
    btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
    btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
    btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
    
    row_one = [btn1, btn2, btn3]
    row_two = [btn4, btn5, btn6]
    row_fre = [btn7, btn8, btn9]
    row_fho = [btn10]
    rows = [row_one, row_two, row_fre, row_fho]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    
    
    photo = FSInputFile("Photo/Ruletka.png")
    await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)


@dp.callback_query(F.data == '0.5⭐')
async def calldata(call: CallbackQuery):
    
    res = random.randint(0,1)
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
        
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 0.5:
        if res == 0:
            await bot.answer_callback_query(call.id, text='Вы проиграли 0.5⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars - 0.5 WHERE user_id = ?", (user_id,))
                await db.commit()
            
            await call.message.delete()

            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
                
            
        else:
            await bot.answer_callback_query(call.id, text='Вы выиграли 1⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars + 1 WHERE user_id = ?", (user_id,))
                await db.commit()
                
            await call.message.delete()
                
            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
    else:
        await bot.send_message(call.from_user.id, '❌ У вас недостаточно звёзд')
    

@dp.callback_query(F.data == '1⭐')
async def calldata(call: CallbackQuery):
    
    res = random.randint(0,1)
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
        
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 1:
        if res == 0:
            await bot.answer_callback_query(call.id, text='Вы проиграли 1⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars - 1 WHERE user_id = ?", (user_id,))
                await db.commit()
            
            await call.message.delete()

            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
                
            
        else:
            await bot.answer_callback_query(call.id, text='Вы выиграли 2⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars + 2 WHERE user_id = ?", (user_id,))
                await db.commit()
                
            await call.message.delete()
                
            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
    else:
        await bot.send_message(call.from_user.id, '❌ У вас недостаточно звёзд')


@dp.callback_query(F.data == '2⭐')
async def calldata(call: CallbackQuery):
    
    res = random.randint(0,1)
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
        
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 2:
        if res == 0:
            await bot.answer_callback_query(call.id, text='Вы проиграли 2⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars - 2 WHERE user_id = ?", (user_id,))
                await db.commit()
            
            await call.message.delete()

            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
                
            
        else:
            await bot.answer_callback_query(call.id, text='Вы выиграли 4⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars + 4 WHERE user_id = ?", (user_id,))
                await db.commit()
                
            await call.message.delete()
                
            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
    else:
        await bot.send_message(call.from_user.id, '❌ У вас недостаточно звёзд')


@dp.callback_query(F.data == '3⭐')
async def calldata(call: CallbackQuery):
    
    res = random.randint(0,1)
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
        
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 3:
        if res == 0:
            await bot.answer_callback_query(call.id, text='Вы проиграли 3⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars - 3 WHERE user_id = ?", (user_id,))
                await db.commit()
            
            await call.message.delete()

            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
                
            
        else:
            await bot.answer_callback_query(call.id, text='Вы выиграли 6⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars + 6 WHERE user_id = ?", (user_id,))
                await db.commit()
                
            await call.message.delete()
                
            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
    else:
        await bot.send_message(call.from_user.id, '❌ У вас недостаточно звёзд')



@dp.callback_query(F.data == '5⭐')
async def calldata(call: CallbackQuery):
    
    res = random.randint(0,1)
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
        
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 5:
        if res == 0:
            await bot.answer_callback_query(call.id, text='Вы проиграли 5⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars - 5 WHERE user_id = ?", (user_id,))
                await db.commit()
            
            await call.message.delete()

            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
                
            
        else:
            await bot.answer_callback_query(call.id, text='Вы выиграли 10⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars + 10 WHERE user_id = ?", (user_id,))
                await db.commit()
                
            await call.message.delete()
                
            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
    else:
        await bot.send_message(call.from_user.id, '❌ У вас недостаточно звёзд')

@dp.callback_query(F.data == '10⭐')
async def calldata(call: CallbackQuery):
    
    res = random.randint(0,1)
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
        
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 10:
        if res == 0:
            await bot.answer_callback_query(call.id, text='Вы проиграли 10⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars - 10 WHERE user_id = ?", (user_id,))
                await db.commit()
            
            await call.message.delete()

            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
                
            
        else:
            await bot.answer_callback_query(call.id, text='Вы выиграли 20⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars + 20 WHERE user_id = ?", (user_id,))
                await db.commit()
                
            await call.message.delete()
                
            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
    else:
        await bot.send_message(call.from_user.id, '❌ У вас недостаточно звёзд')


@dp.callback_query(F.data == '50⭐')
async def calldata(call: CallbackQuery):
    
    res = random.randint(0,1)
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
        
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 50:
        if res == 0:
            await bot.answer_callback_query(call.id, text='Вы проиграли 50⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars - 50 WHERE user_id = ?", (user_id,))
                await db.commit()
            
            await call.message.delete()

            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
                
            
        else:
            await bot.answer_callback_query(call.id, text='Вы выиграли 100⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars + 100 WHERE user_id = ?", (user_id,))
                await db.commit()
                
            await call.message.delete()
                
            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
    else:
        await bot.send_message(call.from_user.id, '❌ У вас недостаточно звёзд')


@dp.callback_query(F.data == '100⭐')
async def calldata(call: CallbackQuery):
    
    res = random.randint(0,1)
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
        
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 100:
        if res == 0:
            await bot.answer_callback_query(call.id, text='Вы проиграли 100⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars - 100 WHERE user_id = ?", (user_id,))
                await db.commit()
            
            await call.message.delete()

            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
                
            
        else:
            await bot.answer_callback_query(call.id, text='Вы выиграли 200⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars + 200 WHERE user_id = ?", (user_id,))
                await db.commit()
                
            await call.message.delete()
                
            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
    else:
        await bot.send_message(call.from_user.id, '❌ У вас недостаточно звёзд')

@dp.callback_query(F.data == '500⭐')
async def calldata(call: CallbackQuery):
    
    res = random.randint(0,1)
    user_id = call.from_user.id
    db = await aiosqlite.connect('users.db')
        
    async with db.cursor() as cursor:
        # Получаем информацию о пользователе из базы данных
        await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        
    stars, referrals, tasks_completed = user_data
    
    if int(stars) >= 500:
        if res == 0:
            await bot.answer_callback_query(call.id, text='Вы проиграли 500⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars - 500 WHERE user_id = ?", (user_id,))
                await db.commit()
            
            await call.message.delete()

            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
                
            
        else:
            await bot.answer_callback_query(call.id, text='Вы выиграли 1000⭐')
            
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE users SET stars = stars + 1000 WHERE user_id = ?", (user_id,))
                await db.commit()
                
            await call.message.delete()
                
            user_id = call.from_user.id
            db = await aiosqlite.connect('users.db')
            
            async with db.cursor() as cursor:
                # Получаем информацию о пользователе из базы данных
                await cursor.execute("SELECT stars, referrals, tasks_completed FROM users WHERE user_id = ?", (user_id,))
                user_data = await cursor.fetchone()
                
            stars, referrals, tasks_completed = user_data
            
            
            btn1 = InlineKeyboardButton(text='0.5⭐', callback_data='0.5⭐')
            btn2 = InlineKeyboardButton(text='1⭐', callback_data='1⭐')
            btn3 = InlineKeyboardButton(text='2⭐', callback_data='2⭐')
            btn4 = InlineKeyboardButton(text='3⭐', callback_data='3⭐')
            btn5 = InlineKeyboardButton(text='5⭐', callback_data='5⭐')
            btn6 = InlineKeyboardButton(text='10⭐', callback_data='10⭐')
            btn7 = InlineKeyboardButton(text='50⭐', callback_data='50⭐')
            btn8 = InlineKeyboardButton(text='100⭐', callback_data='100⭐')
            btn9 = InlineKeyboardButton(text='500⭐', callback_data='500⭐')
            btn10 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
            
            row_one = [btn1, btn2, btn3]
            row_two = [btn4, btn5, btn6]
            row_fre = [btn7, btn8, btn9]
            row_fho = [btn10]
            rows = [row_one, row_two, row_fre, row_fho]
            markup = InlineKeyboardMarkup(inline_keyboard=rows)
            
            
            photo = FSInputFile("Photo/Ruletka.png")
            await bot.send_photo(call.from_user.id, photo,  caption=f'<u>🎰 Крути рулетку и удвой свой баланс !</u>\n\n💰<b> Баланс: {stars} ⭐️\n⬇️ Выбери ставку:</b>', parse_mode='html', reply_markup=markup)
    else:
        await bot.send_message(call.from_user.id, '❌ У вас недостаточно звёзд')


@dp.callback_query(F.data == 'quest')
async def calldata(call: CallbackQuery):
    
    await bot.send_message(call.from_user.id, 'Сейчас нету активных заданий, попробуй позже!')
    
    
@dp.callback_query(F.data == 'work_stars')
async def calldata(call: CallbackQuery):
    await call.message.delete()
    user_id = call.from_user.id
    referral_link = f"{BOT_LINK}?start={user_id}"  # Генерация реферальной ссылки
    
    btn1 = InlineKeyboardButton(text='⬅️ В главное меню', callback_data='exit')
    row_one = [btn1]
    rows = [row_one]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    
    photo = FSInputFile("Photo/Zarabotat.png")
    await bot.send_photo(call.from_user.id, photo, caption=f"*🎉Приглашай друзей и получай по 3 ⭐️ от Патрика за каждого, кто активирует бота по твоей ссылке!*\n\n🔗 _Твоя личная ссылка (нажми чтобы скопировать):_\n\n`{referral_link}`\n\n*🚀 Как набрать много переходов по ссылке?*\n_• Отправь её друзьям в личные сообщения 👥\n• Поделись ссылкой в истории в своем ТГ или в своем Telegram канале 📱\n• Оставь её в комментариях или чатах 🗨\n• Распространяй ссылку в соцсетях: TikTok, Instagram, WhatsApp и других 🌍_", parse_mode='MARKDOWN', reply_markup=markup)
    
    

@dp.callback_query(F.data == 'exit')
async def calldata(call: CallbackQuery):
    await call.message.delete()
    
    #btn1 = InlineKeyboardButton(text='✨ Кликер', callback_data='clicker')
    btn2 = InlineKeyboardButton(text='⭐ Заработать звёзды', callback_data='work_stars')
    btn3 = InlineKeyboardButton(text='👤 Профиль', callback_data='profile')
    btn4 = InlineKeyboardButton(text='💰 Вывод звёзд', callback_data='send_stars')
    btn5 = InlineKeyboardButton(text='🎰 Рулетка', callback_data='ruletka')
    btn6 = InlineKeyboardButton(text='📚 Инструкция', callback_data='instrykciya')
    btn7 = InlineKeyboardButton(text='📝 Задания', callback_data='quest')
    
    #row_one = [btn1]
    row_two = [btn2]
    row_fre = [btn3, btn4]
    row_fho = [btn5, btn6]
    row_five = [btn7]
    rows = [row_two, row_fre, row_fho, row_five]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    
    photo = FSInputFile("Video/Glavnaya.mp4")
    await bot.send_animation(call.from_user.id, photo, caption='1️⃣ Получи свою личную ссылку — жми «⭐️ Заработать звезды»\n2️⃣ Приглашай друзей — 3⭐️ за каждого!\n\n✅ Дополнительно:\n<blockquote>— Ежедневные награды и промокоды (Профиль)\n— Выполняй задания\n— Крути рулетку и удвой баланс!\n— Участвуй в конкурсе на топ</blockquote>\n\n🔻 Главное меню', reply_markup=markup, parse_mode='html')
    
    
    
    
@dp.callback_query(F.data == 'cheak_subscribe')
async def calldata(call: CallbackQuery):
    
    pass

    
    
async def request_op(user_id, chat_id, gender=None):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Auth': '0003448041858122acc42b042ab2a14c7a0a880f488435620adcc6db96f6cf13',
            'Accept': 'application/json',
        }
        data = {
            'UserId': user_id, 
            'ChatId': chat_id
        }
        if gender:
            data['Gender'] = gender

        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.subgram.ru/request-op/', headers=headers, json=data) as response:
                if not response.ok:
                    logging.error('SubGram: %s' % str(await response.json()))
                    return 'ok', 400
                response_json = await response.json()
                
                if response_json['message'] == 'Успешно':
                    db = await aiosqlite.connect('users.db')
    
                    async with db.cursor() as cursor:
                        # Проверяем, есть ли пользователь в базе данных
                        await cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                        user_data = await cursor.fetchone()
                    
                        # Если пользователя нет, создаем его
                        if not user_data:
                            await cursor.execute("INSERT INTO users (user_id, referrer) VALUES (?, ?)", (user_id, referrer_id or None))
                            await db.commit()

                            # Если реферер существует, обновляем количество его рефералов и добавляем звезды
                            if referrer_id:
                                referrer_id = int(referrer_id)
                                # Увеличиваем количество рефералов у реферера
                                await cursor.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id = ?", (referrer_id,))
                                # Добавляем случайное количество звезд за нового реферала
                                stars_reward = 3 #Количество звёзд которое добавится за приглашение
                                await cursor.execute("UPDATE users SET stars = stars + ? WHERE user_id = ?", (stars_reward, referrer_id))
                                await db.commit()
                                # Отправляем рефереру сообщение о начислении звезд
                                await bot.send_message(referrer_id, text=f" Вам начислено {stars_reward} ⭐ за нового реферала!")
                    
                    #btn1 = InlineKeyboardButton(text='✨ Кликер', callback_data='clicker')
                    btn2 = InlineKeyboardButton(text='⭐ Заработать звёзды', callback_data='work_stars')
                    btn3 = InlineKeyboardButton(text='👤 Профиль', callback_data='profile')
                    btn4 = InlineKeyboardButton(text='💰 Вывод звёзд', callback_data='send_stars')
                    btn5 = InlineKeyboardButton(text='🎰 Рулетка', callback_data='ruletka')
                    btn6 = InlineKeyboardButton(text='📚 Инструкция', callback_data='instrykciya')
                    btn7 = InlineKeyboardButton(text='📝 Задания', callback_data='quest')
                    
                    #row_one = [btn1]
                    row_two = [btn2]
                    row_fre = [btn3, btn4]
                    row_fho = [btn5, btn6]
                    row_five = [btn7]
                    rows = [row_two, row_fre, row_fho, row_five]
                    markup = InlineKeyboardMarkup(inline_keyboard=rows)
                    
                    photo = FSInputFile("Video/Glavnaya.mp4")
                    await bot.send_animation(chat_id, photo, caption='1️⃣ Получи свою личную ссылку — жми «⭐️ Заработать звезды»\n2️⃣ Приглашай друзей — 3⭐️ за каждого!\n\n✅ Дополнительно:\n<blockquote>— Ежедневные награды и промокоды (Профиль)\n— Выполняй задания\n— Крути рулетку и удвой баланс!\n— Участвуй в конкурсе на топ</blockquote>\n\n🔻 Главное меню', reply_markup=markup, parse_mode='html')
                    
                    return response_json.get("status"), response_json.get("code")
                else:
                    return response_json.get("status"), response_json.get("code")

    except Exception as e:
        logging.error('SubGram: %s' % str(e))
        return 'ok', 400  
    
@dp.callback_query(lambda call: call.data.startswith("subgram"))
async def subgram_callback_query(call):
    global referrer_id
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if call.data == "subgram-op":
        status, code = await request_op(user_id, chat_id)
        if status == 'ok' and code == 200: #Если статус ok и code 200 (совокупность параметров означает, что пользователь подписан)
            pass
            
        elif status == 'ok':
            pass
            
        else:
            return
        
    elif call.data.startswith("subgram_gender_"):
        gender = call.data.split("_")[2]
        status, code = await request_op(user_id, chat_id, gender)
        if status == 'ok' and code == 200: #Если статус ok и code 200 (совокупность параметров означает, что пользователь подписан)
            pass
        
        elif status == 'ok':
            pass
        
        else:
            return
    
    
async def main() -> None:
    await dp.start_polling(bot)
    
asyncio.run(main())
