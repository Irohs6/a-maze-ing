# view/terminal_view.py — Main facade of the terminal view (eighth-block).
#
# Provides the TerminalView class used by the controller and the menu.
# Delegates:
#   - terminal launch  → view.terminal_launcher
#   - rendering and animation   → view.terminal_renderer

import sys
import tty
import termios

try:
    from colorama import Fore, Style
except ImportError:
    print("\033c", end="")
    print(
        "Colorama not found, try starting the program with 'make run' command."
    )
    sys.exit(7)
from ..model.maze import Maze
from .terminal_renderer import TerminalRenderer


class TerminalView:
    """High-level view facade: delegates rendering to TerminalRenderer."""

    def __init__(
        self,
        maze: Maze,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] = (0, 0),
        forty_two_cells: set[tuple[int, int]] | None = None,
    ) -> None:
        """Initialize the view with maze data and entry/exit positions."""
        self.maze = maze
        self.entry = entry
        self.exit_pos = exit
        self.forty_two: set[tuple[int, int]] = set(forty_two_cells or [])
        self.render = TerminalRenderer(self.maze, self.entry, self.exit_pos)
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)

    def _get_key(self) -> None:
        """Read a single key or escape sequence from stdin."""
        try:
            tty.setraw(self.fd)
            self.input = sys.stdin.read(1)
            if self.input.startswith("\x1b"):
                self.input += sys.stdin.read(2)
        finally:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

    def _display_input(self, speed: int, is_perfect: bool) -> None:
        """Print the status line (perfect/imperfect, shortcuts)
             below the maze."""
        is_perfect_message = (
            Fore.GREEN + "Perfect Maze !" + Style.RESET_ALL
            if is_perfect
            else Fore.RED + "Imperfect Maze !" + Style.RESET_ALL
        )
        is_forty_two_message = (
            Fore.YELLOW
            + " (Couldn't place 42 pattern because maze is too small) "
            + Style.RESET_ALL
            if self.forty_two == set()
            else ""
        )
        sys.stdout.write(f"\r{is_perfect_message}{is_forty_two_message}\n")
        sys.stdout.write(
            f"COLOR: C   SHOW/HIDE SOLUTION: S   "
            f"REPLAY: R   SPEED LEVEL ({speed}): +/-   QUIT: Q"
        )
        sys.stdout.write("\033[A")
        sys.stdout.flush()

    def draw_grid(
        self,
        tracks: list[tuple[int, int, str]],
        paths: list[tuple[int, int, str]],
        is_perfect: bool,
    ) -> None:
        """Animate maze generation and handle interactive keyboard input."""
        solution_visible = False
        speed = self.render._DEFAULT_SPEED_IDX + 1
        try:
            print("\033[?25l", end="")
            speed = self.render._animate_grid(tracks, speed)
            self._display_input(speed, is_perfect)
            while True:
                self._get_key()
                if self.input in ("c", "C"):
                    solution_visible = False
                    print("\033c", end="")
                    self.render._EMOJI_INDEX += 1
                    if self.render._EMOJI_INDEX == len(
                        self.render._EMOJI_LIST[0]
                    ):
                        self.render._EMOJI_INDEX = 0
                    self.render._final_grid()
                    self._display_input(speed, is_perfect)
                if self.input in ("r", "R"):
                    print("\033c", end="")
                    speed = self.render._animate_grid(tracks, speed)
                    self._display_input(speed, is_perfect)
                if self.input in ("+"):
                    self.render._DEFAULT_SPEED_IDX += 1
                    if self.render._DEFAULT_SPEED_IDX == len(
                        self.render._SPEED_LEVELS
                    ):
                        self.render._DEFAULT_SPEED_IDX = 0
                    speed = self.render._DEFAULT_SPEED_IDX + 1
                    self._display_input(speed, is_perfect)
                if self.input in ("-"):
                    self.render._DEFAULT_SPEED_IDX -= 1
                    if self.render._DEFAULT_SPEED_IDX == -1:
                        self.render._DEFAULT_SPEED_IDX = (
                            len(self.render._SPEED_LEVELS) - 1
                        )
                    speed = self.render._DEFAULT_SPEED_IDX + 1
                    self._display_input(speed, is_perfect)
                if self.input in ("s", "S"):
                    # toggle solution animation
                    try:
                        tty.setraw(self.fd)
                        solution_visible = not solution_visible
                        if solution_visible:
                            self.render._animate_solution(paths)
                        else:
                            self.render._erase_solution(paths)
                    finally:
                        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
                elif self.input in ("q", "Q"):
                    print("\033c", end="")
                    break

        finally:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
            print("\033[?25h", end="")
