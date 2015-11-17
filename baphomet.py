from __future__ import print_function
from drawille.graphics_utils import COLOR_CYAN, COLOR_GREEN, COLOR_RED, COLOR_YELLOW
from drawille.graphics_utils import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
from drawille.drawille import Canvas, Palette, animate, handle_input
from snake import DIR_N,DIR_S,DIR_E,DIR_W,Snake
from arena import *

c = Canvas()
p = Palette()
t = 0

def __update__():
    t = 0
    snake1 = Snake(100, 150, COLOR_YELLOW, DIR_E)
    snake2 = Snake(200, 150, COLOR_RED, DIR_E)
    snake3 = Snake(100, 130, COLOR_GREEN, DIR_E)
    snake4 = Snake(200, 130, COLOR_CYAN, DIR_E)
    snakes = [snake1, snake2, snake3, snake4]

    while True:
        key = handle_input()
        if key == KEY_UP:
            snake1.head.dir = DIR_N
        elif key == KEY_DOWN:
            snake1.head.dir = DIR_S
        elif key == KEY_LEFT:
            snake1.head.dir = DIR_W
        elif key == KEY_RIGHT:
            snake1.head.dir = DIR_E

        frame = []
        frame.extend(arena.frame)
        frame.extend(arena.seeds_frame)
        for snake in snakes:
            frame.extend(snake.frame())

        yield frame
        t += 1
        for snake in snakes:
            snake.__update__()
            if t % 10 == 0 and snake is not snake1:
                snake.head.dir += 1
                if snake.head.dir == 4:
                    snake.head.dir = 0


if __name__ == '__main__':
    p.add_color(COLOR_CYAN)
    p.add_color(COLOR_MAGENTA)
    animate(c, p, __update__, 1./60)


