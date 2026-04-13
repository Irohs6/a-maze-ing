# view/terminal_renderer.py — Rendu et animation du labyrinthe (block-wall).
#
# Représentation :
#   █ = mur fermé   espace = couloir ouvert ou intérieur de cellule
#   Chaque cellule occupe cell_width × cell_height chars d'espace intérieur.
#   Les murs sont des colonnes/rangées de █ (U+2588) épaisses d'1 char.
#
# Fonctions :
#   _draw_grid()  : affiche la grille initiale (tous murs fermés)
#   _animate()    : anime le perçage des murs en suivant le track
#   _draw_final() : superpose entrée, sortie et chemin solution

import sys
import time

from colorama import Fore, Back, Style

# Caractères de trait simple pour le chemin solution.
# Index = bitmask : W=1, S=2, E=4, N=8
_BOX_PATH = " ╴╷┐╶─┌┬╵┘│┤└┴├┼"

WALL = "██"
WALL_WIDTH = 2  # colonnes terminales occupées par WALL (██ = 2 × U+2588, ANSI-colorable)

# Thèmes de couleur (mur, 42).  Appuyer sur C pour cycler.
# mur   → Fore.X sur ██ (premier plan)
# 42    → Back.X sur espaces (fond) — toujours visuellement distinct
COLOR_THEMES: list[tuple[str, str]] = [Fore.BLUE, Fore.WHITE, Fore.CYAN,
                                       Fore.GREEN, Fore.MAGENTA, Fore.RED,
                                       Fore.LIGHTYELLOW_EX, Fore.WHITE]
COLOR_THEMES_42: list[str] = [Back.YELLOW, Back.MAGENTA, Back.RED,
                               Back.CYAN, Back.YELLOW, Back.GREEN,
                               Back.BLUE, Back.RED]


def _draw_grid(
    maze_width: int,
    maze_height: int,
    cell_width: int,
    wall_color: str = Fore.WHITE,
    forty_two_cells: set[tuple[int, int]] | None = None,
    forty_two_color: str = "",
) -> None:
    """Affiche la grille initiale du labyrinthe (tous murs fermés).

    ⬛⬛⬛⬛⬛
    ⬛  ⬛  ⬛
    ⬛⬛⬛⬛⬛
    ⬛  ⬛  ⬛
    ⬛⬛⬛⬛⬛
    """
    cell_height = max(1, cell_width // 2)
    total_cols = (cell_width + 1) * maze_width + 1
    total_rows = (cell_height + 1) * maze_height + 1

    print("\033c", end="")  # efface l'écran

    for row in range(1, total_rows + 1):
        if row % (cell_height + 1) == 1:
            # Rangée de mur horizontal
            print(wall_color + WALL * total_cols + Style.RESET_ALL)
        else:
            # Rangée de murs verticaux et espaces intérieurs
            # La ligne logique (0-basé) au sein des cellules
            cell_y = (row - 2) // (cell_height + 1)
            line = ""
            for col in range(1, total_cols + 1):
                if col % (cell_width + 1) == 1:
                    line += wall_color + WALL + Style.RESET_ALL
                else:
                    cell_x = (col - 2) // (cell_width + 1)
                    if forty_two_color and (cell_x, cell_y) in (forty_two_cells or set()):
                        line += forty_two_color + " " * WALL_WIDTH + Style.RESET_ALL
                    else:
                        line += " " * WALL_WIDTH
            print(line)


def _animate(
    track: list[tuple[int, int, str]],
    maze_width: int,
    maze_height: int,
    cell_width: int,
    delay: float = 0.001,
    forty_two_cells: set[tuple[int, int]] | None = None,
    forty_two_color: str = "",
) -> None:
    """Anime la génération en effaçant les murs █ pas à pas depuis le track.

    Correspondance coordonnées → position ANSI (séquences 1-based) :
        Première colonne intérieure de la cellule (cx) :
            inner_col = 1 + cx * (cell_width + 1) + 1
        Première ligne intérieure de la cellule (cy) :
            inner_row = 1 + cy * (cell_height + 1) + 1

    Effacement d'un mur selon la direction :
        N → efface la rangée de mur au-dessus de (cx, cy)
        S → efface la rangée de mur en-dessous de (cx, cy)
        E → efface la colonne de mur à droite de (cx, cy)
        W → efface la colonne de mur à gauche de (cx, cy)
    """
    _ft = forty_two_cells or set()
    cell_height = max(1, cell_width // 2)

    sys.stdout.write("\033[?25l")  # masque le curseur terminal
    sys.stdout.flush()

    for cell_x, cell_y, direction in track:
        if delay:
            time.sleep(delay)

        ww = WALL_WIDTH
        # Colonne terminale du 1er char intérieur de la cellule
        inner_col = (cell_x * (cell_width + 1) + 1) * ww + 1
        inner_row = 1 + cell_y * (cell_height + 1) + 1

        if direction == "N":
            wall_row = 1 + cell_y * (cell_height + 1)
            sys.stdout.write(
                f"\033[{wall_row};{inner_col}H{' ' * (cell_width * ww)}"
            )
        elif direction == "S":
            wall_row = 1 + (cell_y + 1) * (cell_height + 1)
            sys.stdout.write(
                f"\033[{wall_row};{inner_col}H{' ' * (cell_width * ww)}"
            )
        elif direction == "E":
            wall_col = (cell_x + 1) * (cell_width + 1) * ww + 1
            for r in range(cell_height):
                sys.stdout.write(f"\033[{inner_row + r};{wall_col}H{' ' * ww}")
        elif direction == "W":
            wall_col = cell_x * (cell_width + 1) * ww + 1
            for r in range(cell_height):
                sys.stdout.write(f"\033[{inner_row + r};{wall_col}H{' ' * ww}")

        # Curseur vert au centre de la cellule
        cursor_col = inner_col + (cell_width * ww) // 2
        cursor_row = inner_row + (cell_height - 1) // 2
        sys.stdout.write(
            f"\033[{cursor_row};{cursor_col}H{Fore.GREEN}●{Style.RESET_ALL}"
        )
        sys.stdout.flush()

        # Restauration : espace ou fond 42
        if (cell_x, cell_y) in _ft and forty_two_color:
            ww_inner = cell_width * ww
            sys.stdout.write(
                f"\033[{inner_row};{inner_col}H"
                f"{forty_two_color}{' ' * ww_inner}{Style.RESET_ALL}"
            )
            sys.stdout.flush()
        else:
            sys.stdout.write(f"\033[{cursor_row};{cursor_col}H ")

    sys.stdout.write(f"\033[{(cell_height + 1) * maze_height + 2};1H")
    sys.stdout.write("\033[?25h")  # restaure le curseur terminal
    sys.stdout.flush()


def _draw_final(
    maze_width: int,
    maze_height: int,
    cell_width: int,
    entry: tuple[int, int],
    exit_pos: tuple[int, int],
    solution_cells: list[tuple[int, int, set[str]]],
    forty_two_cells: set[tuple[int, int]] | None = None,
    forty_two_color: str = Back.YELLOW,
) -> None:
    """Superpose entrée, sortie et chemin solution sur la grille finale.

    À appeler après _animate(). Ne bloque pas (pas d'input).
    """
    cell_height = max(1, cell_width // 2)
    ww = WALL_WIDTH

    def _center_col(x: int) -> int:
        return (x * (cell_width + 1) + 1) * ww + 1 + (cell_width * ww) // 2

    def _center_row(y: int) -> int:
        return 1 + y * (cell_height + 1) + 1 + (cell_height - 1) // 2

    # Cellules "42" — fond coloré sur espaces (visuellement distinct des murs ██)
    ww_inner = cell_width * ww
    for fx, fy in forty_two_cells or set():
        inner_col = (fx * (cell_width + 1) + 1) * ww + 1
        sys.stdout.write(
            f"\033[{_center_row(fy)};{inner_col}H"
            f"{forty_two_color}{' ' * ww_inner}{Style.RESET_ALL}"
        )

    # Chemin solution en jaune avec traits directionnels
    for sol_x, sol_y, dirs in solution_cells:
        if (sol_x, sol_y) == entry or (sol_x, sol_y) == exit_pos:
            continue
        idx = (
            (1 if "W" in dirs else 0)
            + (2 if "S" in dirs else 0)
            + (4 if "E" in dirs else 0)
            + (8 if "N" in dirs else 0)
        )
        char = _BOX_PATH[idx]
        sys.stdout.write(
            f"\033[{_center_row(sol_y)};{_center_col(sol_x)}H"
            f"{Fore.YELLOW}{char}{Style.RESET_ALL}"
        )

    # Marqueur entrée (vert S)
    ex, ey = entry
    sys.stdout.write(
        f"\033[{_center_row(ey)};{_center_col(ex)}H{Fore.GREEN}S{Style.RESET_ALL}"
    )

    # Marqueur sortie (rouge E)
    xx, xy = exit_pos
    sys.stdout.write(
        f"\033[{_center_row(xy)};{_center_col(xx)}H{Fore.RED}E{Style.RESET_ALL}"
    )

    sys.stdout.write(f"\033[{(cell_height + 1) * maze_height + 2};1H")
    sys.stdout.flush()
