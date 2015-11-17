
from __future__ import print_function
from drawille.graphics_utils import get_terminal_size_in_pixels, COLOR_CYAN, COLOR_GREEN, COLOR_RED, COLOR_YELLOW
from drawille.graphics_utils import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
from drawille.drawille import Canvas, Palette, animate, handle_input
from image2term import image2term
from snake import DIR_N,DIR_S,DIR_E,DIR_W,Snake
from arena import *
import socket
import sys

c = Canvas()
p = Palette()
t = 0
is_server = False
server_ip = None
server_port = None
m_socket = None


def set_pos(frame, xd, yd):
    return [(x+xd, y+yd, c) for (x, y, c) in frame]


def load_arena():
    global arena
    tw, th = get_terminal_size_in_pixels()

    if not arena:
        arena = Arena(150, 'img/arena.png')
        arena.set_pos(tw/2 - arena.w/2, th/2 - arena.h/2)

        bapho_head = image2term('img/baphomet_head.gif', height=0.8*arena.h, invert=True)
        arena.frame.extend(set_pos(bapho_head[2],arena.x + arena.w/2 - bapho_head[0]/2,arena.y + arena.h/2 - bapho_head[1]/2))

    return arena.frame


def __update__():
    t = 0
    snake1 = Snake(100, 150, COLOR_YELLOW, DIR_E)
    snake2 = Snake(200, 150, COLOR_RED, DIR_E)
    snake3 = Snake(100, 200, COLOR_GREEN, DIR_E)
    snake4 = Snake(200, 200, COLOR_CYAN, DIR_E)
    snakes = [snake1, snake2, snake3, snake4]

    while True:
        key = handle_input()
        direction = None
        if key == KEY_UP:
            direction = DIR_N
        elif key == KEY_DOWN:
            direction = DIR_S
        elif key == KEY_LEFT:
            direction = DIR_W
        elif key == KEY_RIGHT:
            direction = DIR_E

        snake1.move(direction)

        if is_server:
            dir2 = receive_dir()
            snake2.move(dir2)
        else:
            send_dir(direction)

        frame = []
        frame.extend(arena.frame)
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


conn = None
addr = None


def init_server_socket():
    global m_socket, conn, addr

    m_socket = socket.socket()
    host = ''
    port = 8080
    m_socket.bind((host, port))

    m_socket.listen(5)
    print("Waiting for connection...")
    conn, addr = m_socket.accept()


dir_dict = {
    "DIR_N": DIR_N,
    "DIR_S": DIR_S,
    "DIR_W": DIR_W,
    "DIR_E": DIR_E,
    "None": None
}
dir_dict_inv = {v: k for k, v in dir_dict.items()}


def receive_dir():
    data = conn.recv(1024)
    string = data.rstrip("\n")

    print("Received " + string)
    return dir_dict[string]


def send_dir(direction):
    m_socket.sendall(dir_dict_inv[direction])


def init_client_socket():
    global m_socket
    m_socket = socket.socket()
    m_socket.connect((server_ip, server_port))


def main(argv):
    global is_server, server_ip, server_port

    print(argv)

    if len(argv) == 0:
        is_server = True
        init_server_socket()
    else:
        is_server = False
        server_ip = argv[1]
        server_port = int(argv[2])
        init_client_socket()

    p.add_color(COLOR_CYAN)
    animate(c, p, __update__, 1./15)

if __name__ == '__main__':
    main(sys.argv[2:])