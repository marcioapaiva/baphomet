# -*- coding: utf-8 -*-

# drawille is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# drawille is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with drawille. If not, see < http://www.gnu.org/licenses/ >.
#
# (C) 2014- by Adam Tauber, <asciimoo@gmail.com>

from graphics_utils import normalize, get_pos, intdefaultdict, DEFAULT_COLORS
import math
import os
from sys import version_info
from collections import defaultdict
from time import sleep
import curses


global stdscr

IS_PY3 = version_info[0] == 3

if IS_PY3:
    unichr = chr

"""

http://www.alanwood.net/unicode/braille_patterns.html

dots:
   ,___,
   |1 4|
   |2 5|
   |3 6|
   |7 8|
   `````
"""

pixel_map = ((0x01, 0x08),
             (0x02, 0x10),
             (0x04, 0x20),
             (0x40, 0x80))

# braille unicode characters starts at 0x2800
braille_char_offset = 0x2800


class Canvas(object):
    """This class implements the pixel surface."""

    def __init__(self, line_ending=os.linesep):
        super(Canvas, self).__init__()
        self.clear()
        self.line_ending = line_ending


    def clear(self):
        """Remove all pixels from the :class:`Canvas` object."""
        self.chars = defaultdict(intdefaultdict)
        self.colors = defaultdict(intdefaultdict)


    def set(self, x, y):
        """Set a pixel of the :class:`Canvas` object.

        :param x: x coordinate of the pixel
        :param y: y coordinate of the pixel
        """
        x = normalize(x)
        y = normalize(y)
        col, row = get_pos(x, y)

        if type(self.chars[row][col]) != int:
            return

        self.chars[row][col] |= pixel_map[y % 4][x % 2]


    def unset(self, x, y):
        """Unset a pixel of the :class:`Canvas` object.

        :param x: x coordinate of the pixel
        :param y: y coordinate of the pixel
        """
        x = normalize(x)
        y = normalize(y)
        col, row = get_pos(x, y)

        if type(self.chars[row][col]) == int:
            self.chars[row][col] &= ~pixel_map[y % 4][x % 2]

        if type(self.chars[row][col]) != int or self.chars[row][col] == 0:
            del(self.chars[row][col])

        if not self.chars.get(row):
            del(self.chars[row])


    def toggle(self, x, y):
        """Toggle a pixel of the :class:`Canvas` object.

        :param x: x coordinate of the pixel
        :param y: y coordinate of the pixel
        """
        x = normalize(x)
        y = normalize(y)
        col, row = get_pos(x, y)

        if type(self.chars[row][col]) != int or self.chars[row][col] & pixel_map[y % 4][x % 2]:
            self.unset(x, y)
        else:
            self.set(x, y)


    def set_text(self, x, y, text):
        """Set text to the given coords.

        :param x: x coordinate of the text start position
        :param y: y coordinate of the text start position
        """
        col, row = get_pos(x, y)

        for i,c in enumerate(text):
            self.chars[row][col+i] = c

    def set_color(self,x,y,color):
        """Set color to the given coords.

        :param x: x coordinate of the char to be colored
        :param y: y coordinate of the char to be colored
        """
        col,row = get_pos(x,y)
        self.colors[row][col] = color


    def get(self, x, y):
        """Get the state of a pixel. Returns bool.

        :param x: x coordinate of the pixel
        :param y: y coordinate of the pixel
        """
        x = normalize(x)
        y = normalize(y)
        dot_index = pixel_map[y % 4][x % 2]
        col, row = get_pos(x, y)
        char = self.chars.get(row, {}).get(col)

        if not char:
            return False

        if type(char) != int:
            return True

        return bool(char & dot_index)


    def rows(self, min_x=None, min_y=None, max_x=None, max_y=None):
        """Returns a list of the current :class:`Canvas` object lines.
        :param min_x: (optional) minimum x coordinate of the canvas
        :param min_y: (optional) minimum y coordinate of the canvas
        :param max_x: (optional) maximum x coordinate of the canvas
        :param max_y: (optional) maximum y coordinate of the canvas
        """

        if not self.chars.keys():
            return []

        minrow = min_y // 4 if min_y != None else min(self.chars.keys())
        maxrow = (max_y - 1) // 4 if max_y != None else max(self.chars.keys())
        mincol = min_x // 2 if min_x != None else min(min(x.keys()) for x in self.chars.values())
        maxcol = (max_x - 1) // 2 if max_x != None else max(max(x.keys()) for x in self.chars.values())
        ret = []

        for rownum in range(minrow, maxrow+1):
            if not rownum in self.chars:
                ret.append('')
                continue

            maxcol = (max_x - 1) // 2 if max_x != None else max(self.chars[rownum].keys())
            row = []

            for x in  range(mincol, maxcol+1):
                char = self.chars[rownum].get(x)

                if not char:
                    row.append(' ')
                elif type(char) != int:
                    row.append(char)
                else:
                    row.append(unichr(braille_char_offset+char))

            ret.append(''.join(row))

        return ret


    def frame(self, min_x=None, min_y=None, max_x=None, max_y=None):
        """String representation of the current :class:`Canvas` object pixels.
        :param min_x: (optional) minimum x coordinate of the canvas
        :param min_y: (optional) minimum y coordinate of the canvas
        :param max_x: (optional) maximum x coordinate of the canvas
        :param max_y: (optional) maximum y coordinate of the canvas
        """
        ret = self.line_ending.join(self.rows(min_x, min_y, max_x, max_y))

        if IS_PY3:
            return ret

        return ret.encode('utf-8')


def line(x1, y1, x2, y2):
    """Returns the coords of the line between (x1, y1), (x2, y2)

    :param x1: x coordinate of the startpoint
    :param y1: y coordinate of the startpoint
    :param x2: x coordinate of the endpoint
    :param y2: y coordinate of the endpoint
    """

    x1 = normalize(x1)
    y1 = normalize(y1)
    x2 = normalize(x2)
    y2 = normalize(y2)

    xdiff = max(x1, x2) - min(x1, x2)
    ydiff = max(y1, y2) - min(y1, y2)
    xdir = 1 if x1 <= x2 else -1
    ydir = 1 if y1 <= y2 else -1

    r = max(xdiff, ydiff)

    for i in range(r+1):
        x = x1
        y = y1

        if ydiff:
            y += (float(i) * ydiff) / r * ydir
        if xdiff:
            x += (float(i) * xdiff) / r * xdir

        yield (x, y)


class Palette(object):
    def __init__(self):
        #each color has an (r,g,b) value as key, mapped to its (color_idx,pair_idx) tuple.
        self.colors = dict(DEFAULT_COLORS)
        self.pair_index = len(DEFAULT_COLORS)

    def start_colors(self):
        if not curses.has_colors():
            return

        print "starting color"
        curses.start_color()
        for color_index in self.colors.keys():
            pair_index = self.colors[color_index]
            if pair_index != 0:
                curses.init_pair(pair_index, color_index, curses.COLOR_BLACK)

    def add_color(self,color_index):
        if color_index not in self.colors:
            self.colors[color_index] = self.pair_index
            self.pair_index += 1


def handle_input():
    global stdscr
    return stdscr.getch()


def animate(canvas, palette, fn, delay=1./24, *args, **kwargs):
    """Animation automatition function

    :param canvas: :class:`Canvas` object
    :param fn: Callable. Frame coord generator
    :param delay: Float. Delay between frames.
    :param *args, **kwargs: optional fn parameters
    """

    # python2 unicode curses fix
    if not IS_PY3:
        import locale
        locale.setlocale(locale.LC_ALL, "")

    def animation(stdscr):
        for frame in fn(*args, **kwargs):
            stdscr.erase()
            for x, y, c in frame:
                canvas.set(x, y)
                canvas.set_color(x, y, c)

                col, row = get_pos(x, y)
                color = canvas.colors[row][col]

                color_pair = curses.color_pair(0)
                if color in palette.colors:
                    color_pair = curses.color_pair(palette.colors[color])

                stdscr.addstr(row, col, unichr(braille_char_offset+canvas.chars[row][col]).encode('utf-8'), color_pair)

            stdscr.refresh()
            if delay:
                sleep(delay)
            canvas.clear()

    animation_wrapper(animation,palette)


def animation_wrapper(func, palette, *args, **kwds):
    global stdscr
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        stdscr.keypad(1)
        stdscr.nodelay(True)

        palette.start_colors()

        return func(stdscr, *args, **kwds)
    finally:
        # Set everything back to normal
        if 'stdscr' in locals() or globals():
            stdscr.keypad(0)
            stdscr.nodelay(False)
            curses.echo()
            curses.curs_set(1)
            curses.nocbreak()
            curses.endwin()



