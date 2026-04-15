# view/terminal_view.py — Façade principale de la vue terminal (eighth-block).
#
# Fournit la classe TerminalView utilisée par le contrôleur et le menu.
# Délègue :
#   - le lancement de terminal  → view.terminal_launcher
#   - le rendu et l'animation   → view.terminal_renderer

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from colorama import init, Fore, Style
from model.maze import Maze
from view.ansi_utils import read_key
from view.terminal_launcher import _spawn_solution_window
from view.terminal_renderer import (
    _draw_grid, _animate, _draw_final, _run_solution_toggle,
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
        path_connections: dict[tuple[int, int], set[str]] | None = None,
    ) -> None:
        self.maze = maze
        self.entry = entry
        self.exit_pos = exit
        self.forty_two: set[tuple[int, int]] = set(forty_two_cells or [])
        self.path_connections: dict[tuple[int, int], set[str]] = (
            path_connections or {}
        )

    @staticmethod
    def _read_key() -> str:
        """Lit une touche sans attendre Entrée (mode raw)."""
        return read_key()

    def show_solution(
        self,
        all_paths: list[dict[tuple[int, int], set[str]]],
        is_perfect: bool,
        tracks: list[tuple[int, int, str]] | None = None,
    ) -> None:
        """Ouvre une nouvelle fenêtre de terminal et anime la génération."""
        del is_perfect  # conservé pour compatibilité API

        cell_width = 1
        solution_cells = [
            [x, y, list(dirs)]
            for (x, y), dirs in (all_paths[0].items() if all_paths else [])
        ]
        if tracks and _spawn_solution_window(
            self.maze.width,
            self.maze.height,
            tracks,
            cell_width,
            entry=self.entry,
            exit_pos=self.exit_pos,
            solution_cells=solution_cells,
            forty_two_cells=list(self.forty_two),
        ):
            return

        # Fallback : affichage dans le terminal courant
        _draw_grid(self.maze.width, self.maze.height, cell_width,
                   forty_two_cells=self.forty_two,
                   forty_two_color=self.COLOR["42"])
        _animate(tracks or [], self.maze.width, self.maze.height, cell_width,
                 forty_two_cells=self.forty_two,
                 forty_two_color=self.COLOR["42"])
        solution = (
            [(x, y, dirs) for (x, y), dirs in all_paths[0].items()]
            if all_paths
            else []
        )
        _draw_final(
            self.maze.width,
            self.maze.height,
            cell_width,
            self.entry,
            self.exit_pos,
            solution,
            solution_visible=True,
        )
        _run_solution_toggle(
            self.maze.height,
            cell_width,
            solution,
            self.entry,
            self.exit_pos,
        )
