"""Function for control game"""
# -*- coding: utf-8 -*-
import random
from app import bot
from app import data_base
from app import graph
from app import usefull_functions
from app import tel_case as tel


@bot.message_handler(commands=["finish"])
def pre_finish(message):
    """Confirmation of starting of game"""
    base = data_base.get_data("Users", "position",
                              id=message.chat.id)
    if base == -1:
        return
    number = base[0][0]
    if number != 14:
        bot.send_message(message.chat.id, "Вы не находитесь в группе")
        return
    x = data_base.get_data('groups', 'name', administrator_id=message.chat.id)
    if x == -1:
        bot.send_message(message.chat.id, "Это может сделать только"
                                          " администратор группы")
        return
    number = usefull_functions.add_stack(number, 24)
    data_base.update_record('users', 1, id=message.chat.id,
                            position=number)
    tel.confirmation(message, "finish_yes", "finish_no")


def distance(u, v):
    """Distance between users"""
    ans = 0
    if u[2] != v[2]:
        ans += 6
    elif u[3] != v[3]:
        ans += 3

    if u[4] != v[4]:
        ans += 2

    if u[5] != v[6]:
        ans += 4
    elif u[5] != v[6]:
        ans += 2

    return ans + random.randint(0, 4)


def finish(call):
    """Starting match"""
    x = data_base.get_data('groups', 'name',
                           administrator_id=call.message.chat.id)
    if x == -1:
        bot.send_message(call.message.chat.id, "Это может сделать только "
                                               "администратор группы")
        return
    if call.data == "finish_no":
        tel.canceled(call)
    elif call.data == "finish_yes":
        list_p = data_base.get_data('users', 'id', 'play_id', 'faculty',
                                    'direction', 'section', 'corpus', 'room',
                                    'first_name', 'last_name',
                                    game_id="\'" + x[0][0] + "\'")
        list_p = [i for i in list_p if i[1] is not None]
        if len(list_p) < 2:
            bot.send_message(call.message.chat.id, "Людей не достаточно")
        else:
            q = graph.ListGraph(len(list_p))
            for i in range(len(list_p)):
                for j in range(len(list_p)):
                    if i != j:
                        q.add_connection(i, j, distance(list_p[i], list_p[j]))

            path = q.max_road()
            for i in range(len(path) - 1):
                data_base.update_record('users', 1, id=list_p[path[i]][0],
                                        aim=list_p[path[i + 1]][0])
                bot.send_message(list_p[path[i]][0], "Игра началась.\n"
                                                     "Ваша цель:")
                bot.send_message(list_p[path[i]][0], list_p[path[i + 1]][7]
                                 + " " + list_p[path[i + 1]][8])
                bot.send_message(list_p[path[i]][0], "Ваш id:")
                bot.send_message(list_p[path[i]][0], list_p[path[i]][1])
                bot.send_message(list_p[path[i]][0], "Когда вас убьют, введите"
                                                     " /killed и id убийцы")
            data_base.update_record('groups', 1, name="\'" + x[0][0] + "\'",
                                    work="\'P\'")
        a = data_base.get_data('users', 'position',
                               id=call.message.chat.id)[0][0]
        a = usefull_functions.pop_stack(a)
        data_base.update_record('users', 1, id=call.message.chat.id,
                                position=a)


@bot.message_handler(commands=["killed"])
def pre_kill(message):
    """Starting of confirmation of murder"""
    base = data_base.get_data("Users", "id", aim=message.chat.id)
    if base == -1:
        return
    number = data_base.get_data("Users", "position", id=message.chat.id)[0][0]
    if number != 14:
        bot.send_message(message.chat.id, "Вы не находитесь в группе")
        return
    bot.send_message(message.chat.id, "Введите код убийцы:")
    base = data_base.get_data("Users", "position", id=message.chat.id)
    if base == -1:
        return
    data_base.update_record('users', 1, id=message.chat.id, position=25)


def killed(message):
    """Confirmation of murder"""
    base = data_base.get_data("Users", "id", "play_id", "game_id", "first_name",
                              "last_name", aim=message.chat.id)
    if base != -1:
        if base[0][1] != int(message.text):
            bot.send_message(message.chat.id, "Это не ваш убийца")
            usefull_functions.generate_id(base[0][0])
            x = data_base.get_data('users', 'play_id', id=base[0][0])[0][0]
            bot.send_message(base[0][0], "Ваш новый игровой id:")
            bot.send_message(base[0][0], str(x))
        else:
            aim_id = data_base.get_data("Users", "aim",
                                        id=message.chat.id)[0][0]
            if aim_id == base[0][0]:
                data_base.update_record('users', 1, id=message.chat.id, aim=0)
                usefull_functions.generate_id(base[0][0])
                data_base.update_record('users', 1, id=base[0][0], aim=0)
                bot.send_message(base[0][0], "Поздравляем с убийством!")
                bot.send_message(base[0][0], "Вы выиграли!")
                list_q = data_base.get_data('users', 'id', 'play_id',
                                            game_id="\'" + base[0][2] + "\'")
                list_q = [i[0] for i in list_q if i[1] != 0 and i[0] != aim_id]
                for i in list_q:
                    bot.send_message(i, "Игра окончена. Победитель:")
                    bot.send_message(i, base[0][3] + " " + base[0][4])
                data_base.update_record('groups', 1,
                                        name="\'" + base[0][2] + "\'",
                                        work="'T'")
            else:
                new_aim = data_base.get_data('users', 'first_name', 'last_name',
                                             id=aim_id)[0]
                data_base.update_record('users', 1, id=message.chat.id, aim=0)
                usefull_functions.generate_id(base[0][0])
                data_base.update_record('users', 1, id=base[0][0], aim=aim_id)
                bot.send_message(base[0][0], "Поздравляем с убийством!")
                bot.send_message(base[0][0], "Ваша новая цель:")
                bot.send_message(base[0][0], new_aim[0] + " " + new_aim[1])
                x = data_base.get_data('users', 'play_id', id=base[0][0])
                bot.send_message(base[0][0], "Ваш новый игровой id:")
                bot.send_message(base[0][0], str(x[0][0]))
                bot.send_message(message.chat.id, "Вы выбыли из игры")
    else:
        bot.send_message(message.chat.id, "У вас нет убийцы")
    data_base.update_record('users', 1, id=message.chat.id, position=14)
