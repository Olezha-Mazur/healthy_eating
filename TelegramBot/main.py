#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from turtle import up
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

from bot_token import TOKEN


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
