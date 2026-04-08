# view/terminal_view.py
# Affichage terminal du labyrinthe : animation de la génération + solution.

import os
import sys
import termios
import time
import tty
from typing import Any

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
    ("blanc",         Fore.WHITE),
    ("rouge",         Fore.RED),
    ("vert",          Fore.GREEN),
    ("jaune",         Fore.YELLOW),
    ("bleu",          Fore.BLUE),
    ("magenta",       Fore.MAGENTA),
    ("cyan",          Fore.CYAN),
    ("blanc vif",     Fore.LIGHTWHITE_EX),
    ("rouge vif",     Fore.LIGHTRED_EX),
    ("vert vif",      Fore.LIGHTGREEN_EX),
    ("jaune vif",     Fore.LIGHTYELLOW_EX),
    ("bleu vif",      Fore.LIGHTBLUE_EX),
    ("magenta vif",   Fore.LIGHTMAGENTA_EX),
    ("cyan vif",      Fore.LIGHTCYAN_EX),
    ("bleu vif+gras", Fore.LIGHTBLUE_EX + Style.BRIGHT),
    ("vert vif+gras", Fore.LIGHTGREEN_EX + Style.BRIGHT),
    ("rouge vif+gras", Fore.LIGHTRED_EX + Style.BRIGHT),
    ("cyan vif+gras", Fore.LIGHTCYAN_EX + Style.BRIGHT),
]


class TerminalView:

    # Couleurs pour chaque type d'élément affiché.
    # COLOR["42"] est remplacé dynamiquement via [C] dans show_solution.
    COLOR = {
        "wall":   Fore.WHITE,
        "42":     Fore.LIGHTBLUE_EX + Style.BRIGHT,
        "path":   Fore.GREEN,
        "cursor": Fore.GREEN + Style.BRIGHT,
        "entry":  Fore.WHITE,
        "exit":   Fore.RED,
        "info":   Fore.GREEN,
    }
    RESET = Style.RESET_ALL

    def __init__(
        self,
        maze: Maze,
        track: list[Any] | None = None,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] = (0, 0),
        forty_two_cells: set[tuple[int, int]] | None = None,
        path_connections: dict[tuple[int, int], set[str]] | None = None,
    ) -> None:
        self.maze = maze
        self.track = track
        self.entry = entry
        self.exit_pos = exit
        # Cellules appartenant au motif "42" (murs colorés en bleu).
        self.forty_two: set[tuple[int, int]] = set(forty_two_cells or [])
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

    # ------------------------------------------------------------------
    #  ANIMATIONS DE LA GÉNÉRATION
    # ------------------------------------------------------------------

    def play(self, tracks: list[tuple], delay: float = 0.03) -> None:
        """Anime la génération pas à pas.

        Chaque step du track est un tuple (x, y, direction),
        identique pour le backtracker et Kruskal.
        """
        anim = self._anim_maze
        for x, y, direction in tracks:
            os.system("clear")
            anim.remove_wall(x, y, direction)
            self._render(anim, cursor=(x, y))
            time.sleep(delay)

    # ------------------------------------------------------------------
    #  AFFICHAGE INTERACTIF DE LA SOLUTION
    # ------------------------------------------------------------------

    def show_solution(
        self,
        all_paths: list[dict[tuple[int, int], set[str]]],
        is_perfect: bool,
        tracks: list[tuple]
    ) -> None:
        """Affiche le labyrinthe avec le chemin solution, navigation N/P/Q.

        all_paths  : liste de chemins, chacun = dict cellule → directions.
        is_perfect : True si un seul chemin existe (labyrinthe parfait).
        Touches    : [N] chemin suivant, [P] précédent, [Q] quitter.
        """
        current = 0
        total = len(all_paths)
        revealed = False
        color_idx = next(
            i for i, (_, c) in enumerate(COLORS_42)
            if c == self.COLOR["42"]
        ) if self.COLOR["42"] in [c for _, c in COLORS_42] else 0
        self.play(tracks=tracks)
        while True:
            self.path_connections = all_paths[current] if revealed else {}
            os.system("clear")
            self._render(self._anim_maze)
            color_name = COLORS_42[color_idx][0]
            if not revealed:
                print(f"\n  [S] afficher la solution  [C] couleur 42 ({color_name})  [Q] quitter")
            elif is_perfect:
                print(
                    f"\n{self.COLOR['info']}✓ Labyrinthe parfait (chemin unique){self.RESET}"
                )
                print(f"  [S] cacher  [C] couleur 42 ({color_name})  [Q] quitter")
            else:
                print(
                    f"\n{Fore.YELLOW}⚠ Labyrinthe imparfait"
                    f" — chemin {current + 1}/{total}{self.RESET}"
                )
                print(f"  [S] cacher  [C] couleur 42 ({color_name})  [N] suivant  [P] précédent  [Q] quitter")

            key = self._read_key().lower()
            if key == 'q':
                break
            elif key == 's':
                revealed = not revealed
            elif key == 'c':
                color_idx = (color_idx + 1) % len(COLORS_42)
                self.COLOR = {**self.COLOR, "42": COLORS_42[color_idx][1]}
            elif revealed and not is_perfect:
                if key == 'n':
                    current = (current + 1) % total
                elif key == 'p':
                    current = (current - 1) % total

    # ------------------------------------------------------------------
    #  MOTEUR DE RENDU UNIQUE
    #  Utilisé à la fois pendant l'animation et pour l'affichage final.
    # ------------------------------------------------------------------

    def _render(
        self,
        maze: Maze,
        cursor: tuple[int, int] | None = None,
    ) -> None:
        """Dessine le labyrinthe dans le terminal.

        maze   : labyrinthe à dessiner (animation en cours ou final).
        cursor : si fourni, affiche un ● à cette position (animation).

        Chaque rangée produit deux lignes :
          TOP : ╔═══╦═══╗   coins + murs horizontaux
          MID : ║   ║ ● ║   murs verticaux + contenu des cellules
        """
        grid = maze.grid
        width = maze.width
        height = maze.height
        C = self.COLOR
        R = self.RESET

        # ── Présence des murs ────────────────────────────────────────────

        def wall_above(col: int, row: int) -> bool:
            """Vrai s'il y a un mur horizontal entre les rangées row-1 et row.

            Ce mur est encodé soit comme WALL_N de (col, row),
            soit comme WALL_S de (col, row-1) — les deux sont équivalents.
            """
            return (
                (row < height and bool(grid[row][col] & WALL_N))
                or (row > 0 and bool(grid[row - 1][col] & WALL_S))
            )

        def wall_left(col: int, row: int) -> bool:
            """Vrai s'il y a un mur vertical entre les colonnes col-1 et col.

            Encodé soit comme WALL_W de (col, row),
            soit comme WALL_E de (col-1, row).
            """
            return (
                (col < width and bool(grid[row][col] & WALL_W))
                or (col > 0 and bool(grid[row][col - 1] & WALL_E))
            )

        # ── Couleurs des murs (blanc ou bleu si motif 42) ────────────────

        def color_h_wall(col: int, row: int) -> str:
            return C["wall"]

        def color_v_wall(col: int, row: int) -> str:
            return C["wall"]

        def color_corner(
            col: int, row: int, up: bool, down: bool,
            left: bool, right: bool
        ) -> str:
            return C["wall"]

        # ── Contenu d'une cellule (3 caractères) ─────────────────────────

        def cell_content(col: int, row: int) -> str:
            if cursor and (col, row) == cursor:
                return C["cursor"] + " ● " + R
            if (col, row) == self.entry:
                return C["entry"] + "🚀 " + R
            if (col, row) == self.exit_pos:
                return C["exit"] + "🏁 " + R
            if (col, row) in self.forty_two:
                return C["42"] + "███" + R
            if (col, row) in self.path_connections:
                dirs = self.path_connections[(col, row)]
                # Index dans BOX_PATH : W=1, S=2, E=4, N=8
                idx = (
                    (1 if 'W' in dirs else 0)
                    + (2 if 'S' in dirs else 0)
                    + (4 if 'E' in dirs else 0)
                    + (8 if 'N' in dirs else 0)
                )
                seg_left = "─" if 'W' in dirs else " "
                seg_right = "─" if 'E' in dirs else " "
                return C["path"] + seg_left + BOX_PATH[idx] + seg_right + R
            return "   "

        # ── Rendu ligne par ligne ─────────────────────────────────────────

        for row in range(height + 1):

            # Ligne TOP : coins + segments horizontaux
            top_line = ""
            for col in range(width + 1):
                up    = row > 0      and wall_left(col, row - 1)
                down  = row < height and wall_left(col, row)
                left  = col > 0      and wall_above(col - 1, row)
                right = col < width  and wall_above(col, row)

                # Index du coin : gauche=1, bas=2, droite=4, haut=8
                corner_idx = (
                    int(left)
                    + int(down) * 2
                    + int(right) * 4
                    + int(up) * 8
                )
                top_line += (
                    color_corner(col, row, up, down, left, right)
                    + BOX_WALL[corner_idx]
                    + R
                )
                if col < width:
                    top_line += (
                        color_h_wall(col, row) + "═══" + R
                        if wall_above(col, row)
                        else "   "
                    )
            print(top_line)

            # Ligne MID : murs verticaux + contenu des cellules
            if row < height:
                mid_line = ""
                for col in range(width + 1):
                    mid_line += (
                        color_v_wall(col, row) + "║" + R
                        if wall_left(col, row)
                        else " "
                    )
                    if col < width:
                        mid_line += cell_content(col, row)
                print(mid_line)
