import telebot
from telebot import apihelper

bot = None


def init_bot(token):
    global bot
    bot = telebot.TeleBot(token)
    apihelper.proxy = {'https': 'http://54.37.136.149:3128'}
    from app import tel_case
