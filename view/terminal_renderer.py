# view/terminal_renderer.py — Rendu et animation du labyrinthe (block-wall).
#
# Représentation :
#   █ = mur fermé   espace = couloir ouvert ou intérieur de cellule
#   Chaque cellule occupe cell_width × cell_height chars d'espace intérieur.
#   Les murs sont des colonnes/rangées de █ (U+2588) épaisses d'1 char.
#
# Fonctions publiques :
#   _draw_grid()  : affiche la grille initiale (tous murs fermés) — 1 flush
#   _animate()    : anime le perçage des murs — 1 flush/cellule ou 1 flush total
#   _draw_final() : superpose entrée, sortie et chemin solution — 1 flush

import sys
import time

from colorama import Fore, Back, Style

from view.ansi_utils import (
    WALL, WALL_WIDTH,
    cell_height, grid_cols, grid_rows,
    inner_col, inner_row, center_col, center_row,
    wall_row_n, wall_row_s, wall_col_e, wall_col_w,
    raw_stdin, read_key_or_timeout,
)

# Caractères de trait simple pour le chemin solution.
# Index = bitmask : W=1, S=2, E=4, N=8
_BOX_PATH = " ╴╷┐╶─┌┬╵┘│┤└┴├┼"

# Thèmes de couleur (mur, 42).  Appuyer sur C pour cycler.
# mur   → Fore.X sur ██ (premier plan)
# 42    → Back.X sur espaces (fond) — toujours visuellement distinct
COLOR_THEMES: list[str] = [
    Fore.BLUE, Fore.WHITE, Fore.CYAN,
    Fore.GREEN, Fore.MAGENTA, Fore.RED,
    Fore.LIGHTYELLOW_EX, Fore.WHITE,
]
COLOR_THEMES_42: list[str] = [
    Back.YELLOW, Back.MAGENTA, Back.RED,
    Back.CYAN, Back.YELLOW, Back.GREEN,
    Back.BLUE, Back.RED,
]

# Niveaux de vitesse d'animation : (délai en s, label affiché).
# [+] → plus rapide (index plus bas), [-] → plus lent (index plus haut)
_SPEED_LEVELS: list[tuple[float, str]] = [
    (0.2,    "1"),   # très lent
    (0.05,   "2"),
    (0.01,   "3"),
    (0.001,  "4"),   # vitesse par défaut
    (0.0003, "5"),
    (0.0,    "6"),   # instantané (MAX)
]
_DEFAULT_SPEED_IDX: int = 3


def _build_cell_buf(
    cell_x: int,
    cell_y: int,
    direction: str,
    cell_width: int,
    ft: set[tuple[int, int]],
    forty_two_color: str,
    pending_restore: str,
) -> tuple[list[str], str]:
    """Construit le buffer ANSI pour un pas d'animation.

    Retourne (cell_buf, nouveau_pending_restore).
    """
    ch = cell_height(cell_width)
    ww = WALL_WIDTH
    ww_inner = cell_width * ww
    ic = inner_col(cell_x, cell_width)
    ir = inner_row(cell_y, cell_width)
    cc = center_col(cell_x, cell_width)
    cr = center_row(cell_y, cell_width)

    buf: list[str] = [pending_restore] if pending_restore else []

    if direction == "N":
        wr = wall_row_n(cell_y, cell_width)
        buf.append(f"\033[{wr};{ic}H{' ' * ww_inner}")
    elif direction == "S":
        wr = wall_row_s(cell_y, cell_width)
        buf.append(f"\033[{wr};{ic}H{' ' * ww_inner}")
    elif direction == "E":
        wc = wall_col_e(cell_x, cell_width)
        for r in range(ch):
            buf.append(f"\033[{ir + r};{wc}H{' ' * ww}")
    elif direction == "W":
        wc = wall_col_w(cell_x, cell_width)
        for r in range(ch):
            buf.append(f"\033[{ir + r};{wc}H{' ' * ww}")

    buf.append(f"\033[{cr};{cc}H{Fore.GREEN}\u25cf{Style.RESET_ALL}")

    if (cell_x, cell_y) in ft and forty_two_color:
        restore = (
            f"\033[{ir};{ic}H"
            f"{forty_two_color}{' ' * ww_inner}{Style.RESET_ALL}"
        )
    else:
        restore = f"\033[{cr};{cc}H "

    return buf, restore


def _draw_grid(
    maze_width: int,
    maze_height: int,
    cell_width: int,
    wall_color: str = Fore.WHITE,
    forty_two_cells: set[tuple[int, int]] | None = None,
    forty_two_color: str = "",
) -> None:
    """Affiche la grille initiale du labyrinthe (tous murs fermés).

    Tous les caractères sont accumulés dans un buffer puis envoyés en
    un seul write + flush (évite O(lignes) flush implicites via print).
    """
    ch = cell_height(cell_width)
    total_cols = grid_cols(maze_width, cell_width)
    total_rows = grid_rows(maze_height, cell_width)
    ft = forty_two_cells or set()

    buf: list[str] = ["\033c"]  # efface l'écran
    for row in range(1, total_rows + 1):
        if row % (ch + 1) == 1:
            # Rangée de mur horizontal
            buf.append(wall_color + WALL * total_cols + Style.RESET_ALL + "\n")
        else:
            # Rangée de murs verticaux et espaces intérieurs
            cell_y = (row - 2) // (ch + 1)
            parts: list[str] = []
            for col in range(1, total_cols + 1):
                if col % (cell_width + 1) == 1:
                    parts.append(wall_color + WALL + Style.RESET_ALL)
                else:
                    cell_x = (col - 2) // (cell_width + 1)
                    if forty_two_color and (cell_x, cell_y) in ft:
                        parts.append(
                            forty_two_color
                            + " " * WALL_WIDTH
                            + Style.RESET_ALL
                        )
                    else:
                        parts.append(" " * WALL_WIDTH)
            buf.append("".join(parts) + "\n")

    sys.stdout.write("".join(buf))
    sys.stdout.flush()


def _animate(
    track: list[tuple[int, int, str]],
    maze_width: int,
    maze_height: int,
    cell_width: int,
    delay: float = 0.001,
    forty_two_cells: set[tuple[int, int]] | None = None,
    forty_two_color: str = "",
    interactive: bool = True,
) -> None:
    """Anime la génération en effaçant les murs █ pas à pas.

    Stratégie de flush :
      delay > 0, interactif  : 1 flush/cellule ; contrôles clavier actifs.
      delay > 0, passif      : 1 flush/cellule, time.sleep(delay).
      delay = 0 (replay)     : 1 flush total en fin de boucle.

    Contrôles (mode interactif, stdin est un tty) :
      Espace  : pause / play
      N       : avancer d'un pas (si en pause)
      +       : vitesse plus rapide
      -       : vitesse plus lente
    """
    ft = forty_two_cells or set()
    is_interactive = (
        interactive and delay > 0 and sys.stdin.isatty()
    )
    end_row = grid_rows(maze_height, cell_width) + 1
    pending_restore = ""

    sys.stdout.write("\033[?25l")  # masque le curseur
    sys.stdout.flush()

    if is_interactive:
        speed_idx = _DEFAULT_SPEED_IDX
        paused = False

        def _status() -> str:
            lbl = _SPEED_LEVELS[speed_idx][1]
            if paused:
                return (
                    f"\033[{end_row};1H\033[2K"
                    f"⏸  [Espace] ▶  [N] étape  "
                    f"[+/-] vitesse: {lbl}"
                )
            return (
                f"\033[{end_row};1H\033[2K"
                f"▶  [Espace] ⏸  [+/-] vitesse: {lbl}"
            )

        with raw_stdin():
            sys.stdout.write(_status())
            sys.stdout.flush()

            idx = 0
            while idx < len(track):
                cell_x, cell_y, direction = track[idx]
                d = _SPEED_LEVELS[speed_idx][0]
                key = read_key_or_timeout(
                    None if paused else d
                )

                advance = False
                redraw = False
                if key == " ":
                    paused = not paused
                    redraw = True
                    advance = not paused
                elif key in ("+", "="):
                    speed_idx = max(0, speed_idx - 1)
                    redraw = True
                    advance = not paused
                elif key == "-":
                    n = len(_SPEED_LEVELS) - 1
                    speed_idx = min(n, speed_idx + 1)
                    redraw = True
                    advance = not paused
                elif key in ("n", "N") and paused:
                    advance = True
                elif key in ("\x03", "\x1b"):
                    break
                elif key is None:
                    advance = True  # timeout → pas normal

                if redraw:
                    sys.stdout.write(_status())
                if not advance:
                    sys.stdout.flush()
                    continue

                cell_buf, pending_restore = _build_cell_buf(
                    cell_x, cell_y, direction, cell_width,
                    ft, forty_two_color, pending_restore,
                )
                sys.stdout.write("".join(cell_buf))
                sys.stdout.flush()
                idx += 1

        # Efface la barre de statut, restaure la visibilité du curseur
        sys.stdout.write(
            f"{pending_restore}"
            f"\033[{end_row};1H\033[2K"
            f"\033[?25h"
        )
        sys.stdout.flush()
        return

    # --- Mode passif (delay=0 ou stdin pas tty) ---
    buf_replay: list[str] = []
    flush_per_cell = delay > 0

    for cell_x, cell_y, direction in track:
        if delay:
            time.sleep(delay)

        cell_buf, pending_restore = _build_cell_buf(
            cell_x, cell_y, direction, cell_width,
            ft, forty_two_color, pending_restore,
        )

        if flush_per_cell:
            sys.stdout.write("".join(cell_buf))
            sys.stdout.flush()
        else:
            buf_replay.extend(cell_buf)

    # Fin de boucle : restauration + repositionnement
    end_seq = f"{pending_restore}\033[{end_row};1H\033[?25h"
    if flush_per_cell:
        sys.stdout.write(end_seq)
        sys.stdout.flush()
    else:
        buf_replay.append(end_seq)
        sys.stdout.write("".join(buf_replay))
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

    À appeler après _animate(). Accumule tous les writes en un buffer
    puis effectue un unique flush.
    """
    ww_inner = cell_width * WALL_WIDTH
    end_row = grid_rows(maze_height, cell_width) + 1
    buf: list[str] = []

    # Cellules "42" — fond coloré sur espaces intérieurs
    for fx, fy in forty_two_cells or set():
        ic = inner_col(fx, cell_width)
        buf.append(
            f"\033[{center_row(fy, cell_width)};{ic}H"
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
        cr = center_row(sol_y, cell_width)
        cc = center_col(sol_x, cell_width)
        buf.append(
            f"\033[{cr};{cc}H"
            f"{Fore.YELLOW}{_BOX_PATH[idx]}{Style.RESET_ALL}"
        )

    # Marqueur entrée (vert S)
    ex, ey = entry
    buf.append(
        f"\033[{center_row(ey, cell_width)};{center_col(ex, cell_width)}H"
        f"{Fore.GREEN}S{Style.RESET_ALL}"
    )

    # Marqueur sortie (rouge E)
    xx, xy = exit_pos
    buf.append(
        f"\033[{center_row(xy, cell_width)};{center_col(xx, cell_width)}H"
        f"{Fore.RED}E{Style.RESET_ALL}"
    )

    buf.append(f"\033[{end_row};1H")
    sys.stdout.write("".join(buf))
    sys.stdout.flush()
