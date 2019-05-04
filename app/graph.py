"""
There is ListGraph
"""

import copy
import queue
import sys


def search(arr, element):
    """Поиск элемента в массиве"""
    for k in range(len(arr)):
        if arr[k] == element:
            return k

    return -1


class ListGraph:
    """Using for saving users"""

    def __init__(self, n):
        """Constructor"""
        self.size = n
        self.matrix = [[] for i in range(n)]

    def add_connection(self, u, v, value):
        """Add edge"""
        if u >= len(self.matrix) or u < 0:
            raise IOError('\"from\" is out of range')
        if v >= len(self.matrix) or v < 0:
            raise IOError('\"to\" is out of range')
        v_from = copy.copy(u)
        v_to = copy.copy(v)
        v_value = copy.copy(value)
        self.matrix[v_from].append([v_to, v_value])

    def get_next_vertices(self, u):
        """Getting next vertices"""
        return self.matrix[u]

    def get_value(self, u, v):
        """Return value of edge"""
        transfer = self.matrix[u]
        for i in transfer:
            if i[0] == v:
                return i[1]
        return -1

    def max_road(self):
        """Find max cycle"""
        list_q = queue.PriorityQueue()
        list_q.put([sys.maxsize, [0, [0]]])
        while not list_q.empty():
            u = list_q.get()
            transfer = self.matrix[u[1][1][len(u[1][1]) - 1]]
            k = 0
            for i in transfer:
                if search(u[1][1], i[0]) != -1:
                    continue
                k += 1
                x = u[1][0] + i[1]
                u[1][1].append(i[0])
                list_q.put([1 / x, [x, u[1][1]]])
            if k == 0:
                if u[1][1][len(u[1][1]) - 1] == 0:
                    return u[1][1]
                x = u[1][0] + self.get_value(u[1][1][len(u[1][1]) - 1], 0)
                u[1][1].append(0)
                list_q.put([1/x, [x, u[1][1]]])
        return -1
