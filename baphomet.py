from __future__ import print_function
from drawille.graphics_utils import COLOR_CYAN, COLOR_GREEN, COLOR_RED, COLOR_YELLOW
from drawille.graphics_utils import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
from drawille.drawille import Canvas, Palette, animate, handle_input
from snake import DIR_N,DIR_S,DIR_E,DIR_W,Snake
from arena import *
import socket
import sys
import json

import time
# Global state
# 'Cause I don't know python and it's too fucking late
total = 0
my_number = 0
c = Canvas()
p = Palette()
t = 0
is_server = False
server_ip = None
server_port = None
m_socket = None
dir_dict = {
    "DIR_N": DIR_N,
    "DIR_S": DIR_S,
    "DIR_W": DIR_W,
    "DIR_E": DIR_E,
    "None": None
}
key_dir_dict = {
    KEY_UP: DIR_N,
    KEY_DOWN: DIR_S,
    KEY_LEFT: DIR_W,
    KEY_RIGHT: DIR_E
}
dir_dict_inv = {v: k for k, v in dir_dict.items()}
sockets_dict = {
}
snake1 = Snake(100, 90, COLOR_YELLOW, DIR_E)
snake2 = Snake(140, 90, COLOR_RED, DIR_E)
snake3 = Snake(100, 78, COLOR_GREEN, DIR_E)
snake4 = Snake(140, 78, COLOR_CYAN, DIR_E)
snakes = [snake1, snake2, snake3, snake4]

# Client state
client_number = None

GAME_TIME = 30.0
FRAME_PERIOD = 1./30

c = Canvas()
p = Palette()
t = GAME_TIME


def __update__():
    global t
    k = 0
    arena.add_snakes(snakes)

    while t >= 0:
        start = time.time()

        key = handle_input()
        this_direction = key_dir_dict.get(key, None)

        snakes[0].move(this_direction)

        if is_server:
            for player in sockets_dict.keys():
                direction = receive_dir(sockets_dict[player])
                snakes[player].move(direction)
            send_dirs_all_players()
        else:
            send_dir(this_direction)
            dirs = receive_dirs(m_socket)
            for player in dirs.keys():
                snakes[int(player)].move(dirs[player])

        frame = []
        frame.extend(arena.frame)
        frame.extend(arena.seeds_frame)
        frame.extend(arena.snakes_frame())
        frame.extend(arena.show_scores_frame())
        frame.extend(arena.show_timer_frame(t))

        yield frame
        k += 1
        t -= time.time() - start
        for snake in snakes:
            snake.__update__()
            if k % 10 == 0 and snake is not snake1 and snake is not snake2:
                snake.head.dir += 1
                if snake.head.dir == 4:
                    snake.head.dir = 0

    #Endgame screen.
    frame = []

    frame.extend(arena.show_victory_frame())

    frame.extend(arena.snakes_frame())
    frame.extend(arena.show_scores_frame())
    frame.extend(arena.frame)

    while True:
        yield frame


def init_server_socket():
    global m_socket

    m_socket = socket.socket()
    host = ''
    port = 8087
    m_socket.bind((host, port))

    m_socket.listen(4)


def receive_dir(sckt):
    data = get_line(sckt).next()
    string = data.rstrip("\n")

    return dir_dict[string]


def receive_dirs(sckt):
    data = get_line(sckt).next()
    data = data.rstrip("\n")
    dirs = json.loads(data)

    return dirs


def send_dir(direction):
    m_socket.sendall(dir_dict_inv[direction] + "\n")


def send_dirs_all_players():
    for player in sockets_dict.keys():
        sckt = sockets_dict[player]
        send_dirs(sckt)


def send_dirs(sckt):
    dirs = {}
    for player in range(len(snakes)):
        dirs[player] = snakes[player].head.dir

    sckt.send(json.dumps(dirs) + "\n")


def init_client_socket():
    global m_socket
    m_socket = socket.socket()
    m_socket.connect((server_ip, server_port))

    # Wait for start


def main(argv):
    global is_server, server_ip, server_port, snakes, total, my_number

    if len(argv) == 0:
        is_server = True
    else:
        is_server = False

    if is_server:
        init_server_socket()
        total = 1
        while total <= 3 and prompt_wait_for_player():
            wait_for_player(total)
            total += 1
        send_start_game()
    else:
        server_ip = argv[0]
        server_port = int(argv[1])
        init_client_socket()
        print("Waiting for game start...")
        my_number_total = get_line(m_socket).next()
        my_number_total = json.loads(my_number_total)
        my_number = my_number_total["my_number"]
        total = my_number_total["total"]

    snakes = snakes[0:total]

    p.add_color(COLOR_CYAN)
    p.add_color(COLOR_MAGENTA)
    animate(c, p, __update__, FRAME_PERIOD)


def wait_for_player(number):
    print("Waiting for player " + str(number+1))
    conn, addr = m_socket.accept()
    print(addr[0] + " connected as player " + str(number+1))
    sockets_dict[number] = conn


def prompt_wait_for_player():
    str_wait = raw_input("Wait for another player? [y/n] ")
    if str_wait.upper() == "Y":
        return True
    return False


def get_line(sckt):
    sckt_buffer = sckt.recv(4096)
    buffering = True
    while buffering:
        if "\n" in sckt_buffer:
            (line, sckt_buffer) = sckt_buffer.split("\n", 1)
            yield line + "\n"
        else:
            more = sckt.recv(4096)
            if not more:
                buffering = False
            else:
                sckt_buffer += more
    if sckt_buffer:
        yield sckt_buffer


def send_start_game():
    for player in sockets_dict.keys():
        sockets_dict[player].send(
            json.dumps({"total": len(sockets_dict.keys())+1, "my_number": player}) + "\n")

if __name__ == '__main__':
    main(sys.argv[1:])
