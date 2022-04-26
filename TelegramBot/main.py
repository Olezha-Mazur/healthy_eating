#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sqlite3
import telebot
from telebot import types
from werkzeug.security import check_password_hash, generate_password_hash

from bot_token import TOKEN


bot = telebot.TeleBot(TOKEN)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

con = sqlite3.connect('../db/users.sqlite', check_same_thread=False)
cur = con.cursor()

LOGIN, PASSWORD = '', ''


@bot.message_handler(commands=['start'])
def start_message(message):
    msg = "Привет! Я - бот правильного питания!\nАвторизуйтесь, пожалуйста"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Авторизация'))
    bot.send_message(message.chat.id, msg, reply_markup=markup)


@bot.message_handler(commands=['login'])
def login_message(message):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 'Введите Ваш логин:', reply_markup=markup)
    bot.register_next_step_handler(message, get_login_message)


def get_login_message(message):
    global login
    login = message.text
    bot.send_message(message.chat.id, 'Теперь введите пароль:')
    bot.register_next_step_handler(message, get_password_message)


def get_password_message(message):
    global password
    password = message.text
    try_to_login_message(message)


def try_to_login_message(message):
    try:
        hashed_password = cur.execute(
            """SELECT hashed_password FROM users WHERE name = ?""", (login,)
        ).fetchone()[0]
        if not check_password_hash(hashed_password, password):
            bot.send_message(message.chat.id, 'Логин или пароль неверны.')
            login_message(message)
        else:
            LOGIN, PASSWORD = login, hashed_password
            bot.send_message(message.chat.id, f'Вход выполнен успешно!\nДобро пожаловать, {LOGIN}!')
    except Exception:
        bot.send_message(message.chat.id, 'Логин или пароль неверны.')
        login_message(message)


def check_auth_message(message):
    if len(LOGIN) == 0 or len(PASSWORD) == 0:
        bot.message_handler(message.chat.id, 'Необходимо авторизоваться!')
        return False
    return True


@bot.message_handler(content_types=['text'])
def message_reply(message):
    if message.text == 'Авторизация':
        login_message(message)
    if message.text == 'Выход':
        pass


bot.infinity_polling()