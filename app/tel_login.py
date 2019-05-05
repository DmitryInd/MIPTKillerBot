"""Functions for enter in group"""
# -*- coding: utf-8 -*-
from app import bot
from app import data_base
from app import usefull_functions


@bot.message_handler(commands=["create"])
def pre_create(message):
    """Starting of creating new group"""
    base = data_base.get_data("Users", "position",
                              id=message.chat.id)
    if base == -1:
        return
    number = base[0][0]
    if number != 9:
        return
    bot.send_message(message.chat.id, "Введите название новой группы:")
    data_base.update_record('users', 1, id=message.chat.id, position=11)


def create(message):
    """Creating of new group"""
    list_f = data_base.get_data('groups', 'name',
                                name="\'" + message.text + "\'")
    if list_f != -1:
        bot.send_message(message.chat.id, "Название уже занято")
        return
    data_base.create_record('groups', name="\'" + message.text + "\'",
                            administrator_id=message.chat.id, work="\'F\'")
    bot.send_message(message.chat.id, "Введите пароль:")
    data_base.update_record("Users", 1, id=message.chat.id,
                            game_id="\'" + message.text + "\'", position=12)


def password(message):
    """Setting up password"""
    data_base.update_record('groups', 1, administrator_id=message.chat.id,
                            password="\'" + message.text + "\'")
    bot.send_message(message.chat.id, "Подтвердите пароль:")
    data_base.update_record("Users", 1, id=message.chat.id, position=13)


def confirm_password(message):
    """Confirming password"""
    list_f = data_base.get_data('groups', "password",
                                administrator_id=message.chat.id)
    if list_f[0][0] != message.text:
        bot.send_message(message.chat.id, "Пароли не совпадают")
        bot.send_message(message.chat.id, "Введите пароль ещё раз:")
        data_base.update_record("Users", 1, id=message.chat.id, position=12)
        return
    data_base.update_record('groups', 1, administrator_id=message.chat.id,
                            work="\'T\'")
    bot.send_message(message.chat.id, "Вы стали администратором группы")
    bot.send_message(message.chat.id, "Если хотите выйти из неё введите /exit,"
                                      "если хотите удалить её введите"
                                      " /delete_group")
    bot.send_message(message.chat.id, "Чтобы завершить сбор игроков, введите"
                                      " /finish")
    data_base.update_record("Users", 1, id=message.chat.id, position=14)
    usefull_functions.generate_id(message.chat.id)


def login(message):
    """Entering in a group: input name"""
    list_f = data_base.get_data('groups', "name", "work",
                                name="\'" + message.text + "\'")
    if list_f == -1:
        bot.send_message(message.chat.id, "Такой группы не существует")
        return
    if list_f[0][1] != "T":
        bot.send_message(message.chat.id, "К этой группе нельзя присоединиться")
        return
    data_base.update_record("Users", 1, id=message.chat.id,
                            game_id="\'" + message.text + "\'", position=10)
    bot.send_message(message.chat.id, "Введите пароль:")


def login_password(message):
    """Entering in a group: input password"""
    list_f = data_base.get_data("Users", 'game_id', id=message.chat.id)
    list_f = data_base.get_data('groups', 'password', 'work',
                                name="\'" + list_f[0][0] + "\'")
    if list_f == -1:
        bot.send_message(message.chat.id, "Такой  группы уже не существует")
        data_base.update_record("Users", 1, id=message.chat.id,
                                game_id="NULL", position=9)
        return
    if list_f[0][1] != "T":
        bot.send_message(message.chat.id, "К этой группе уже нельзя"
                                          " присоединиться")
        data_base.update_record("Users", 1, id=message.chat.id,
                                game_id="NULL", position=9)
        return
    if list_f[0][0] != message.text:
        bot.send_message(message.chat.id, "Неправильное название группы"
                                          " или пароль")
        data_base.update_record("Users", 1, id=message.chat.id,
                                game_id="NULL", position=9)
        return
    data_base.update_record("Users", 1, id=message.chat.id, position=14)
    usefull_functions.generate_id(message.chat.id)
    bot.send_message(message.chat.id, "Вы вошли в группу")
    bot.send_message(message.chat.id, "Если хотите выйти из неё,"
                                      " введите /exit,")
