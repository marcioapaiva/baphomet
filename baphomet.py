from __future__ import print_function
import time
from drawille.graphics_utils import get_terminal_size_in_pixels, COLOR_CYAN, COLOR_GREEN, COLOR_RED, COLOR_YELLOW
from drawille.graphics_utils import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
from drawille.drawille import Canvas, Palette, animate, handle_input
from image2term import image2term
from snake import DIR_N,DIR_S,DIR_E,DIR_W,Snake
from arena import *
import socket
import sys
import json

# Global state
# 'Cause I don't know python and it's too fucking late
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
snakes = [Snake(100, 150, COLOR_YELLOW, DIR_E),
          Snake(200, 150, COLOR_RED, DIR_E),
          Snake(100, 200, COLOR_GREEN, DIR_E),
          Snake(200, 200, COLOR_CYAN, DIR_E)]

# Client state
client_number = None


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

    while True:
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
                snakes[int(player)].move(dirs[int(player)])

        frame = []
        frame.extend(arena.frame)
        for snake in snakes:
            frame.extend(snake.frame())

        yield frame
        t += 1
        for snake in snakes:
            snake.__update__()


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

    time.sleep(4)
    arq = open("/home/moco/bizu", "w")
    arq.write(json.dumps(dirs) + "\n")
    arq.close()
    sckt.send(json.dumps(dirs) + "\n")


def init_client_socket():
    global m_socket
    m_socket = socket.socket()
    m_socket.connect((server_ip, server_port))

    # Wait for start


def main(argv):
    global is_server, server_ip, server_port, snakes

    if len(argv) == 0:
        is_server = True
    else:
        is_server = False

    if is_server:
        init_server_socket()
        p_number = 1
        while p_number <= 3 and prompt_wait_for_player():
            wait_for_player(p_number)
            p_number += 1
        snakes = snakes[0:p_number]
        send_start_game()
    else:
        server_ip = argv[0]
        server_port = int(argv[1])
        init_client_socket()
        print("Waiting for game start...")
        my_number = get_line(m_socket).next()

    p.add_color(COLOR_CYAN)
    animate(c, p, __update__, 1./15)


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
        sockets_dict[player].send(str(player) + "\n")

if __name__ == '__main__':
    main(sys.argv[1:])
