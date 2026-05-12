# view/terminal_view.py — Main facade of the terminal view (eighth-block).
#
# Provides the TerminalView class used by the controller and the menu.
# Delegates:
#   - terminal launch  → view.terminal_launcher
#   - rendering and animation   → view.terminal_renderer

import sys
from pathlib import Path
import tty
import termios
if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from colorama import init, Fore, Style
from model.maze import Maze
from .terminal_renderer import TerminalRenderer

init(autoreset=False)


class TerminalView:

    FORTY_TWO_COLOR: str = Fore.LIGHTBLUE_EX + Style.BRIGHT

    def __init__(
        self,
        maze: Maze,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] = (0, 0),
        forty_two_cells: set[tuple[int, int]] | None = None
    ) -> None:
        self.maze = maze
        self.entry = entry
        self.exit_pos = exit
        self.forty_two: set[tuple[int, int]] = set(forty_two_cells or [])
        self.render = TerminalRenderer(self.maze)
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)

    def _get_key(self) -> None:
        try:
            tty.setraw(self.fd)
            self.input = sys.stdin.read(1)
            if self.input.startswith("\x1b"):
                self.input += sys.stdin.read(2)
        finally:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

    def draw_grid(self, tracks):
        try:
            print("\033[?25l", end="")
            self.render._animate_grid(tracks)
            while True:
                self._get_key()
                if self.input in ("c", "C"):
                    print("\033c", end="")
                    self.render._EMOJI_INDEX += 1
                    if self.render._EMOJI_INDEX == len(self.render._EMOJI_LIST):
                        self.render._EMOJI_INDEX = 0
                    self.render._final_grid()
                elif self.input in ("q", "Q"):
                    break

        finally:
            print("\033[?25h", end="")
