# view/terminal_view.py
# Affichage terminal du labyrinthe : animation de la génération + solution.

import os
import sys
import termios
import time
import tty
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from colorama import init, Fore, Style
from model.maze import Maze

# colorama : on gère les resets manuellement pour contrôler les couleurs.
init(autoreset=False)

# Bitmask des murs encodés dans grid[row][col].
# Chaque cellule stocke ses murs présents dans un entier 4 bits.
WALL_N = 1  # mur au nord  (haut)
WALL_E = 2  # mur à l'est  (droite)
WALL_S = 4  # mur au sud   (bas)
WALL_W = 8  # mur à l'ouest (gauche)

# Caractères de jonction pour les coins/intersections.
# L'index est un bitmask : gauche=1, bas=2, droite=4, haut=8
# Exemples : index 6 (droite+bas) = coin haut-gauche = ╔
#            index 15 (tout)       = croix centrale  = ╬
BOX_WALL = " ═║╗══╔╦║╝║╣╚╩╠╬"  # double trait (murs du labyrinthe)
BOX_PATH = " ╴╷┐╶─┌┬╵┘│┤└┴├┼"  # simple trait (chemin solution)

# Toutes les couleurs disponibles pour le motif 42 (cycle avec [C]).
COLORS_42 = [
    ("blanc", Fore.WHITE),
    ("rouge", Fore.RED),
    ("vert", Fore.GREEN),
    ("jaune", Fore.YELLOW),
    ("bleu", Fore.BLUE),
    ("magenta", Fore.MAGENTA),
    ("cyan", Fore.CYAN),
    ("blanc vif", Fore.LIGHTWHITE_EX),
    ("rouge vif", Fore.LIGHTRED_EX),
    ("vert vif", Fore.LIGHTGREEN_EX),
    ("jaune vif", Fore.LIGHTYELLOW_EX),
    ("bleu vif", Fore.LIGHTBLUE_EX),
    ("magenta vif", Fore.LIGHTMAGENTA_EX),
    ("cyan vif", Fore.LIGHTCYAN_EX),
    ("bleu vif+gras", Fore.LIGHTBLUE_EX + Style.BRIGHT),
    ("vert vif+gras", Fore.LIGHTGREEN_EX + Style.BRIGHT),
    ("rouge vif+gras", Fore.LIGHTRED_EX + Style.BRIGHT),
    ("cyan vif+gras", Fore.LIGHTCYAN_EX + Style.BRIGHT),
]


class TerminalView:

    # Couleurs pour chaque type d'élément affiché.
    # COLOR["42"] est remplacé dynamiquement via [C] dans show_solution.
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
        track: list[Any] | None = None,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] = (0, 0),
        path_connections: dict[tuple[int, int], set[str]] | None = None,
    ) -> None:
        self.maze = maze
        self.track = track
        self.entry = entry
        self.exit_pos = exit
        # Cellules appartenant au motif "42" (murs colorés en bleu).
        self.forty_two: set[tuple[int, int]] = set(self.maze.forty_two_cells)
        # Chemin solution : cellule → directions de connexion (entrée + sortie).
        # Ex : {(2,3): {'N','S'}} = le chemin entre par le nord, repart au sud.
        self.path_connections: dict[tuple[int, int], set[str]] = (
            path_connections or {}
        )
        # Labyrinthe vierge pour l'animation : murs cassés au fil du track.
        self._anim_maze = Maze(maze.width, maze.height)

    # ------------------------------------------------------------------
    #  LECTURE CLAVIER
    # ------------------------------------------------------------------

    @staticmethod
    def _read_key() -> str:
        """Lit une touche sans attendre Entrée (mode raw)."""
        fd = sys.stdin.fileno()
        saved = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, saved)

    @staticmethod
    def _write_at(screen_row: int, screen_col: int, text: str) -> None:
        """Écrit `text` à une position précise dans le terminal."""
        sys.stdout.write(f"\033[{screen_row};{screen_col}H{text}")

    @staticmethod
    def _screen_coords(x: int, y: int) -> tuple[int, int]:
        """Retourne la position terminal correspondant à la cellule."""
        return 2 + y * 2, 2 + x * 4

    @staticmethod
    def _is_adjacent_step(
        previous_cell: tuple[int, int] | None,
        x: int,
        y: int,
    ) -> bool:
        """Vrai si l'étape courante est visuellement continue."""
        if previous_cell is None:
            return True
        px, py = previous_cell
        return abs(px - x) + abs(py - y) <= 1

    def _cell_content(
        self,
        col: int,
        row: int,
        cursor: tuple[int, int] | None = None,
    ) -> str:
        """Construit le contenu visuel d'une cellule sur 3 caractères."""
        C = self.COLOR
        R = self.RESET

        if cursor and (col, row) == cursor:
            return C["cursor"] + " ● " + R
        if (col, row) == self.entry:
            return C["entry"] + " S " + R
        if (col, row) == self.exit_pos:
            return C["exit"] + " E " + R
        if (col, row) in self.forty_two:
            return C["42"] + "███" + R
        if (col, row) in self.path_connections:
            dirs = self.path_connections[(col, row)]
            idx = (
                (1 if "W" in dirs else 0)
                + (2 if "S" in dirs else 0)
                + (4 if "E" in dirs else 0)
                + (8 if "N" in dirs else 0)
            )
            seg_left = "─" if "W" in dirs else " "
            seg_right = "─" if "E" in dirs else " "
            return C["path"] + seg_left + BOX_PATH[idx] + seg_right + R
        return "   "

    def _draw_cell(
        self,
        x: int,
        y: int,
        cursor: tuple[int, int] | None = None,
    ) -> None:
        """Redessine une seule cellule à sa position écran."""
        screen_row, screen_col = self._screen_coords(x, y)
        self._write_at(
            screen_row, screen_col, self._cell_content(x, y, cursor)
        )

    def _erase_wall_segment(self, x: int, y: int, direction: str) -> None:
        """Efface visuellement le segment de mur supprimé."""
        screen_row, screen_col = self._screen_coords(x, y)

        if direction == "N":
            self._write_at(screen_row - 1, screen_col, "   ")
        elif direction == "S":
            self._write_at(screen_row + 1, screen_col, "   ")
        elif direction == "E":
            self._write_at(screen_row, screen_col + 3, " ")
        elif direction == "W":
            self._write_at(screen_row, screen_col - 1, " ")

    def _redraw_cells(self, cells: set[tuple[int, int]]) -> None:
        """Redessine uniquement les cellules demandées."""
        for x, y in cells:
            self._draw_cell(x, y)

    def _render_status_lines(self, lines: list[str]) -> None:
        """Met à jour la zone d'aide sous le labyrinthe sans tout effacer."""
        base_row = 2 * self.maze.height + 3
        total_rows = max(3, len(lines) + 1)

        for offset in range(total_rows):
            self._write_at(base_row + offset, 1, "\033[K")

        for offset, line in enumerate(lines):
            self._write_at(base_row + offset, 1, f"\033[K{line}")

        self._write_at(base_row + total_rows, 1, "")

    def _build_status_lines(
        self,
        total: int,
        revealed: bool,
        is_perfect: bool,
        current: int,
        color_name: str,
    ) -> list[str]:
        """Construit les lignes d'aide affichées sous le labyrinthe."""
        if total == 0:
            return [
                (
                    f"{Fore.RED}✗ Aucun chemin trouvé entre l'entrée "
                    f"et la sortie.{self.RESET}"
                ),
                f"  [C] couleur 42 ({color_name})  [Q] quitter",
            ]

        if not revealed:
            return [
                (
                    f"  [S] afficher la solution  [C] couleur 42 "
                    f"({color_name})  [Q] quitter"
                )
            ]

        if is_perfect:
            return [
                (
                    f"{self.COLOR['info']}✓ Labyrinthe parfait "
                    f"(chemin unique){self.RESET}"
                ),
                f"  [S] cacher  [C] couleur 42 ({color_name})  [Q] quitter",
            ]

        return [
            (
                f"{Fore.YELLOW}⚠ Labyrinthe imparfait — chemin "
                f"{current + 1}/{total}{self.RESET}"
            ),
            (
                f"  [S] cacher  [C] couleur 42 ({color_name})  "
                f"[N] suivant  [P] précédent  [Q] quitter"
            ),
        ]

    # ------------------------------------------------------------------
    #  ANIMATIONS DE LA GÉNÉRATION
    # ------------------------------------------------------------------

    def play(
        self,
        tracks: list[tuple[int, int, str]] | None = None,
        delay: float = 0.001,
    ) -> None:
        """Anime la génération sans réimprimer tout le labyrinthe.

        Le labyrinthe initial est dessiné une seule fois, puis seules les
        cellules et segments de mur modifiés sont mis à jour par ANSI.
        """
        steps = tracks if tracks is not None else (self.track or [])
        self._anim_maze = Maze(self.maze.width, self.maze.height)
        previous_cell: tuple[int, int] | None = None
        previous_cursor: tuple[int, int] | None = None

        os.system("clear")
        self._render(self._anim_maze)
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        try:
            for x, y, direction in steps:
                self._anim_maze.remove_wall(x, y, direction)
                self._erase_wall_segment(x, y, direction)

                if previous_cursor is not None:
                    self._draw_cell(*previous_cursor)
                    previous_cursor = None

                if self._is_adjacent_step(previous_cell, x, y):
                    self._draw_cell(x, y, cursor=(x, y))
                    previous_cursor = (x, y)

                previous_cell = (x, y)
                sys.stdout.flush()
                time.sleep(delay)

            if previous_cursor is not None:
                self._draw_cell(*previous_cursor)
            self._write_at(2 * self.maze.height + 3, 1, "")
            sys.stdout.flush()
        finally:
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()

    def show_solution(
        self,
        all_paths: list[dict[tuple[int, int], set[str]]],
        is_perfect: bool,
        tracks: list[tuple[int, int, str]] | None = None,
    ) -> None:
        """Affiche le labyrinthe avec le chemin solution.

        Touches : [S] montrer/cacher, [C] couleur 42,
        [N]/[P] navigation, [Q] quitter.
        """
        current = 0
        total = len(all_paths)
        revealed = False
        available_colors = [c for _, c in COLORS_42]
        color_idx = (
            available_colors.index(self.COLOR["42"])
            if self.COLOR["42"] in available_colors
            else 0
        )
        previous_path_cells: set[tuple[int, int]] = set()
        self.path_connections = {}

        def refresh_screen(force_42_refresh: bool = False) -> None:
            nonlocal previous_path_cells
            current_path_cells = set(self.path_connections)
            cells_to_refresh = previous_path_cells | current_path_cells

            if force_42_refresh:
                cells_to_refresh |= self.forty_two

            if cells_to_refresh:
                self._redraw_cells(cells_to_refresh)

            previous_path_cells = current_path_cells
            color_name = COLORS_42[color_idx][0]

            lines = self._build_status_lines(
                total=total,
                revealed=revealed,
                is_perfect=is_perfect,
                current=current,
                color_name=color_name,
            )
            self._render_status_lines(lines)
            sys.stdout.flush()

        self.play(tracks=tracks, delay=0.02)
        refresh_screen(force_42_refresh=True)

        while True:
            key = self._read_key().lower()
            refresh = False
            refresh_42 = False

            if key == "q":
                break
            if key == "c":
                color_idx = (color_idx + 1) % len(COLORS_42)
                self.COLOR = {**self.COLOR, "42": COLORS_42[color_idx][1]}
                refresh = True
                refresh_42 = True
            elif key == "s" and total > 0:
                revealed = not revealed
                refresh = True
            elif revealed and not is_perfect and total > 0:
                if key == "n":
                    current = (current + 1) % total
                    refresh = True
                elif key == "p":
                    current = (current - 1) % total
                    refresh = True

            if refresh:
                self.path_connections = (
                    all_paths[current] if revealed and total > 0 else {}
                )
                refresh_screen(force_42_refresh=refresh_42)

    def _render(
        self,
        maze: Maze,
        cursor: tuple[int, int] | None = None,
    ) -> None:
        """Dessine le labyrinthe dans le terminal."""
        grid = maze.grid
        width = maze.width
        height = maze.height
        C = self.COLOR
        R = self.RESET

        def wall_above(col: int, row: int) -> bool:
            return (row < height and bool(grid[row][col] & WALL_N)) or (
                row > 0 and bool(grid[row - 1][col] & WALL_S)
            )

        def wall_left(col: int, row: int) -> bool:
            return (col < width and bool(grid[row][col] & WALL_W)) or (
                col > 0 and bool(grid[row][col - 1] & WALL_E)
            )

        for row in range(height + 1):
            top_line = ""
            for col in range(width + 1):
                up = row > 0 and wall_left(col, row - 1)
                down = row < height and wall_left(col, row)
                left = col > 0 and wall_above(col - 1, row)
                right = col < width and wall_above(col, row)

                corner_idx = (
                    int(left) + int(down) * 2 + int(right) * 4 + int(up) * 8
                )
                top_line += C["wall"] + BOX_WALL[corner_idx] + R
                if col < width:
                    top_line += (
                        C["wall"] + "═══" + R
                        if wall_above(col, row)
                        else "   "
                    )
            print(top_line)

            if row < height:
                mid_line = ""
                for col in range(width + 1):
                    mid_line += (
                        C["wall"] + "║" + R if wall_left(col, row) else " "
                    )
                    if col < width:
                        mid_line += self._cell_content(col, row, cursor)
                print(mid_line)
