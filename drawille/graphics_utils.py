import os
from collections import defaultdict
import curses
__author__ = 'ericmuxagata'


COLOR_BLACK     = curses.COLOR_BLACK
COLOR_RED       = curses.COLOR_RED
COLOR_GREEN     = curses.COLOR_GREEN
COLOR_BLUE      = curses.COLOR_BLUE
COLOR_YELLOW    = curses.COLOR_YELLOW
COLOR_CYAN      = curses.COLOR_CYAN
COLOR_MAGENTA   = curses.COLOR_MAGENTA
COLOR_WHITE     = curses.COLOR_WHITE


DEFAULT_COLORS = {COLOR_WHITE:0,
                  COLOR_RED:1,
                  COLOR_GREEN:2,
                  COLOR_BLUE:3,
                  COLOR_YELLOW:4}

KEY_UP      = curses.KEY_UP
KEY_DOWN    = curses.KEY_DOWN
KEY_LEFT    = curses.KEY_LEFT
KEY_RIGHT   = curses.KEY_RIGHT


# http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
def getTerminalSize():
    """Returns terminal width, height
    """
    env = os.environ

    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return
        return cr

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)

    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass

    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

    return int(cr[1]), int(cr[0])

def get_terminal_size_in_pixels():
    tw, th = getTerminalSize()
    return (2*tw,4*th)


# rounds real valued coords to pixel coords.
def normalize(coord):
    coord_type = type(coord)

    if coord_type == int:
        return coord
    elif coord_type == float:
        return int(round(coord))
    else:
        raise TypeError("Unsupported coordinate type <{0}>".format(type(coord)))


def intdefaultdict():
    return defaultdict(int)


def get_pos(x, y):
    """Convert x, y to cols, rows"""
    return normalize(x) // 2, normalize(y) // 4