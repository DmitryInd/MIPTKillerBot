"""
Для работы с базой данных
"""
import sqlite3
import os

def_tables = ['users', 'faculty', 'sections', 'groups']
def_columns = {'users': ['id', 'first_name', 'last_name', 'faculty',
                         'direction', 'section', 'corpus', 'room', 'game_id',
                         'play_id', 'aim', 'position'],
               'faculty': ['name', 'direction'],
               'sections': ['section_id', 'section_nm'],
               'groups': ['name', 'password', 'administrator_id', 'work']}
def_create = {'users': '''
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY,
                        first_name VARCHAR(255),
                        last_name VARCHAR(255),
                        faculty VARCHAR(511),
                        direction VARCHAR(511),
                        section VARCHAR(511),
                        corpus INTEGER,
                        room INTEGER,
                        game_id VARCHAR(511),
                        play_id INTEGER DEFAULT 0,
                        aim INTEGER DEFAULT 0,
                        position INTEGER
                    )''',
              'faculty': '''
                    CREATE TABLE faculty (
                        name VARCHAR(255),
                        direction VARCHAR(255),
                        PRIMARY KEY (name, direction)
                    );
                    INSERT INTO faculty (name, direction) VALUES (
                    'Физтех-школа радиотехники и компьютерных технологий',
                     'Факультет радиотехники и кибернетики');
                     INSERT INTO faculty (name, direction) VALUES (
                    'Физтех-школа физики и исследований им. Ландау',
                     'Факультет общей и прикладной физики');
                     INSERT INTO faculty (name, direction) VALUES (
                    'Физтех-школа физики и исследований им. Ландау',
                     'Факультет проблем физики и энергетики');
                     INSERT INTO faculty (name, direction) VALUES (
                    'Физтех-школа аэрокосмических технологий',
                     'Факультет аэрофизики и космических исследований');
                     INSERT INTO faculty (name, direction) VALUES (
                    'Физтех-школа аэрокосмических технологий',
                     'Факультет аэромеханики и летательной техники');
                     INSERT INTO faculty (name, direction) VALUES (
                    'Физтех-школа электроники, фотоники и молекулярной физики',
                     'Факультет молекулярной и химической физики');
                     INSERT INTO faculty (name, direction) VALUES (
                    'Физтех-школа электроники, фотоники и молекулярной физики',
                     'Факультет физической и квантовой электроники');
                     INSERT INTO faculty (name, direction) VALUES (
                    'Физтех-школа прикладной математики и информатики',
                     'Факультет управления и прикладной математики');
                     INSERT INTO faculty (name, direction) VALUES (
                    'Физтех-школа прикладной математики и информатики',
                     'Факультет инноваций и высоких технологий');
                     INSERT INTO faculty (name, direction) VALUES (
                    'Физтех-школа биологической и медицинской физики',
                     'Факультет биологической и медицинской физики')''',
              'sections': '''CREATE TABLE sections (
                        section_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        section_nm VARCHAR(255)
                        );
                        INSERT INTO sections (section_nm)
                         VALUES ('Волейбол');
                        INSERT INTO sections (section_nm)
                         VALUES ('Баскетбол');
                        INSERT INTO sections (section_nm)
                         VALUES ('Футбол');
                        INSERT INTO sections (section_nm)
                         VALUES ('СМГ');''',
              'groups': '''CREATE TABLE groups (
                        name VARCHAR(511) UNIQUE,
                        password VARCHAR(255),
                        administrator_id INTEGER,
                        work VARCHAR(1)
                        );'''}


def def_check(table_name):
    """Проверяет корректность таблицы"""
    path = os.path.join("Info", 'killers_base.db')
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    try:
        cur.execute('''SELECT count(*) FROM sqlite_master WHERE type='table'
         AND name={}'''.format("\'" + table_name + "\'"))
        if cur.__next__() == (0, ):
            raise Exception
        cur.execute('''pragma table_info ({})'''.format(table_name))
        columns = [a[1] for a in cur]
        if columns != def_columns[table_name]:
            raise Exception
    except Exception as e:
        cur.execute('''DROP TABLE IF EXISTS {}'''.format(table_name))
        conn.commit()
        request = def_create[table_name].split(";")
        for i in request:
            cur.execute(i)
        conn.commit()
    conn.commit()
    conn.close()


def def_base():
    """Проверяет корректность базы данных"""
    for i in def_tables:
        def_check(i)


def joke(request):
    """Выявляет шутников"""
    request = request.split("")
    for i in range(0, len(request)):
        if request[i] == ';' or request[i] == '"' or request[i] == '\'':
            request.insert(i, "\\")
            i += 1

    request = "".join(request)


def get_data(table, *args, **kwargs):
    """Для получения списков с данными из базы данных"""
    path = os.path.join("Info", 'killers_base.db')
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    request = '''SELECT {} FROM {} {}'''
    column = []
    for i in args:
        column.append(i)
    column = ", ".join(column)
    condition = "WHERE "
    for i in kwargs.items():
        condition += i[0] + " = " + str(i[1]) + " and "
    if condition == "WHERE ":
        condition = ""
    else:
        condition = condition[: -5]
    try:
        cur.execute(request.format(column, table, condition))
    except Exception as e:
        print(e)
        conn.close()
        return -1

    ans = []
    for i in cur:
        ans.append(i)

    conn.close()
    if len(ans) == 0:
        ans = -1
    return ans


def create_record(table_name, **kwargs):
    """Создаёт пустую запись в таблице"""
    path = os.path.join("Info", 'killers_base.db')
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute('''pragma table_info ({})'''.format(table_name))
    values = {a[1]: a[2] for a in cur}
    columns = []
    value = []
    for i in kwargs.items():
        try:
            k = values[i[0]]
            value.append(str(i[1]))
            columns.append(str(i[0]))
        except Exception:
            pass
    value = ", ".join(value)
    columns = ", ".join(columns)
    request = '''INSERT INTO {} ({}) VALUES ({})'''.format(table_name, columns
                                                           , value)
    cur.execute(request)
    conn.commit()
    conn.close()


def update_record(table_name, num, **kwargs):
    """Обновляет запись"""

    path = os.path.join("Info", 'killers_base.db')
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    primary_key = ""
    p = kwargs.items().__iter__()
    for i in range(num):
        obj = p.__next__()
        primary_key += str(obj[0]) + " = "
        primary_key += str(obj[1]) + " and "

    primary_key = primary_key[: -5]

    for i in p:
        cur.execute('''UPDATE {} SET {} = {}
        WHERE {}'''.format(table_name, i[0], i[1], primary_key))
    conn.commit()
    conn.close()


def delete_record(table, **kwargs):
    """Удаление записи из таблицы"""
    path = os.path.join("Info", 'killers_base.db')
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    request = '''DELETE FROM {} {}'''
    condition = "WHERE "
    for i in kwargs.items():
        condition += i[0] + " = " + str(i[1]) + " and "
    if condition == "WHERE ":
        condition = ""
    else:
        condition = condition[: -5]
    conn.execute(request.format(table, condition))
    conn.commit()
    conn.close()
