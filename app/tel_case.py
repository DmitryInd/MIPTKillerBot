"""Processing of messages to bot"""
# -*- coding: utf-8 -*-
from app import bot
from telebot import types
from app import data_base
from app import usefull_functions
from app import tel_change, tel_game, tel_login, tel_register


# Standard confirmed functions
def confirmation(message, c_yes, c_no):
    """Confirmation"""
    keyboard = types.InlineKeyboardMarkup()
    callback_button0 = types.InlineKeyboardButton(text="Да",
                                                  callback_data=c_yes)
    callback_button1 = types.InlineKeyboardButton(
        text="Нет", callback_data=c_no)
    keyboard.add(callback_button0)
    keyboard.add(callback_button1)
    bot.send_message(message.chat.id, "Уверен?",
                     reply_markup=keyboard)


def canceled(call):
    """Cancellation of confirmation"""
    bot.send_message(call.message.chat.id, "Действие отменено")
    ans = data_base.get_data('users', 'position', id=call.message.chat.id)[0][0]
    number = usefull_functions.pop_stack(ans)
    data_base.update_record('users', 1, id=call.message.chat.id,
                            position=number)


# Command functions
@bot.message_handler(commands=["stop"])
def stop(message):
    """Stopping of process"""
    base = data_base.get_data("Users", "position",
                              id=message.chat.id)
    if base == -1:
        return
    a = base[0][0]
    number = usefull_functions.get_stack(a)
    a = usefull_functions.pop_stack(a)
    if a == 0:
        if number == 9 or number == 14:  # стабильные состояния
            return
        if number > 14:
            if usefull_functions.stable(message):
                a = 14
            else:
                a = 9
        elif number > 10:
            group = data_base.get_data('users', 'game_id',
                                       id=message.chat.id)[0][0]
            if group is not None:
                data_base.delete_record('groups', name="\'" + group + "\'")
                data_base.update_record('users', 1, id=message.chat.id,
                                        game_id='NULL')
            a = 9
        elif number > 8:
            group = data_base.get_data('users', 'game_id',
                                       id=message.chat.id)[0][0]
            if group is not None:
                data_base.update_record('users', 1, id=message.chat.id,
                                        game_id='NULL')
            a = 9
        else:
            if usefull_functions.full_record(message):
                if usefull_functions.stable(message):
                    a = 14
                else:
                    a = 9
            else:
                a = 0
    data_base.update_record('users', 1, id=message.chat.id, position=a)
    bot.send_message(message.chat.id, "Действие приостановлено")
    data_base.update_record('users', 1, id=message.chat.id, position=a)


# Launching functions depending on the position
@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    base = data_base.get_data("Users", "id", "position",
                              id=message.chat.id)
    if base == -1:
        return
    number = base[0][1]
    number = usefull_functions.get_stack(number)
    try:
        func = {2: tel_register.surname, 3: tel_register.choosing_school,
                7: tel_register.room, 8: tel_register.enter_in_game,
                9: tel_login.login, 10: tel_login.login_password,
                11: tel_login.create, 12: tel_login.password,
                13: tel_login.confirm_password, 25: tel_game.killed}
        func[number](message)  # вызов функции
    except Exception as e:
        print(e)
        pass


@bot.callback_query_handler(func=lambda call: True)
def input_keyboard(call):
    base = data_base.get_data("Users", "position",
                              id=call.message.chat.id)
    if base == -1:
        return
    number = base[0][0]
    number = usefull_functions.get_stack(number)
    try:
        func = {1: tel_register.agreement, 4: tel_register.choosing_faculty,
                5: tel_register.physical_culture, 6: tel_register.corp,
                20: tel_change.change_admin, 21: tel_change.update,
                22: tel_change.tel_exit, 23: tel_change.tel_delete,
                24: tel_game.finish}
        func[number](call)  # вызов функции
    except Exception as e:
        print(e)
        pass
