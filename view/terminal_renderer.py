from importlib.metadata import entry_points
from re import I
import time
import sys
from model.maze import Maze
import tty
import termios
import select


class TerminalRenderer:

    _DIRECTION_ARROWS: dict[str, str] = {
        "N": "⮝",
        "E": "⮞",
        "S": "⮟",
        "W": "⮜"
    }

    # Animation speed levels: (delay in s, displayed label).
    # [+] → faster (lower index), [-] → slower (higher index)
    _SPEED_LEVELS: list[tuple[float, str]] = [
        (0.1, "1"),  # as slow as possible (delay after every frame)
        (0.01, "2"),
        (0.005, "3"),
        (0.001, "4"),  # default speed
        (0.0003, "5"),
        (0.0001, "6"),  # as fast as possible (no delay, single final flush)
    ]
    _DEFAULT_SPEED_IDX: int = 1

    _EMOJI_LIST = [
        [
            "✋", "🌲", "🌳", "🌵", "🌟", "⬛",
            "⬜", "🔴", "🔵", "🔥", "💧", "🍄", "🌕",
            "🎃", "👹", "👾", "🤖", "👻", "👽",
            "💎", "🔮", "🌻", "🌹",
            "🌷", "🌼", "🌸", "🌺", "🌍"
        ],
        [
            "💎", "🌷", "🍄", "🌼", "🔮", "⬜",
            "⬛", "🔵", "🔴", "💧", "🔥", "🌳", "🌍",
            "👻", "👾", "👹", "👽", "🎃", "🤖",
            "✋", "🌟", "🌸", "🌺",
            "🌲", "🌵", "🌻", "🌹", "🌕",
        ]
    ]
    _EMOJI_INDEX = 0

    _EMOJI_ENTRY = "🏃"
    _EMOJI_EXIT = "🏆"

    def __init__(self, maze: Maze, entry, exit_pos):
        self.maze = maze
        self.entry = entry
        self.exit_pos = exit_pos
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)

    def _get_key_or_timeout(self, timeout: float = 0.0) -> None:
        try:
            # Use select to wait for input up to 'timeout' seconds
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if rlist:
                self.input = sys.stdin.read(1)
                if self.input.startswith("\x1b"):
                    self.input += sys.stdin.read(2)
            else:
                self.input = None
        except Exception:
            self.input = None

    def _print_full(self, y):
        forty_two = False
        for x in range(self.maze.width):
            if (x, y) in self.maze.forty_two_cells or (
                    x, y-1) in self.maze.forty_two_cells:
                sys.stdout.write(self._EMOJI_LIST[1][self._EMOJI_INDEX] * 2)
                forty_two = True
            else:
                if forty_two:
                    sys.stdout.write(self._EMOJI_LIST[1][self._EMOJI_INDEX])
                    sys.stdout.write(self._EMOJI_LIST[0][self._EMOJI_INDEX])
                    forty_two = False
                else:
                    sys.stdout.write(self._EMOJI_LIST[0][self._EMOJI_INDEX])
                    sys.stdout.write(self._EMOJI_LIST[0][self._EMOJI_INDEX])
        sys.stdout.write(f"{self._EMOJI_LIST[0][self._EMOJI_INDEX]}\n")

    def _print_middle(self, y):
        forty_two = False
        for x in range(self.maze.width):
            if (x, y) in self.maze.forty_two_cells:
                sys.stdout.write(self._EMOJI_LIST[1][self._EMOJI_INDEX] * 2)
                forty_two = True
            else:
                if forty_two:
                    sys.stdout.write(self._EMOJI_LIST[1][self._EMOJI_INDEX])
                    sys.stdout.write("  ")
                    forty_two = False
                else:
                    sys.stdout.write(self._EMOJI_LIST[0][self._EMOJI_INDEX])
                    if x == self.entry[0] and y == self.entry[1]:
                        sys.stdout.write(self._EMOJI_ENTRY)
                    elif x == self.exit_pos[0] and y == self.exit_pos[1]:
                        sys.stdout.write(self._EMOJI_EXIT)
                    else:
                        sys.stdout.write("  ")
        sys.stdout.write(f"{self._EMOJI_LIST[0][self._EMOJI_INDEX]}\n")

    def _print_cells_lign(self, y):
        self._print_full(y)
        self._print_middle(y)

    def _display_grid(self) -> None:
        for y in range(self.maze.height):
            self._print_cells_lign(y)
        self._print_full(y)
        sys.stdout.flush()

    def _get_terminal_coordinates(self, x: int, y: int) -> tuple[int, int]:
        tx, ty = 3, 2
        tx += x * 4
        ty += y * 2
        return (tx, ty)

    def _final_grid(self) -> None:
        directions = ["E", "S"]
        self._display_grid()
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                tx, ty = self._get_terminal_coordinates(x, y)
                sys.stdout.write(f"\033[{ty};{tx}f")
                for direction in directions:
                    sys.stdout.write(f"\033[{ty};{tx}f")
                    if not self.maze.has_wall(x, y, direction):
                        if direction == "E":
                            sys.stdout.write("   ")
                        else:
                            sys.stdout.write(f"\033[{ty + 1};{tx}f")
                            sys.stdout.write(" ")
        _, ty = self._get_terminal_coordinates(0, self.maze.height + 1)
        sys.stdout.write(f"\033[{ty};{1}f")
        sys.stdout.flush()

    def dispaly_shorcuts(self, speed: int) -> None:
        _, ty = self._get_terminal_coordinates(
                        0, self.maze.height + 1)
        sys.stdout.write(f"\033[{ty + 1};{1}f")
        sys.stdout.write(f"SPEED LEVEL ({speed}): +/- ")

    def _animate_grid(self, tracks, speed: int) -> None:

        self._display_grid()
        self.dispaly_shorcuts(speed)
        try:
            tty.setraw(self.fd)
            for x, y, direction in tracks:
                tx, ty = self._get_terminal_coordinates(x, y)
                sys.stdout.write(f"\033[{ty};{tx}f")
                if direction == "E":
                    sys.stdout.write("\033[2C")
                    sys.stdout.write("  ")
                elif direction == "W":
                    sys.stdout.write("\b\b  ")
                elif direction == "S":
                    sys.stdout.write(f"\033[{ty + 1};{tx}f")
                    sys.stdout.write("  ")
                else:
                    sys.stdout.write(f"\033[{ty - 1};{tx}f")
                    sys.stdout.write("  ")
                sys.stdout.flush()

                self._get_key_or_timeout(self._SPEED_LEVELS[
                    self._DEFAULT_SPEED_IDX][0])
                if self.input:
                    if self.input in ("+"):
                        self._DEFAULT_SPEED_IDX += 1
                        if self._DEFAULT_SPEED_IDX == len(
                                self._SPEED_LEVELS):
                            self._DEFAULT_SPEED_IDX = 0
                        speed = self._DEFAULT_SPEED_IDX + 1
                        self.dispaly_shorcuts(speed)
                    if self.input in ("-"):
                        self._DEFAULT_SPEED_IDX -= 1
                        if self._DEFAULT_SPEED_IDX == -1:
                            self._DEFAULT_SPEED_IDX = len(
                                    self._SPEED_LEVELS) - 1
                        speed = self._DEFAULT_SPEED_IDX + 1
                        self.dispaly_shorcuts(speed)
                    sys.stdout.write(f"\033[{ty};{tx}f")
                    sys.stdout.flush()

            _, ty = self._get_terminal_coordinates(0, self.maze.height + 1)
            sys.stdout.write(f"\033[{ty};{1}f")
            sys.stdout.flush()
        finally:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

        return speed

    def _animate_solution(self, paths: list[dict[tuple[int, int], list[str]]]):
        for (x, y), directions in paths[0].items():
            if x == self.entry[0] and y == self.entry[1] or x == self.exit_pos[0] and y == self.exit_pos[1]:
                continue
            else:
                tx, ty = self._get_terminal_coordinates(x, y)
                sys.stdout.write(f"\033[{ty};{tx}f")
                sys.stdout.write(self._DIRECTION_ARROWS[directions[-1]])
                sys.stdout.flush()
                time.sleep(0.05)
        _, ty = self._get_terminal_coordinates(0, self.maze.height + 1)
        sys.stdout.write(f"\033[{ty};{1}f")
        sys.stdout.flush()

    def _erase_solution(self, paths: list[dict[tuple[int, int], list[str]]]):
        reversed = [key for key in paths[0].keys()][::-1]
        for x, y in reversed:
            if x == self.entry[0] and y == self.entry[1] or x == self.exit_pos[0] and y == self.exit_pos[1]:
                continue
            else:
                tx, ty = self._get_terminal_coordinates(x, y)
                sys.stdout.write(f"\033[{ty};{tx}f")
                sys.stdout.write(" ")
                sys.stdout.flush()
                time.sleep(0.05)
        _, ty = self._get_terminal_coordinates(0, self.maze.height + 1)
        sys.stdout.write(f"\033[{ty};{1}f")
        sys.stdout.flush()
