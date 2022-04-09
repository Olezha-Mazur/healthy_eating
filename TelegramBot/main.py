#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from turtle import up
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler


TOKEN = '5149274621:AAHNf_XDRwWR5M4OhpJXFjx2kwWfF9oC6-s'


def start(update, context):
	update.message.reply_text(
		'Привет! Я - бот правльного питания!'
	)


def main():
	updater = Updater(TOKEN)
	dp = updater.dispatcher

	dp.add_handler(CommandHandler('start', start))

	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
	main()
