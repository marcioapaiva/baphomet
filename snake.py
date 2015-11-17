__author__ = 'ericmuxagata'

BASE_SIZE = 5

DIR_W = 0
DIR_S = 1
DIR_E = 2
DIR_N = 3
CH_HEIGHT = 4.0
CH_WIDTH  = 2.0

def frange(x, y, jump):
  while x < y:
    yield x
    x += jump


class SnakeNode(object):
    def __init__(self,x,y,c,dir, next=None,prev=None):
        self.x, self.y = get_pos(x,y)
        self.color, self.dir = c, dir
        self.prev = prev
        self.next = next
        self.dir = dir

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
    def __init__(self,x,y,c,dir):
        self.color = c
        self.nodes = [SnakeNode(x-i*CH_WIDTH,y,c,dir) for i in xrange(BASE_SIZE)]
        self.head = self.nodes[0]
        self.tail = self.nodes[-1]
        for i in xrange(len(self.nodes)):
            self.nodes[i].prev = self.nodes[i+1] if i+1 < len(self.nodes) else None
            self.nodes[i].next = self.nodes[i-1] if i-1 >= 0 else None
    def __update__(self):
        self.tail.follow_next()
        if self.head.dir == DIR_S:
            self.head.add_pos(0,1)
        elif self.head.dir == DIR_N:
            self.head.add_pos(0,-1)
        elif self.head.dir == DIR_W:
            self.head.add_pos(-1,0)
        else:
            self.head.add_pos(1,0)

    def frame(self):
        frame = []
        for node in self.nodes:
            frame.extend(node.frame())
        return frame

