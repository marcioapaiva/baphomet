
from __future__ import print_function
from drawille.drawille import Canvas, Palette, animate, COLOR_CYAN, COLOR_GREEN, COLOR_RED, COLOR_YELLOW, getTerminalSizeInPixels
from math import sin, radians
from random import randint
from image2term import image2term

c = Canvas()
p = Palette()
t = 0

r,g,b = [randint(0,1000) for i in xrange(3)]


DIR_W = 0
DIR_S = 1
DIR_E = 2
DIR_N = 3
JOINT_HEIGHT = 5
JOINT_WIDTH  = 10


class SnakeNode(object):
    def __init__(self,x,y,c,dir,prev=None):
        self.x, self.y, self.color, self.dir = x, y, c, dir
        self.prev = prev
    def add_pos(self, x,y):
        self.x += x
        self.y += y
    def change_dir(self,dir):
        self.dir = dir

    def frame(self):
        frame = []
        for x in xrange(self.x - JOINT_WIDTH/2,self.x + JOINT_WIDTH/2):
            for y in xrange(self.y - JOINT_HEIGHT/2, self.y + JOINT_HEIGHT/2):
                frame.append((x,y,self.color))
        return frame


BASE_SIZE = 5
SPEED = 10


class Snake(object):
    def __init__(self,x,y,c,dir):
        self.color = c
        self.head = SnakeNode(x,y,c,dir)
    def __update__(self):
        if self.head.dir == DIR_S:
            self.head.add_pos(0,SPEED)
        elif self.head.dir == DIR_N:
            self.head.add_pos(0,-SPEED)
        elif self.head.dir == DIR_W:
            self.head.add_pos(-SPEED,0)
        else:
            self.head.add_pos(SPEED,0)

    def frame(self):
        return self.head.frame()


def set_pos(frame,xd,yd):
    return [(x+xd,y+yd,c) for (x,y,c) in frame]


def load_arena():
    arena = []
    baphomet_head = image2term('img/baphomet_head.gif', ratio=0.48, invert=True)
    tw,th = getTerminalSizeInPixels()

    arena.extend(set_pos(baphomet_head,tw/2 - 105,th/2 - 105))
    arena.extend(image2term('img/arena.png',ratio=0.999))

    return arena



def __update__():
    t = 0
    snake1 = Snake(100,150,COLOR_YELLOW,DIR_E)
    snake2 = Snake(200,150,COLOR_RED,DIR_E)
    snake3 = Snake(100,200,COLOR_GREEN,DIR_E)
    snake4 = Snake(200,200,COLOR_CYAN,DIR_E)
    snakes = [snake1, snake2, snake3, snake4]


    while True:
        frame = []
        frame.extend(load_arena())
        for snake in snakes:
            frame.extend(snake.frame())

        # frame = [(x+100,y+20,c) for (x,y,c) in frame]

        # frame = []
        # for x in range(0,600,5):
        #     frame.extend([(x/5,50+50*sin(radians(x-t))+i, COLOR_RED) for i in range(0,8)])
        # for x in range(600,1200,5):
        #     frame.extend([(x/5,50+50*sin(radians(x-t))+i, COLOR_CYAN) for i in range(0,8)])
        # for x in range(1200,1800,5):
        #     frame.extend([(x/5,50+50*sin(radians(x-t))+i, COLOR_BLUE) for i in range(0,8)])

        #TODO: Aqui faz a arena do snake.

        yield frame
        t += 1
        for snake in snakes:
            snake.__update__()
            if t % 10 == 0:
                snake.head.dir += 1
                if snake.head.dir == 4:
                    snake.head.dir = 0


if __name__ == '__main__':
    p.add_color(COLOR_CYAN)
    animate(c,p, __update__, 1./60)

