# For touch typing enjoyers and aspires,
# keep the rythm and a line will emerge, maintain the line.

# Play with these keys
keys = "abcdefghijklmnopqrstuvxyz@.;"

# at this speed (50=slow, 200=fast)
speed = 100

# this frequency (50=sparse, 200=overwhelming)
frequency = 100

# and this many colors (1=white only)
colors = 7

# Enjoy!

import curses, _curses
import random
import time
import threading


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

    def __repr__(self) -> str:
        return f"({self.ix}, {self.iy})"

    def __eq__(self, other) -> bool:
        return self.ix == other.ix and self.iy == other.iy


class letter:
    def __init__(
        self, char: str, pos: v, vel: v = v(0, 0), acc: v = v(0, 0), col: int = 1
    ) -> None:
        self.char = char
        self._pos = v(-1, -1)
        self.pos = pos
        self.vel = vel
        self.acc = acc
        self.col = col

    def tick(self) -> None:
        self.vel += self.acc
        self.pos += self.vel

    def contained(self, box: v) -> bool:
        return (
            self.pos.ix > -2
            and self.pos.iy > -2
            and self.pos.ix < box.ix + 1
            and self.pos.iy < box.iy + 1
        )

    def queue(self, erase: str = " ") -> list[tuple[int, int, str, int]]:
        q = []
        if self.pos != self._pos:
            q = [
                (self.pos.iy, self.pos.ix, self.char, self.col),
                (self._pos.iy, self._pos.ix, erase, 0),
            ]
            self._pos = self.pos
        return q

    def __repr__(self) -> str:
        return f"{self.char}@{self.pos}"


class letterchaos:
    def __init__(self, box: v) -> None:
        self.box = box
        self.letters = []

    def insert(self, letter: letter) -> None:
        self.letters.append(letter)

    def tick(self) -> None:
        for letter in self.letters:
            letter.tick()

        self.letters = [letter for letter in self.letters if letter.contained(self.box)]

    def clear(self, char: str) -> None:
        for i, l in enumerate(self.letters):
            if l.char == char:
                del self.letters[i]
                break

    def queue(self) -> list[tuple[int, int, str, int]]:
        q = []
        for letter in self.letters:
            q += letter.queue()
        return q


def insertletter(lc):
    side = random.choice([-1, 1])
    k = random.randint(0, len(keys) - 1)
    lc.insert(
        letter(
            keys[k],
            v(
                lc.box.ix if side == 1 else 1,
                0.5 * lc.box.iy
                + random.randint(-int(0.25 * lc.box.iy), int(0.25 * lc.box.iy)),
            ),
            v(side * (-1), 0),
            v(side / lc.box.ix, 0),
            k % colors,
        )
    )


def main(stdscr):
    stdscr.clear()
    curses.curs_set(False)
    stdscr.nodelay(True)

    my, mx = stdscr.getmaxyx()
    lc = letterchaos(v(mx, my))
    lc.insert(letter("↓", v(0.5 * mx, 0.25 * my - 1), col=0))
    lc.insert(letter("↑", v(0.5 * mx, 0.75 * my + 1), col=0))

    measure = int(512 * (mx**0.5) / frequency)

    for i in range(colors):
        curses.init_pair(i + 1, i + 1, curses.COLOR_BLACK)

    counter = 0
    while True:
        key = stdscr.getch()

        if key > 0 and chr(key) in keys:
            lc.clear(chr(key))

        if key == ord(" "):  # Space to pause
            stdscr.nodelay(0)
            key = stdscr.getch()
            stdscr.nodelay(1)

        if key == 27:  # Esc to exit
            break

        for y, x, l, c in lc.queue():
            try:
                stdscr.addstr(y, x, l, curses.color_pair(c) | curses.A_BOLD)
            except _curses.error:
                pass

        stdscr.refresh()
        time.sleep(16 / (speed * mx**0.5))
        lc.tick()

        counter += 1
        if counter % measure == 0:
            insertletter(lc)
            counter = 0


curses.wrapper(main)
