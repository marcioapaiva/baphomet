import random
from datetime import datetime
from drawille.graphics_utils import get_terminal_size_in_pixels, COLOR_MAGENTA, CH_HEIGHT, CH_WIDTH, frange, get_pos
from image2term import image2term


__author__ = 'ericmuxagata'

NUM_SEEDS = 4


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

        # Generate seeds.
        random.seed(datetime.now())
        self.seeds = self.generate_seeds(NUM_SEEDS)
        self.reset_seeds_frame()

    def reset_seeds_frame(self):
        self.seeds_frame = []
        for (sx,sy,c) in self.seeds:
            frame = []
            for x in frange(sx*CH_WIDTH, (sx+1)*CH_WIDTH, 1.0):
                for y in frange(sy*CH_HEIGHT, (sy+1)*CH_HEIGHT, 1.0):
                    frame.append((x, y, c))
            self.seeds_frame.extend(frame)

    def generate_seeds(self,n):
        xl, xh, yl, yh = self.x + 15, self.x + self.w - 15, self.y + 15, self.y + self.h - 15
        seeds = []
        for i in xrange(n):
            x,y = get_pos(random.randint(xl,xh), random.randint(yl,yh))
            seeds.append((x,y,COLOR_MAGENTA))
        return seeds

    def set_pos(self,xd,yd):
        self.x, self.y = xd, yd
        self.frame = [(x + self.x, y + self.y, c) for (x,y,c) in self.frame]

    def is_out_of_bounds(self, x, y):
        return (x < self.x) or (x > self.x + self.w) or (y < self.y) or (y > self.y + self.h)

    def find_and_eat_seed(self, x, y):
        seed = None
        for s in self.seeds:
            sx,sy = s[0], s[1]
            if sx == x and sy == y:
                seed = s
                break
        # Fail and quit.
        if not seed:
            return False
        # Add new seed and return success.
        self.seeds.remove(seed)
        self.seeds.extend(self.generate_seeds(1))
        self.reset_seeds_frame()
        return True




arena = Arena(130,'img/arena.png')