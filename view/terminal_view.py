# view/terminal_view.py — Main facade of the terminal view (eighth-block).
#
# Provides the TerminalView class used by the controller and the menu.
# Delegates:
#   - terminal launch  → view.terminal_launcher
#   - rendering and animation   → view.terminal_renderer

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from colorama import init, Fore, Style
from model.maze import Maze
from view.ansi_utils import read_key
from view.terminal_launcher import _spawn_solution_window
from view.terminal_renderer import (
    _draw_grid, _animate, _draw_final, _erase_corners
)

init(autoreset=False)


class TerminalView:

    COLOR = {
        "wall": Fore.WHITE,
        "42": Fore.LIGHTBLUE_EX + Style.BRIGHT,
        "path": Fore.GREEN,
        "cursor": Fore.GREEN + Style.BRIGHT,
        "entry": Fore.WHITE,
        "exit": Fore.RED,
        "info": Fore.GREEN,
    }

    RESET = Style.RESET_ALL

    def __init__(
        self,
        maze: Maze,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] = (0, 0),
        forty_two_cells: set[tuple[int, int]] | None = None,
        path_connections: dict[tuple[int, int], list[str]] | None = None,
    ) -> None:
        self.maze = maze
        self.entry = entry
        self.exit_pos = exit
        self.forty_two: set[tuple[int, int]] = set(forty_two_cells or [])
        self.path_connections: dict[tuple[int, int], list[str]] = (
            path_connections or {}
        )

    @staticmethod
    def _read_key() -> str:
        """Reads a key without waiting for Enter (raw mode)."""
        return read_key()

    def show_solution(
        self,
        all_paths: list[dict[tuple[int, int], list[str]]],
        is_perfect: bool,
        tracks: list[tuple[int, int, str]] | None = None,
    ) -> None:
        """Opens a new terminal window and animates the generation."""
        # Displays whether the maze is perfect or imperfect

        cell_width = 1
        solution_cells: list[list[int | list[str]]] = [
            [x, y, list(dirs)]
            for (x, y), dirs in (all_paths[0].items() if all_paths else [])
        ]
        # Attempt to open a new window for smoother
        # animation and cleaner rendering
        # without the artifacts of the current terminal.
        if tracks and _spawn_solution_window(
            self.maze.width,
            self.maze.height,
            tracks,
            cell_width,
            is_perfect,
            entry=self.entry,
            exit_pos=self.exit_pos,
            solution_cells=solution_cells,
            forty_two_cells=list(self.forty_two),
            maze_grid=[list(row) for row in self.maze.grid],
        ):
            return

        # Fallback: display in the current terminal
        _draw_grid(self.maze.width, self.maze.height, cell_width,
                   forty_two_cells=self.forty_two,
                   forty_two_color=self.COLOR["42"])

        _animate(tracks or [], self.maze.width, self.maze.height, cell_width,
                 forty_two_cells=self.forty_two,
                 forty_two_color=self.COLOR["42"])
        _erase_corners(
            [list(row) for row in self.maze.grid],
            self.maze.width, self.maze.height, cell_width
        )
        solution = (
            [(x, y, dirs) for (x, y), dirs in all_paths[0].items()]
            if all_paths
            else []
        )

        # Also displays in the final status bar
        _draw_final(
            self.maze.width,
            self.maze.height,
            cell_width,
            self.entry,
            self.exit_pos,
            solution,
            is_perfect,
            solution_visible=True,
        )
