# view/ansi_utils.py — Utilitaires ANSI et géométrie de cellule.
#
# Ce module centralise :
#   - les constantes de rendu (WALL, WALL_WIDTH)
#   - les calculs de géométrie de cellule (cell_height, grid_cols, grid_rows)
#   - les conversions coordonnées logiques → positions ANSI (1-based)
#   - le helper move_to() et la fonction read_key()

import contextlib
import select as _select
import sys
import termios
import tty
from typing import Iterator

# Représentation d'un mur fermé.
# U+2588 (FULL BLOCK) × 2 → 2 colonnes terminales, colorable via ANSI Fore.X
WALL = "██"
WALL_WIDTH = 2  # colonnes terminales occupées par WALL


# ---------------------------------------------------------------------------
# Géométrie de cellule
# ---------------------------------------------------------------------------

def cell_height(cell_width: int) -> int:
    """Hauteur intérieure d'une cellule en lignes terminales."""
    return max(1, cell_width // 2)


def grid_cols(maze_width: int, cell_width: int) -> int:
    """Nombre d'unités logiques (colonnes de WALL) de la grille."""
    return (cell_width + 1) * maze_width + 1


def grid_rows(maze_height: int, cell_width: int) -> int:
    """Nombre de lignes terminales de la grille (hors marges)."""
    return (cell_height(cell_width) + 1) * maze_height + 1


def terminal_cols(maze_width: int, cell_width: int) -> int:
    """Colonnes terminales totales nécessaires pour la fenêtre."""
    return grid_cols(maze_width, cell_width) * WALL_WIDTH


def terminal_rows(maze_height: int, cell_width: int, extra: int = 2) -> int:
    """Lignes terminales totales nécessaires, avec `extra` lignes de marge."""
    return grid_rows(maze_height, cell_width) + extra


# ---------------------------------------------------------------------------
# Coordonnées ANSI (toutes 1-based, unité = colonne/ligne terminale)
# ---------------------------------------------------------------------------

def inner_col(cell_x: int, cell_width: int) -> int:
    """Colonne ANSI du premier char intérieur (gauche) de la cellule."""
    return (cell_x * (cell_width + 1) + 1) * WALL_WIDTH + 1


def inner_row(cell_y: int, cell_width: int) -> int:
    """Ligne ANSI du premier char intérieur (haut) de la cellule."""
    ch = cell_height(cell_width)
    return 1 + cell_y * (ch + 1) + 1


def center_col(cell_x: int, cell_width: int) -> int:
    """Colonne ANSI du centre horizontal de la cellule."""
    return inner_col(cell_x, cell_width) + (cell_width * WALL_WIDTH) // 2


def center_row(cell_y: int, cell_width: int) -> int:
    """Ligne ANSI du centre vertical de la cellule."""
    ch = cell_height(cell_width)
    return inner_row(cell_y, cell_width) + (ch - 1) // 2


def wall_row_n(cell_y: int, cell_width: int) -> int:
    """Ligne ANSI du mur Nord (rangée horizontale au-dessus de la cellule)."""
    ch = cell_height(cell_width)
    return 1 + cell_y * (ch + 1)


def wall_row_s(cell_y: int, cell_width: int) -> int:
    """Ligne ANSI du mur Sud (rangée horizontale en-dessous de la cellule)."""
    ch = cell_height(cell_width)
    return 1 + (cell_y + 1) * (ch + 1)


def wall_col_e(cell_x: int, cell_width: int) -> int:
    """Colonne ANSI du mur Est de la cellule."""
    return (cell_x + 1) * (cell_width + 1) * WALL_WIDTH + 1


def wall_col_w(cell_x: int, cell_width: int) -> int:
    """Colonne ANSI du mur Ouest de la cellule."""
    return cell_x * (cell_width + 1) * WALL_WIDTH + 1


def move_to(row: int, col: int) -> str:
    """Séquence ANSI CSI pour positionner le curseur (1-based)."""
    return f"\033[{row};{col}H"


# ---------------------------------------------------------------------------
# Lecture de touche (POSIX uniquement)
# ---------------------------------------------------------------------------

def read_key() -> str:
    """Lit une touche sans attendre Entrée (mode raw, POSIX uniquement)."""
    fd = sys.stdin.fileno()
    saved = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)


@contextlib.contextmanager
def raw_stdin() -> Iterator[None]:
    """Context manager : stdin en mode raw, restauré à la sortie.

    Utile pour les boucles interactives appelant read_key_or_timeout()
    de manière répétitive (réduit les tcgetattr/tcsetattr).
    """
    fd = sys.stdin.fileno()
    saved = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)


def read_key_or_timeout(timeout: float | None) -> str | None:
    """Lit une touche avec délai (stdin doit être en mode raw).

    timeout=None  : bloquant jusqu'à une touche.
    timeout=0.0   : non bloquant, retourne None immédiatement.
    Retourne None si le délai expire sans touche.
    """
    ready, _, _ = _select.select([sys.stdin], [], [], timeout)
    return sys.stdin.read(1) if ready else None
