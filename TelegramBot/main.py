#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests
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
            main_menu_message(message)
    except Exception:
        bot.send_message(message.chat.id, 'Логин или пароль неверны.')
        login_message(message)


def main_menu_message(message):
    msg = 'Что желаете сделать?'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Статистика текущей недели'))
    markup.add(types.KeyboardButton('Статистика предыдущей недели'))
    markup.add(types.KeyboardButton('Выйти из аккаунта'))
    bot.send_message(message.chat.id, msg, reply_markup=markup)


def week_stats_message(message, week_off):
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    msg = ''
    week = requests.get(f'http://127.0.0.1:5000/api/users/5/weeks/{week_off}').json()
    for i, day in enumerate(week):
        msg += f'<b>{days[i]}</b>\n'
        msg += f'Завтрак: {day["breakfast"]} кал\n'
        msg += f'Обед: {day["lunch"]} кал\n'
        msg += f'Ужин: {day["dinner"]} кал\n'
        msg += f'Вне приёмов пищи: {day["other_gains"]} кал\n'
        msg += f'Потрачено: {day["lost"]} кал\n'
        msg += f'Заметка: {day["note"]}\n'
        msg += '\n'

    bot.send_message(message.chat.id, msg, parse_mode='HTML')


@bot.message_handler(content_types=['text'])
def message_reply(message):
    if message.text == 'Авторизация':
        login_message(message)
    if message.text == 'Статистика текущей недели':
        week_stats_message(message, 0)
    if message.text == 'Статистика предыдущей недели':
        week_stats_message(message, 1)
    if message.text == 'Выйти из аккаунта':
        bot.send_message(message.chat.id, 'Выход выполнен успешно.')
        start_message(message)


bot.infinity_polling()