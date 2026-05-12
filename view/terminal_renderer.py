import time
from typing import NamedTuple
from colorama import Fore, Style
import sys
from model.maze import Maze


class TerminalRenderer:

    class ColorTheme(NamedTuple):
        wall: str
        forty_two: str

    COLOR_THEMES: list[ColorTheme] = [
        ColorTheme(Fore.BLUE, Fore.YELLOW + Style.BRIGHT),
        ColorTheme(Fore.RED, Fore.GREEN + Style.BRIGHT),
        ColorTheme(Fore.GREEN, Fore.CYAN + Style.BRIGHT),
        ColorTheme(Fore.MAGENTA, Fore.BLUE + Style.BRIGHT),
        ColorTheme(Fore.CYAN, Fore.MAGENTA + Style.BRIGHT),
        ColorTheme(Fore.YELLOW, Fore.RED + Style.BRIGHT),
        ColorTheme(Fore.LIGHTBLUE_EX, Fore.CYAN + Style.BRIGHT),
    ]

    _DIRECTION_ARROWS: dict[str, str] = {
        "N": "⮝",
        "E": "⮞",
        "S": "⮟",
        "W": "⮜"
    }

    # Animation speed levels: (delay in s, displayed label).
    # [+] → faster (lower index), [-] → slower (higher index)
    _SPEED_LEVELS: list[tuple[float, str]] = [
        (0.2, "1"),  # very slow
        (0.05, "2"),
        (0.01, "3"),
        (0.001, "4"),  # default speed
        (0.0003, "5"),
        (0.0, "6"),  # as fast as possible (no delay, single final flush)
    ]
    _DEFAULT_SPEED_IDX: int = 3

    _EMOJI_LIST = [
        "✋", "🌲", "🌳", "🌵", "🌿", "🌟", "✨",
        "⬛", "⬜", "🔴",
        "🔵", "🔥", "💧", "🍄", "🎃", "👹", "👾",
        "🤖", "👻", "👽", "💩", "💎", "🔮", "🚪",
        "🌲", "🎄", "🌻", "🌹", "🌷", "🌼", "🌸", "🌺", "🌍", "🌕"
    ]
    _EMOJI_INDEX = 0

    _WALL_FORTY_TWO = "⬛"

    def __init__(self, maze: Maze):
        self.maze = maze

    def _print_full(self, y):
        forty_two = False
        for x in range(self.maze.width):
            if (x, y) in self.maze.forty_two_cells or (x, y-1) in self.maze.forty_two_cells:
                sys.stdout.write(self._WALL_FORTY_TWO * 2)
                forty_two = True
            else:
                if forty_two:
                    sys.stdout.write(self._WALL_FORTY_TWO)
                    sys.stdout.write(self._EMOJI_LIST[self._EMOJI_INDEX])
                    forty_two = False
                else:
                    sys.stdout.write(self._EMOJI_LIST[self._EMOJI_INDEX])
                    sys.stdout.write(self._EMOJI_LIST[self._EMOJI_INDEX])
        end_char = self._WALL_FORTY_TWO if forty_two else self._EMOJI_LIST[self._EMOJI_INDEX]
        sys.stdout.write(f"{end_char}\n")

    def _print_middle(self, y):
        forty_two = False
        for x in range(self.maze.width):
            if (x, y) in self.maze.forty_two_cells:
                sys.stdout.write(self._WALL_FORTY_TWO * 2)
                forty_two = True
            else:
                if forty_two:
                    sys.stdout.write(self._WALL_FORTY_TWO)
                    sys.stdout.write("  ")
                    forty_two = False
                else:
                    sys.stdout.write(self._EMOJI_LIST[self._EMOJI_INDEX])
                    sys.stdout.write("  ")
        end_char = self._WALL_FORTY_TWO if forty_two else self._EMOJI_LIST[self._EMOJI_INDEX]
        sys.stdout.write(f"{end_char}\n")

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

    def _animate_grid(self, tracks):
        self._display_grid()
        for x, y, direction in tracks:
            tx, ty = self._get_terminal_coordinates(x, y)
            sys.stdout.write(f"\033[{ty};{tx}f")
            if direction == "E":
                sys.stdout.write("   ")
            elif direction == "W":
                sys.stdout.write("\b ")
            elif direction == "S":
                sys.stdout.write(f"\033[{ty + 1};{tx}f")
                sys.stdout.write(" ")
            else:
                sys.stdout.write(f"\033[{ty - 1};{tx}f")
                sys.stdout.write(" ")
            sys.stdout.flush()
            time.sleep(0.008)
        _, ty = self._get_terminal_coordinates(0, self.maze.height + 1)
        sys.stdout.write(f"\033[{ty};{1}f")
        sys.stdout.flush()
