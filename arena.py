import random
from datetime import datetime
from drawille.graphics_utils import get_terminal_size_in_pixels, COLOR_MAGENTA, CH_HEIGHT, CH_WIDTH, frange, get_pos
from image2term import image2term


__author__ = 'ericmuxagata'

NUM_SEEDS = 4


def set_pos(frame,xd,yd):
    return [(x+xd,y+yd,c) for (x,y,c) in frame]

# Massive class containing most of the game logic.
class Arena(object):
    def __init__(self,height,path):
        self.w, self.h, self.frame = image2term(path,height=height)
        self.x = self.y = 0

        tw, th = get_terminal_size_in_pixels()
        self.set_pos(tw/2 - self.w/2,th/2 - self.h/2)

        bapho_head = image2term('img/baphomet_head.gif', height=0.8*self.h, invert=True)
        self.frame.extend(set_pos(bapho_head[2],self.x + self.w/2 - bapho_head[0]/2,self.y + self.h/2 - bapho_head[1]/2))

        bapho_title = image2term('img/baphomet_title.jpg', height=85,invert=True)
        self.frame.extend(set_pos(bapho_title[2],self.x + self.w/2 - bapho_title[0]/2,self.y - 25 - bapho_title[1]/2))

        # Generate seeds.
        random.seed(datetime.now())
        self.seeds = self.generate_seeds(NUM_SEEDS)
        self.reset_seeds_frame()

        # Snakes.
        self.snakes = None

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

    def generate_random_pos(self):
        xl, xh, yl, yh = self.x + 15, self.x + self.w - 15, self.y + 15, self.y + self.h - 15
        return get_pos(random.randint(xl,xh), random.randint(yl,yh))

    def set_pos(self,xd,yd):
        self.x, self.y = xd, yd
        self.frame = [(x + self.x, y + self.y, c) for (x,y,c) in self.frame]

    def add_snakes(self, snakes):
        self.snakes = snakes

    def snakes_frame(self):
        frame = []
        for snake in self.snakes:
            frame.extend(snake.frame())
        return frame

    def show_scores_frame(self):
        frame = []
        uix, uiy = self.x + 60, self.y + self.h + 20
        for snake in self.snakes:
            frame.append((uix, uiy, snake.color, "Score: %d" % snake.max_points))
            uix += 30
        return frame


    # Game logic.

    def is_out_of_bounds(self, x, y):
        x *= CH_WIDTH
        y *= CH_HEIGHT
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

    def has_hit_snake(self,x,y,target):
        for snake in self.snakes:
            for node in snake.nodes:
                if node.x == x and node.y == y and node != target:
                    return True
        return False
        




arena = Arena(130,'img/arena.png')