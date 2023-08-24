import curses, _curses
import random
import time


# For touch typing enjoyers and aspires,
# keep the rythm and a line will emerge, maintain the line.

# Play with these keys
keys = "abcdefghijklmnopqrstuvxyz@."

# at this speed (50=slow, 200=fast).
speed = 100

# this frequency (50=sparse, 200=overwhelming)
frequency = 100

# and this many colors (0=black/white)
colors = 8

# Enjoy!


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
        self._pos = self.pos = pos
        self.vel = vel or v(0, 0)
        self.acc = acc or v(0, 0)
        self.col = col

    def tick(self):
        self.vel += self.acc
        self.pos += self.vel

    def contained(self, box):
        return (
            self.pos.ix > -2
            and self.pos.iy > -2
            and self.pos.ix < box.ix + 1
            and self.pos.iy < box.iy + 1
        )

    def print(self, erase=" "):
        args = [
            (
                self.pos.iy,
                self.pos.ix,
                self.char,
                self.col,
            )
        ]
        if self.pos != self._pos:
            args += [
                (
                    self._pos.iy,
                    self._pos.ix,
                    erase,
                    0,
                )
            ]
            self._pos = self.pos
        return args

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
        self.letters = [letter for letter in self.letters if letter.char != char]

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
    lc.insert(letter("↓", v(mx / 2, my / 2 - my / 4 - 1), col=0))
    lc.insert(letter("↑", v(mx / 2, my / 2 + my / 4 + 1), col=0))

    counter = 0
    while True:
        key = stdscr.getch()

        for i in range(colors):
            curses.init_pair(i + 1, i + 1, curses.COLOR_BLACK)

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
                        my / 2 + random.randint(-int(my / 4), int(my / 4)),
                    ),
                    v(side * (-1), 0),
                    v(side / mx, 0),
                    random.randint(0, colors),
                )
            )

        if key > 0 and chr(key) in keys:
            lc.clear(chr(key))

        if key == ord(" "):
            stdscr.nodelay(0)
            key = stdscr.getch()
            stdscr.nodelay(1)

        for y, x, l, c in lc.print():
            try:
                stdscr.addstr(y, x, l, curses.color_pair(c))
            except _curses.error:
                pass

        stdscr.refresh()


curses.wrapper(main)
