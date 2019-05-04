# -*- coding: utf-8 -*-
import random
from app import bot
from telebot import types
from app import data_base
import copy
from app import graph


def sort_by_first(a):
    """Ключ для сортировки"""
    return a[0]


def add_stack(a, command):
    """Добавление команды в стек"""
    number = copy.copy(a)
    i = 100
    while i < number:
        i *= 100
    command = i * command
    return number + command


def pop_stack(a):
    """Стирание команды из стека"""
    number = copy.copy(a)
    i = 100
    while i < number:
        i *= 100
    i /= 100
    number = number % i
    return number


def get_stack(a):
    """Возращает последнюю команду"""
    number = copy.copy(a)
    while number > 100:
        number = int(number/100)
    return number


def generate_id(pl_id):
    """Генерирует участникам уникальные коды"""
    group = data_base.get_data('users', 'game_id', id=pl_id)[0][0]
    group = data_base.get_data('users', 'play_id', game_id="'" + group + "'")
    group = [i[0] for i in group] if group != -1 else []
    p_id = random.randint(1, 1000000)
    while graph.search(group, p_id) != -1:
        p_id = random.randint(1, 1000000)
    data_base.update_record('users', 1, id=pl_id, play_id=p_id)


def stable(message):
    """Проверяет на наличие в группе"""
    group = data_base.get_data('users', 'game_id', id=message.chat.id)[0][0]
    if group is None:
        return False
    return True


def full_record(message):
    """Проверяет на целостность записи"""
    group = data_base.get_data('users', 'first_name', 'last_name', 'faculty',
                               'direction', 'section', 'corpus', 'room'
                               , id=message.chat.id)[0]
    for i in group:
        if i is None:
            return False

    return True


def confirmation(message, c_yes, c_no):
    """Подтверждение"""
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
    """Отмена подтверждения"""
    bot.send_message(call.message.chat.id, "Действие отменено")
    ans = data_base.get_data('users', 'position', id=call.message.chat.id)[0][0]
    number = pop_stack(ans)
    data_base.update_record('users', 1, id=call.message.chat.id,
                            position=number)


def first_name(call):
    """Просьба ввода имени"""
    bot.send_message(call.message.chat.id,
                     'Здравствуй, у меня есть для тебя заказ.'
                     ' Сообщи свои данные чтобы я мог назначить'
                     ' тебя подальше от врагов. Будет сложно,'
                     ' но некоторое время ты ещё можешь отказаться (/stop)')
    bot.send_message(call.message.chat.id, "Введите своё имя:")
    data_base.update_record('users', 1, id=call.message.chat.id, position=2)


def surname(message):
    """Просьба ввода фамилии"""
    data_base.update_record("Users", 1, id=message.chat.id,
                            first_name="\'" + message.text + "\'", position=3)
    bot.send_message(message.chat.id, "Введите свою фамилию:")


def agreement(call):
    """Соглашение на начало регистрации"""
    if call.data == "yes":
        first_name(call)
    elif call.data == "no":
        data_base.update_record('users', 1, id=call.message.chat.id, position=0)
        bot.send_message(call.message.chat.id, "До следующей игры")
    else:
        bot.send_message(call.message.chat.id, "Такого варианта ответа нет")


def choosing_direction(message):
    """Выдача запроса на направление"""
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


def direction(call):
    """Выбор факультета"""
    if call.data[-1:] != "f" or not call.data[:-1].isdigit():
        return
    ans = int(call.data[:-1])
    list_f = [i[0] for i in list(set(data_base.get_data('faculty', 'name')))]
    list_f.sort()
    data_base.update_record("Users", 1, id=call.message.chat.id,
                            faculty="\'" + list_f[ans] + "\'", position=5)
    list_f = data_base.get_data('faculty', 'direction',
                                name="\'" + list_f[ans] + "\'")
    list_f.sort(key=sort_by_first)
    keyboard = types.InlineKeyboardMarkup()
    for j in range(len(list_f)):
        callback_button = types.InlineKeyboardButton(
            text=str(list_f[j][0]), callback_data=str(j) + "d")
        keyboard.add(callback_button)

    bot.send_message(call.message.chat.id, "Выберите факультет,"
                                           " на котором вы учитесь:",
                     reply_markup=keyboard)


def physical_culture(call):
    """Вывод варинтов секции по физкультуре"""
    if call.data[-1:] != "d" or not call.data[:-1].isdigit():
        return
    ans = int(call.data[:-1])
    list_f = data_base.get_data('users', 'faculty', id=call.message.chat.id)
    list_f = data_base.get_data('faculty', 'direction',
                                name="\'" + list_f[0][0] + "\'")
    list_f.sort(key=sort_by_first)
    data_base.update_record("Users", 1, id=call.message.chat.id,
                            direction="\'" + list_f[ans][0] + "\'", position=6)
    list_f = data_base.get_data('sections', 'section_nm', 'section_id')
    list_f.sort(key=sort_by_first)
    keyboard = types.InlineKeyboardMarkup()
    for j in list_f:
        callback_button = types.InlineKeyboardButton(
            text=str(j[0]), callback_data=str(j[1]) + "s")
        keyboard.add(callback_button)

    bot.send_message(call.message.chat.id,
                     "Выберите секцию по физкультуре, на которую вы ходите:",
                     reply_markup=keyboard)


def corp(call):
    """Просьба ввести номер корпуса"""
    if call.data[-1:] != "s" or not call.data[:-1].isdigit():
        return
    ans = int(call.data[:-1])
    ans = data_base.get_data('sections', 'section_nm', section_id=str(ans))
    data_base.update_record("Users", 1, id=call.message.chat.id,
                            section="\'" + ans[0][0] + "\'", position=7)
    bot.send_message(call.message.chat.id,
                     "Введите номер корпуса, в котором вы живёте:")


def room(message):
    """Просьба ввести номер комнаты"""
    if not message.text.isdigit():
        bot.send_message(message.chat.id,
                         "Можно использовать только цифры")
        return
    data_base.update_record("Users", 1, id=message.chat.id,
                            corpus=int(message.text), position=8)
    bot.send_message(message.chat.id,
                     "Введите номер комнаты, в которой вы живёте:")


def enter_in_game(message):
    """Предложение войти в игру"""
    if not message.text.isdigit():
        bot.send_message(message.chat.id,
                         "Можно использовать только цифры")
        return
    if stable(message):
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


def update(call):
    """Обновлене данных в записи пользователя"""
    if call.data == "update_no":
        canceled(call)
    elif call.data == "update_yes":
        bot.send_message(call.message.chat.id, "Введите своё имя:")
        data_base.update_record('users', 1, id=call.message.chat.id, position=2)


def next_exit(call):
    """Жизнь после выхода"""
    number = data_base.get_data('users', 'position',
                                id=call.message.chat.id)[0][0]
    a = pop_stack(number)
    number = get_stack(a)
    if number == 14:
        a = pop_stack(a)
        a = add_stack(a, 9)
        data_base.update_record('users', 1, id=call.message.chat.id,
                                game_id='NULL', position=a)
        bot.send_message(call.message.chat.id, "Вы вышли из группы")
        bot.send_message(call.message.chat.id, "Чтобы начать играть,"
                                               " войдите в группу"
                                               " (введите логин:) или"
                                               " создайте новую (/create)")
    else:
        data_base.update_record('users', 1, id=call.message.chat.id,
                                game_id='NULL', position=a)
        next_func = {23: tel_delete}
        ans = {23: "delete_yes"}
        try:
            if ans[number] is None:
                next_func[number](call.message)
                return
            call.data = ans[number]
            next_func[number](call)
        except Exception as e:
            print(e)


def tel_exit(call):
    """Выход из группы"""
    if call.data == "exit_no":
        canceled(call)
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
            killed(copy_message)
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
                number = pop_stack(number)
                number = add_stack(number, 20)
                data_base.update_record('users', 1, id=call.message.chat.id,
                                        position=number)
                return

        next_exit(call)


def change_admin(call):
    """Измение админа"""
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
    next_exit(call)


def tel_delete(call):
    """Удаление аккаунта"""
    if call.data == "delete_no":
        canceled(call)
    elif call.data == "delete_yes":
        group = data_base.get_data('users', 'game_id',
                                   id=call.message.chat.id)[0][0]
        if group is not None:
            number = data_base.get_data('users', 'position',
                                        id=call.message.chat.id)[0][0]
            number = add_stack(number, 20)
            data_base.update_record('users', 1, id=call.message.chat.id,
                                    position=number)
            call.data = "exit_yes"
            tel_exit(call)
            return
        data_base.delete_record('users', id=call.message.chat.id)
        bot.send_message(call.message.chat.id, "Вы удалены из базы данных")


def distance(u, v):
    """Расстояние между игроками"""
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
    """Начинает матч"""
    x = data_base.get_data('groups', 'name',
                           administrator_id=call.message.chat.id)
    if x == -1:
        bot.send_message(call.message.chat.id, "Это может сделать только "
                                               "администратор группы")
        return
    if call.data == "finish_no":
        canceled(call)
    elif call.data == "finish_yes":
        list_p = data_base.get_data('users', 'id', 'play_id', 'faculty',
                                    'direction', 'section', 'corpus', 'room',
                                    'first_name', 'last_name',
                                    game_id="\'" + x[0][0] + "\'")
        list_p = [i for i in list_p if i[1] is not None]
        q = graph.ListGraph(len(list_p))
        for i in range(len(list_p)):
            for j in range(len(list_p)):
                if i != j:
                    q.add_connection(i, j, distance(list_p[i], list_p[j]))

        path = q.max_road()
        for i in range(len(path) - 1):
            data_base.update_record('users', 1, id=list_p[path[i]][0],
                                    aim=list_p[path[i + 1]][0])
            bot.send_message(list_p[path[i]][0], "Игра началась.\nВаша цель:")
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
        a = pop_stack(a)
        data_base.update_record('users', 1, id=call.message.chat.id,
                                position=a)


def killed(message):
    """Признание убийства"""
    base = data_base.get_data("Users", "id", "play_id", "game_id", "first_name",
                              "last_name", aim=message.chat.id)
    if base != -1:
        if base[0][1] != int(message.text):
            bot.send_message(message.chat.id, "Это не ваш убийца")
            generate_id(base[0][0])
            x = data_base.get_data('users', 'play_id', id=base[0][0])[0][0]
            bot.send_message(base[0][0], "Ваш новый игровой id:")
            bot.send_message(base[0][0], str(x))
        else:
            aim_id = data_base.get_data("Users", "aim",
                                        id=message.chat.id)[0][0]
            if aim_id == base[0][0]:
                data_base.update_record('users', 1, id=message.chat.id, aim=0)
                generate_id(base[0][0])
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
                generate_id(base[0][0])
                data_base.update_record('users', 1, id=base[0][0], aim=aim_id)
                bot.send_message(base[0][0], "Поздравляем с убийством!")
                bot.send_message(base[0][0], "Ваша новая цель:")
                bot.send_message(base[0][0], new_aim[0] + " " + new_aim[1])
                x = data_base.get_data('users', 'play_id', id=base[0][0])
                bot.send_message(base[0][0], "Ваш новый игровой id:")
                bot.send_message(base[0][0], str(x))
    else:
        bot.send_message(message.chat.id, "У вас нет убийцы")
    base = data_base.get_data("Users", "position", id=message.chat.id)
    number = base[0][0]
    number = pop_stack(number)
    number = add_stack(number, 14)
    data_base.update_record('users', 1, id=message.chat.id, position=number)


# Функции, отвечающие за вход в группу
def create(message):
    """Создание новой группы"""
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
    """Установление пароля"""
    data_base.update_record('groups', 1, administrator_id=message.chat.id,
                            password="\'" + message.text + "\'")
    bot.send_message(message.chat.id, "Подтвердите пароль:")
    data_base.update_record("Users", 1, id=message.chat.id, position=13)


def confirm_password(message):
    """Подтверждение пароля"""
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
    data_base.update_record("Users", 1, id=message.chat.id, position=14)
    generate_id(message.chat.id)


def login(message):
    """Вход в группу: ввод имени"""
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
    """Вход в группу: ввод пароля"""
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
    generate_id(message.chat.id)
    bot.send_message(message.chat.id, "Вы вошли в группу")
    bot.send_message(message.chat.id, "Если хотите выйти из неё,"
                                      " введите /exit,")


@bot.message_handler(commands=["start"])
def start(message):
    """Внос пользователя в бд"""
    base = data_base.get_data("Users", "id", "position", id=message.chat.id)
    num = -1 if base == -1 else 0
    try:
        if num == -1:
            raise Exception
        if base[num][1] == 0 or base[num][1] == 1:
            raise Exception
        else:
            bot.send_message(message.chat.id, "Ты уже начал игру")
    except Exception:
        if num == -1:
            print("Success!")
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


# Функции, отвечающие за подготовку к выполнению команд
@bot.message_handler(commands=["update"])
def pre_update(message):
    """Подтверждение апдейта"""
    base = data_base.get_data("Users", "position",
                              id=message.chat.id)
    num = -1 if base == -1 else 0
    if num == -1:
        return
    number = base[num][0]
    if get_stack(number) != 9 and get_stack(number) != 14:
        return
    i = add_stack(number, 21)
    data_base.update_record('users', 1, id=message.chat.id,
                            position=i)
    confirmation(message, "update_yes", "update_no")


@bot.message_handler(commands=["create"])
def pre_create(message):
    """Начало создания комнаты"""
    base = data_base.get_data("Users", "position",
                              id=message.chat.id)
    num = -1 if base == -1 else 0
    if num == -1:
        return
    number = get_stack(base[num][0])
    if number != 9:
        return
    bot.send_message(message.chat.id, "Введите название новой группы:")
    data_base.update_record('users', 1, id=message.chat.id, position=11)


@bot.message_handler(commands=["exit"])
def pre_exit(message):
    """Выход из группы"""
    base = data_base.get_data("Users", "position",
                              id=message.chat.id)
    num = -1 if base == -1 else 0
    if num == -1:
        return
    number = base[num][0]
    if get_stack(number) != 14:
        return
    i = add_stack(number, 22)
    data_base.update_record('users', 1, id=message.chat.id,
                            position=i)
    confirmation(message, "exit_yes", "exit_no")


@bot.message_handler(commands=["delete"])
def pre_delete(message):
    """Подготовка к удалению"""
    base = data_base.get_data("Users", "position",
                              id=message.chat.id)
    num = -1 if base == -1 else 0
    if num == -1:
        return
    number = base[num][0]
    i = add_stack(number, 23)
    data_base.update_record('users', 1, id=message.chat.id,
                            position=i)
    confirmation(message, "delete_yes", "delete_no")


@bot.message_handler(commands=["finish"])
def pre_finish(message):
    """Начинает игру"""
    x = data_base.get_data('groups', 'name', administrator_id=message.chat.id)
    if x == -1:
        bot.send_message(message.chat.id, "Это может сделать только"
                                          " администратор группы")
        return
    base = data_base.get_data("Users", "position",
                              id=message.chat.id)
    num = -1 if base == -1 else 0
    if num == -1:
        return
    number = base[num][0]
    i = add_stack(number, 24)
    data_base.update_record('users', 1, id=message.chat.id,
                            position=i)
    confirmation(message, "finish_yes", "finish_no")


@bot.message_handler(commands=["killed"])
def pre_kill(message):
    """Признание смерти"""
    base = data_base.get_data("Users", "id", aim=message.chat.id)
    if base == -1:
        return
    bot.send_message(message.chat.id, "Введите код убийцы:")
    base = data_base.get_data("Users", "position", id=message.chat.id)
    if base == -1:
        return
    number = base[0][0]
    number = pop_stack(number)
    number = add_stack(number, 25)
    data_base.update_record('users', 1, id=message.chat.id, position=number)

# Командные функции
@bot.message_handler(commands=["stop"])
def stop(message):
    """Остановливает процессы"""
    base = data_base.get_data("Users", "position",
                              id=message.chat.id)
    num = -1 if base == -1 else 0
    if num == -1:
        return
    a = base[num][0]
    number = get_stack(a)
    a = pop_stack(a)
    if a == 0:
        if number == 9 or number == 14:  # стабильные состояния
            return
        if number > 14:
            if stable(message):
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
            if full_record(message):
                if stable(message):
                    a = 14
                else:
                    a = 9
            else:
                a = 0
    data_base.update_record('users', 1, id=message.chat.id, position=a)
    bot.send_message(message.chat.id, "Действие приостановлено")
    data_base.update_record('users', 1, id=message.chat.id, position=a)


# Вызов функций
@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    base = data_base.get_data("Users", "id", "position",
                              id=message.chat.id)
    num = -1 if base == -1 else 0
    if num == -1:
        return
    number = base[num][1]
    number = get_stack(number)
    try:
        func = {2: surname, 3: choosing_direction, 7: room, 8: enter_in_game,
                9: login, 10: login_password, 11: create, 12: password,
                13: confirm_password, 25: killed}
        func[number](message)  # вызов функции
    except Exception as e:
        print(e)
        pass


@bot.callback_query_handler(func=lambda call: True)
def input_keyboard(call):
    base = data_base.get_data("Users", "position",
                              id=call.message.chat.id)
    num = -1 if base == -1 else 0
    if num == -1:
        return
    number = base[num][0]
    number = get_stack(number)
    try:
        func = {1: agreement, 4: direction, 5: physical_culture, 6: corp,
                20: change_admin, 21: update, 22: tel_exit, 23: tel_delete,
                24: finish}
        func[number](call)  # вызов функции
    except Exception as e:
        print(e)
        pass
