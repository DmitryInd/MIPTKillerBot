"""Functions for changing record"""
# -*- coding: utf-8 -*-
import random
from app import bot
from telebot import types
from app import data_base
import copy
from app import usefull_functions
from app import tel_case as tel
from app import tel_game


@bot.message_handler(commands=["update"])
def pre_update(message):
    """Confirmation of update"""
    base = data_base.get_data("Users", "position",
                              id=message.chat.id)
    if base == -1:
        return
    number = base[0][0]
    if number > 14 or 9 < number < 14:
        return
    i = usefull_functions.add_stack(number, 21)
    data_base.update_record('users', 1, id=message.chat.id,
                            position=i)
    tel.confirmation(message, "update_yes", "update_no")


def update(call):
    """Updating data in record of users"""
    if call.data == "update_no":
        tel.canceled(call)
    elif call.data == "update_yes":
        bot.send_message(call.message.chat.id, "Введите своё имя:")
        data_base.update_record('users', 1, id=call.message.chat.id, position=2)


@bot.message_handler(commands=["exit"])
def pre_exit(message):
    """Confirmation of exiting from group"""
    base = data_base.get_data("Users", "position",
                              id=message.chat.id)
    if base == -1:
        return
    number = base[0][0]
    if usefull_functions.get_stack(number) != 14:
        return
    i = usefull_functions.add_stack(number, 22)
    data_base.update_record('users', 1, id=message.chat.id,
                            position=i)
    tel.confirmation(message, "exit_yes", "exit_no")


def next_exit(call):
    """Final of exiting"""
    number = data_base.get_data('users', 'position',
                                id=call.message.chat.id)[0][0]
    number = usefull_functions.pop_stack(number)
    if number == 14:
        data_base.update_record('users', 1, id=call.message.chat.id,
                                game_id='NULL', position=9)
        bot.send_message(call.message.chat.id, "Вы вышли из группы")
        bot.send_message(call.message.chat.id, "Чтобы начать играть,"
                                               " войдите в группу"
                                               " (введите логин:) или"
                                               " создайте новую (/create)")
    else:
        data_base.update_record('users', 1, id=call.message.chat.id,
                                game_id='NULL', position=number)
        next_func = {23: tel_delete}
        ans = {23: "delete_yes"}
        number = usefull_functions.get_stack(number)
        try:
            if ans[number] is None:
                next_func[number](call.message)
                return
            call.data = ans[number]
            next_func[number](call)
        except Exception as e:
            print(e)


def tel_exit(call):
    """Exiting from a group"""
    if call.data == "exit_no":
        tel.canceled(call)
    elif call.data == "exit_yes":
        group = data_base.get_data('users', 'game_id',
                                   id=call.message.chat.id)[0][0]
        a = group
        group = data_base.get_data('users', 'aim',
                                   id=call.message.chat.id)[0][0]
        if group != 0:
            copy_message = copy.copy(call.message)
            base = data_base.get_data("Users", "play_id",
                                      aim=call.message.chat.id)
            copy_message.text = str(base[0][0])
            tel_game.killed(copy_message)
        if data_base.get_data('groups', 'name',
                              administrator_id=call.message.chat.id) != -1:
            people = data_base.get_data('users', 'id', 'first_name',
                                        'last_name', game_id="\'" + a + "\'")
            if len(people) == 1:
                data_base.delete_record('groups', name="\'" + a + "\'")
            else:
                keyboard = types.InlineKeyboardMarkup()
                for i in people:
                    if i[0] != call.message.chat.id:
                        callback_button = types.InlineKeyboardButton(
                            text=i[1] + " " + i[2], callback_data=i[0])
                        keyboard.add(callback_button)
                bot.send_message(call.message.chat.id, "Выберите наследника:",
                                 reply_markup=keyboard)
                number = data_base.get_data('users', 'position',
                                            id=call.message.chat.id)[0][0]
                number = usefull_functions.pop_stack(number)
                number = usefull_functions.add_stack(number, 20)
                data_base.update_record('users', 1, id=call.message.chat.id,
                                        position=number)
                return

        next_exit(call)


def change_admin(call):
    """Changing of admin"""
    a = data_base.get_data('users', 'game_id', id=call.message.chat.id)[0][0]
    b = data_base.get_data('users', 'game_id', id=call.data)[0][0]
    if a != b:
        bot.send_message(call.message.chat.id, "Этот участник уже вышел"
                                               " из группы")
        call.data = "exit_yes"
        tel_exit(call)
        return
    data_base.update_record('groups', 1, name="\'" + a + "\'",
                            administrator_id=call.data)
    bot.send_message(call.data, "Теперь вы администратор группы")
    bot.send_message(call.data, "Чтобы завершить сбор игроков, введите /finish")
    next_exit(call)


@bot.message_handler(commands=["delete"])
def pre_delete(message):
    """Prepare for deleting record"""
    base = data_base.get_data("Users", "position",
                              id=message.chat.id)
    if base == -1:
        return
    number = base[0][0]
    number = usefull_functions.add_stack(number, 23)
    data_base.update_record('users', 1, id=message.chat.id,
                            position=number)
    tel.confirmation(message, "delete_yes", "delete_no")


def tel_delete(call):
    """Deleting of record of user"""
    if call.data == "delete_no":
        tel.canceled(call)
    elif call.data == "delete_yes":
        group = data_base.get_data('users', 'game_id',
                                   id=call.message.chat.id)[0][0]
        if group is not None:
            number = data_base.get_data('users', 'position',
                                        id=call.message.chat.id)[0][0]
            number = usefull_functions.add_stack(number, 20)
            data_base.update_record('users', 1, id=call.message.chat.id,
                                    position=number)
            call.data = "exit_yes"
            tel_exit(call)
            return
        data_base.delete_record('users', id=call.message.chat.id)
        bot.send_message(call.message.chat.id, "Вы удалены из базы данных")
