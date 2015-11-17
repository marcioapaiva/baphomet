from image2term import image2term

__author__ = 'ericmuxagata'


class Arena(object):
    def __init__(self,height,path):
        self.w, self.h, self.frame = image2term(path,height=height)
        self.x = self.y = 0

    def set_pos(self,xd,yd):
        self.x, self.y = xd, yd
        self.frame = [(x + self.x, y + self.y, c) for (x,y,c) in self.frame]