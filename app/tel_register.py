"""Functions for entry information about users"""
# -*- coding: utf-8 -*-
from app import bot
from telebot import types
from app import data_base
from app import usefull_functions


@bot.message_handler(commands=["start"])
def start(message):
    """Entering a user into database"""
    base = data_base.get_data("Users", "id", "position", id=message.chat.id)
    try:
        if base == -1:
            raise Exception
        if base[0][1] == 0 or base[0][1] == 1:
            raise Exception
        else:
            bot.send_message(message.chat.id, "Ты уже начал игру")
    except Exception:
        if base == -1:
            data_base.create_record('users', id=message.chat.id)
        data_base.update_record('users', 1, id=message.chat.id,
                                position=1)
        keyboard = types.InlineKeyboardMarkup()
        callback_button0 = types.InlineKeyboardButton(text="Да",
                                                      callback_data="yes")
        callback_button1 = types.InlineKeyboardButton(
            text="Нет", callback_data="no")
        keyboard.add(callback_button0)
        keyboard.add(callback_button1)
        bot.send_message(message.chat.id, "Хочешь сыграть в киллера?",
                         reply_markup=keyboard)


def agreement(call):
    """Agreement om start registration"""
    if call.data == "yes":
        first_name(call)
    elif call.data == "no":
        data_base.update_record('users', 1, id=call.message.chat.id, position=0)
        bot.send_message(call.message.chat.id, "До следующей игры")
    else:
        bot.send_message(call.message.chat.id, "Такого варианта ответа нет")


def first_name(call):
    """Request to input name"""
    bot.send_message(call.message.chat.id,
                     'Здравствуй, у меня есть для тебя заказ.'
                     ' Сообщи свои данные чтобы я мог назначить'
                     ' тебя подальше от врагов. Будет сложно,'
                     ' но некоторое время ты ещё можешь отказаться (/stop)')
    bot.send_message(call.message.chat.id, "Введите своё имя:")
    data_base.update_record('users', 1, id=call.message.chat.id, position=2)


def surname(message):
    """Request to input surname"""
    data_base.update_record("Users", 1, id=message.chat.id,
                            first_name="\'" + message.text + "\'", position=3)
    bot.send_message(message.chat.id, "Введите свою фамилию:")


def choosing_school(message):
    """Request on choosing MIPT-school"""
    data_base.update_record("Users", 1, id=message.chat.id,
                            last_name="\'" + message.text + "\'", position=4)
    list_f = [i[0] for i in list(set(data_base.get_data('faculty', 'name')))]
    list_f.sort()
    keyboard = types.InlineKeyboardMarkup()
    for j in range(len(list_f)):
        callback_button = types.InlineKeyboardButton(
            text=str(list_f[j]), callback_data=str(j) + "f")
        keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Выберите физтех-школу,"
                                      " в которой вы учитесь:",
                     reply_markup=keyboard)


def choosing_faculty(call):
    """Request on choosing faculty"""
    if call.data[-1:] != "f" or not call.data[:-1].isdigit():
        return
    ans = int(call.data[:-1])
    list_f = [i[0] for i in list(set(data_base.get_data('faculty', 'name')))]
    list_f.sort()
    data_base.update_record("Users", 1, id=call.message.chat.id,
                            faculty="\'" + list_f[ans] + "\'", position=5)
    list_f = data_base.get_data('faculty', 'direction',
                                name="\'" + list_f[ans] + "\'")
    list_f.sort(key=usefull_functions.sort_by_first)
    keyboard = types.InlineKeyboardMarkup()
    for j in range(len(list_f)):
        callback_button = types.InlineKeyboardButton(
            text=str(list_f[j][0]), callback_data=str(j) + "d")
        keyboard.add(callback_button)

    bot.send_message(call.message.chat.id, "Выберите факультет,"
                                           " на котором вы учитесь:",
                     reply_markup=keyboard)


def physical_culture(call):
    """Output options of sections of physical culture"""
    if call.data[-1:] != "d" or not call.data[:-1].isdigit():
        return
    ans = int(call.data[:-1])
    list_f = data_base.get_data('users', 'faculty', id=call.message.chat.id)
    list_f = data_base.get_data('faculty', 'direction',
                                name="\'" + list_f[0][0] + "\'")
    list_f.sort(key=usefull_functions.sort_by_first)
    data_base.update_record("Users", 1, id=call.message.chat.id,
                            direction="\'" + list_f[ans][0] + "\'", position=6)
    list_f = data_base.get_data('sections', 'section_nm', 'section_id')
    list_f.sort(key=usefull_functions.sort_by_first)
    keyboard = types.InlineKeyboardMarkup()
    for j in list_f:
        callback_button = types.InlineKeyboardButton(
            text=str(j[0]), callback_data=str(j[1]) + "s")
        keyboard.add(callback_button)

    bot.send_message(call.message.chat.id,
                     "Выберите секцию по физкультуре, на которую вы ходите:",
                     reply_markup=keyboard)


def corp(call):
    """Request to input number of corpus"""
    if call.data[-1:] != "s" or not call.data[:-1].isdigit():
        return
    ans = int(call.data[:-1])
    ans = data_base.get_data('sections', 'section_nm', section_id=str(ans))
    data_base.update_record("Users", 1, id=call.message.chat.id,
                            section="\'" + ans[0][0] + "\'", position=7)
    bot.send_message(call.message.chat.id,
                     "Введите номер корпуса, в котором вы живёте:")


def room(message):
    """Request to input number of room"""
    if not message.text.isdigit():
        bot.send_message(message.chat.id,
                         "Можно использовать только цифры")
        return
    data_base.update_record("Users", 1, id=message.chat.id,
                            corpus=int(message.text), position=8)
    bot.send_message(message.chat.id,
                     "Введите номер комнаты, в которой вы живёте:")


def enter_in_game(message):
    """Suggestion to enter in game"""
    if not message.text.isdigit():
        bot.send_message(message.chat.id,
                         "Можно использовать только цифры")
        return
    if usefull_functions.stable(message):
        data_base.update_record("Users", 1, id=message.chat.id,
                                room=int(message.text), position=14)
    else:
        data_base.update_record("Users", 1, id=message.chat.id,
                                room=int(message.text), position=9)
    bot.send_message(message.chat.id,
                     "Ваши данные сохранены, если хотите поменять их, введите"
                     " /update, если хотите полностью удалить, введите /delete")
    bot.send_message(message.chat.id,
                     "Введите название команды, в которой вы хотите играть,"
                     " или создайте свою (/create).")

