"""Functions for the all life cases"""
# -*- coding: utf-8 -*-
import random
from app import data_base
import copy
from app import graph


def sort_by_first(a):
    """Key for sorting"""
    return a[0]


def add_stack(a, command):
    """Adding command in stack"""
    number = copy.copy(a)
    i = 100
    while i < number:
        i *= 100
    command = i * command
    return number + command


def pop_stack(a):
    """Vanishing command from stack"""
    number = copy.copy(a)
    i = 100
    while i < number:
        i *= 100
    i /= 100
    number = number % i
    return number


def get_stack(a):
    """Return last command"""
    number = copy.copy(a)
    while number > 100:
        number = int(number/100)
    return number


def generate_id(pl_id):
    """Generate for participant of group unique code"""
    group = data_base.get_data('users', 'game_id', id=pl_id)[0][0]
    group = data_base.get_data('users', 'play_id', game_id="'" + group + "'")
    group = [i[0] for i in group] if group != -1 else []
    p_id = random.randint(1, 1000000)
    while graph.search(group, p_id) != -1:
        p_id = random.randint(1, 1000000)
    data_base.update_record('users', 1, id=pl_id, play_id=p_id)


def stable(message):
    """Check on presence in any group"""
    group = data_base.get_data('users', 'game_id', id=message.chat.id)[0][0]
    if group is None:
        return False
    return True


def full_record(message):
    """Check record on wholeness"""
    group = data_base.get_data('users', 'first_name', 'last_name', 'faculty',
                               'direction', 'section', 'corpus', 'room'
                               , id=message.chat.id)[0]
    for i in group:
        if i is None:
            return False

    return True
