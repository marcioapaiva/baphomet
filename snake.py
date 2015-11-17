from drawille.graphics_utils import get_pos, CH_HEIGHT, CH_WIDTH, frange
from arena import *

__author__ = 'ericmuxagata'

BASE_SIZE = 5

DIR_W = 0
DIR_S = 1
DIR_E = 2
DIR_N = 3

class SnakeNode(object):
    def __init__(self,x,y,c,dir, next=None,prev=None):
        self.x, self.y = x,y
        self.color, self.dir = c, dir
        self.prev = prev
        self.next = next
        self.dir = dir
        self.is_head = False

    def add_pos(self,x,y):
        self.x += x
        self.y += y

    def follow_next(self):
        if not self.next:
            return
        self.x, self.y, self.dir = self.next.x, self.next.y, self.next.dir
        self.next.follow_next()

    def frame(self):
        frame = []
        for x in frange(self.x*CH_WIDTH, (self.x+1)*CH_WIDTH, 1.0):
            for y in frange(self.y*CH_HEIGHT, (self.y+1)*CH_HEIGHT, 1.0):
                frame.append((x, y, self.color))
        return frame


class Snake(object):
    def __init__(self, x, y, c, dir):
        x,y = get_pos(x,y)
        self.points, self.max_points = 0,0
        self.color = c
        self.dir = dir
        self.nodes = [SnakeNode(x-i, y, c, dir) for i in xrange(BASE_SIZE)]
        self.head = self.nodes[0]
        self.head.is_head = True
        self.tail = self.nodes[-1]
        for i in xrange(len(self.nodes)):
            self.nodes[i].prev = self.nodes[i+1] if i+1 < len(self.nodes) else None
            self.nodes[i].next = self.nodes[i-1] if i-1 >= 0 else None

    def __update__(self):
        if self.head.dir == DIR_S:
            move = (0, 1)
        elif self.head.dir == DIR_N:
            move = (0, -1)
        elif self.head.dir == DIR_W:
            move = (-1, 0)
        else:
            move = (1, 0)

        # check move.
        dx, dy = move
        if arena.is_out_of_bounds(self.head.x + dx, self.head.y + dy):
            self.kill_reset()
            return
        if arena.has_hit_snake(self.head.x, self.head.y, self.head):
            self.kill_reset()
            return
        if arena.find_and_eat_seed(self.head.x + dx, self.head.y + dy):
            self.points += 10
            self.max_points = max(self.max_points, self.points)
            self.expand()

        # update if necessary.
        self.tail.follow_next()
        self.head.add_pos(*move)

    def expand(self):
        if self.tail.dir == DIR_S:
            ds = (0, -1)
        elif self.tail.dir == DIR_N:
            ds = (0, 1)
        elif self.tail.dir == DIR_W:
            ds = (1, 0)
        else:
            ds = (-1, 0)
        new_tail = SnakeNode(self.tail.x + ds[0], self.tail.y + ds[1], self.color, self.tail.dir)
        new_tail.next = self.tail
        new_tail.prev = None
        self.nodes.append(new_tail)

        self.tail.prev = new_tail
        self.tail = new_tail

    def kill_reset(self):
        x,y = arena.generate_random_pos()
        self.points = 0
        self.nodes = [SnakeNode(x-i, y, self.color, self.dir) for i in xrange(BASE_SIZE)]
        self.head = self.nodes[0]
        self.head.is_head = True
        self.tail = self.nodes[-1]
        for i in xrange(len(self.nodes)):
            self.nodes[i].prev = self.nodes[i+1] if i+1 < len(self.nodes) else None
            self.nodes[i].next = self.nodes[i-1] if i-1 >= 0 else None

    def frame(self):
        frame = []
        for node in self.nodes:
            frame.extend(node.frame())
        return frame

