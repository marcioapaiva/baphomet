from drawille.graphics_utils import get_terminal_size_in_pixels
from image2term import image2term


__author__ = 'ericmuxagata'


def set_pos(frame,xd,yd):
    return [(x+xd,y+yd,c) for (x,y,c) in frame]


class Arena(object):
    def __init__(self,height,path):
        self.w, self.h, self.frame = image2term(path,height=height)
        self.x = self.y = 0

        tw, th = get_terminal_size_in_pixels()
        self.set_pos(tw/2 - self.w/2,th/2 - self.h/2)

        bapho_head = image2term('img/baphomet_head.gif', height=0.8*self.h, invert=True)
        self.frame.extend(set_pos(bapho_head[2],self.x + self.w/2 - bapho_head[0]/2,self.y + self.h/2 - bapho_head[1]/2))

    def set_pos(self,xd,yd):
        self.x, self.y = xd, yd
        self.frame = [(x + self.x, y + self.y, c) for (x,y,c) in self.frame]

    def is_out_of_bounds(self, x, y):
        return (x < self.x) or (x > self.x + self.w) or (y < self.y) or (y > self.y + self.h)

arena = Arena(130,'img/arena.png')