from drawille.drawille import get_terminal_size_in_pixels


__author__ = 'ericmuxagata'

BASE_SIZE = 5

DIR_W = 0
DIR_S = 1
DIR_E = 2
DIR_N = 3
JOINT_HEIGHT = 3.0
JOINT_WIDTH  = 6.0

EDGE_X = 12.0
EDGE_Y = 7.0

tw,th = get_terminal_size_in_pixels()

def frange(x, y, jump):
  while x < y:
    yield x
    x += jump


class SnakeNode(object):
    def __init__(self,x,y,c,dir,speed=JOINT_WIDTH, next=None,prev=None):
        self.x, self.y, self.color, self.dir = x, y, c, dir
        self.prev = prev
        self.next = next
        self.dir = dir
        self.speed = speed

    def add_pos(self, x,y):
        self.x += x
        self.y += y
        self.x = max(EDGE_X + JOINT_WIDTH/2,min(self.x, tw - EDGE_X - JOINT_WIDTH/2))
        self.y = max(EDGE_Y + JOINT_WIDTH/2,min(self.y, th - EDGE_Y - JOINT_WIDTH))

    def follow_next(self):
        if not self.next:
            return
        self.x, self.y, self.dir = self.next.x, self.next.y, self.next.dir
        self.next.follow_next()

    def frame(self):
        frame = []
        jw, jh = self.speed, JOINT_HEIGHT
        if self.dir == DIR_N or self.dir == DIR_S:
            jw, jh = jh, jw

        for x in frange(self.x - jw/2,self.x + jw/2,0.25):
            for y in frange(self.y - jh/2, self.y + jh/2,0.25):
                frame.append((x,y,self.color))
        return frame


class Snake(object):
    def __init__(self,x,y,c,dir):
        self.color = c
        self.speed = 2*JOINT_WIDTH
        self.nodes = [SnakeNode(x-i*self.speed,y,c,dir,self.speed) for i in xrange(BASE_SIZE)]
        self.head = self.nodes[0]
        self.tail = self.nodes[-1]
        for i in xrange(len(self.nodes)):
            self.nodes[i].prev = self.nodes[i+1] if i+1 < len(self.nodes) else None
            self.nodes[i].next = self.nodes[i-1] if i-1 >= 0 else None
    def __update__(self):
        self.tail.follow_next()
        if self.head.dir == DIR_S:
            self.head.add_pos(0,self.speed)
        elif self.head.dir == DIR_N:
            self.head.add_pos(0,-self.speed)
        elif self.head.dir == DIR_W:
            self.head.add_pos(-self.speed,0)
        else:
            self.head.add_pos(self.speed,0)

    def frame(self):
        frame = []
        for node in self.nodes:
            frame.extend(node.frame())
        return frame

