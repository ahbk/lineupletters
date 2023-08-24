# For touch typing enjoyers and aspires,
# keep the rythm and a line will emerge, maintain the line.

# Play with these keys
keys = "abcdefghijklmnopqrstuvxyz@.;"

# at this speed (50=slow, 200=fast).
speed = 100

# this frequency (50=sparse, 200=overwhelming)
frequency = 100

# and this many colors (0=black/white)
colors = 8

# Enjoy!

import curses, _curses
import random
import time


class v:
    def __init__(self, x: float, y: float) -> None:
        self.x, self.y = (x, y)
        self.ix, self.iy = (int(x), int(y))

    def __add__(self, other: "v") -> "v":
        return v(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "v") -> "v":
        return v(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "v":
        return v(scalar * self.x, scalar * self.y)

    def __repr__(self):
        return f"({self.ix}, {self.iy})"

    def __eq__(self, other):
        return self.ix == other.ix and self.iy == other.iy


class letter:
    def __init__(
        self, char: str, pos: v, vel: v = v(0, 0), acc: v = v(0, 0), col: int = 1
    ):
        self.char = char
        self._pos = v(-1, -1)
        self.pos = pos
        self.vel = vel
        self.acc = acc
        self.col = col

    def tick(self):
        self.vel += self.acc
        self.pos += self.vel

    def contained(self, box: v):
        return (
            self.pos.ix > -2
            and self.pos.iy > -2
            and self.pos.ix < box.ix + 1
            and self.pos.iy < box.iy + 1
        )

    def print(self, erase: str = " "):
        queue = []
        if self.pos != self._pos:
            queue = [
                (self.pos.iy, self.pos.ix, self.char, self.col),
                (self._pos.iy, self._pos.ix, erase, 0),
            ]
            self._pos = self.pos
        return queue

    def __repr__(self):
        return f"{self.char}@{self.pos}"


class letterchaos:
    def __init__(self, box: v):
        self.box = box
        self.letters = []

    def insert(self, letter: letter):
        self.letters.append(letter)

    def tick(self):
        for letter in self.letters:
            letter.tick()

        self.letters = [letter for letter in self.letters if letter.contained(self.box)]

    def clear(self, char: str):
        for i, l in enumerate(self.letters):
            if l.char == char:
                del self.letters[i]
                break

    def print(self):
        queue = []
        for letter in self.letters:
            queue += letter.print()
        return queue


def main(stdscr):
    stdscr.clear()
    curses.curs_set(False)
    stdscr.nodelay(True)

    my, mx = stdscr.getmaxyx()
    lc = letterchaos(v(mx, my))
    lc.insert(letter("↓", v(0.5 * mx, 0.25 * my - 1), col=0))
    lc.insert(letter("↑", v(0.5 * mx, 0.75 * my + 1), col=0))

    for i in range(colors):
        curses.init_pair(i + 1, i + 1, curses.COLOR_BLACK)

    counter = 0
    while True:
        key = stdscr.getch()

        time.sleep(15 / (speed * mx**0.5))
        lc.tick()

        counter += 1
        if counter % int((700 * mx**0.5) / frequency) == 0:
            side = random.choice([-1, 1])
            lc.insert(
                letter(
                    keys[random.randint(0, len(keys) - 1)],
                    v(
                        mx if side == 1 else 1,
                        .5 * my + random.randint(-int(0.25 * my), int(0.25 * my)),
                    ),
                    v(side * (-1), 0),
                    v(side / mx, 0),
                    random.randint(0, colors),
                )
            )

        if key > 0 and chr(key) in keys:
            lc.clear(chr(key))

        if key == ord(" "):  # Space to pause
            stdscr.nodelay(0)
            key = stdscr.getch()
            stdscr.nodelay(1)

        if key == 27:  # Esc to exit
            break

        for y, x, l, c in lc.print():
            try:
                stdscr.addstr(y, x, l, curses.color_pair(c) | curses.A_BOLD)
            except _curses.error:
                pass

        stdscr.refresh()


curses.wrapper(main)
