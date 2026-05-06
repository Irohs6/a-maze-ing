# view/ansi_utils.py — ANSI utilities and cell geometry.
#
# This module centralises:
#   - rendering constants (WALL, WALL_WIDTH)
#   - cell geometry calculations (cell_height, grid_cols, grid_rows)
#   - logical coordinate → ANSI position conversions (1-based)
#   - the move_to() helper and the read_key() function

import contextlib
import select as _select
import sys
import termios
import tty
from typing import Iterator

# Representation of a closed wall.
# U+2588 (FULL BLOCK) x 2 -> 2 terminal columns, colorable via ANSI Fore.X
WALL = "██"
WALL_WIDTH = 2  # terminal columns occupied by WALL


# ---------------------------------------------------------------------------
# Cell geometry
# ---------------------------------------------------------------------------

def cell_height(cell_width: int) -> int:
    """Interior height of a cell in terminal rows."""
    return max(1, cell_width // 2)


def grid_cols(maze_width: int, cell_width: int) -> int:
    """Number of logical units (WALL columns) of the grid."""
    return (cell_width + 1) * maze_width + 1


def grid_rows(maze_height: int, cell_width: int) -> int:
    """Nombre de lignes terminales de la grille (hors marges)."""
    return (cell_height(cell_width) + 1) * maze_height + 1


def terminal_cols(maze_width: int, cell_width: int) -> int:
    """Total terminal columns needed for the window."""
    return grid_cols(maze_width, cell_width) * WALL_WIDTH


def terminal_rows(maze_height: int, cell_width: int, extra: int = 2) -> int:
    """Total terminal rows needed, with `extra` margin rows."""
    return grid_rows(maze_height, cell_width) + extra


# ---------------------------------------------------------------------------
# ANSI coordinates (all 1-based, unit = terminal column/row)
# ---------------------------------------------------------------------------

def inner_col(cell_x: int, cell_width: int) -> int:
    """ANSI column of the first interior character (left) of the cell."""
    return (cell_x * (cell_width + 1) + 1) * WALL_WIDTH + 1


def inner_row(cell_y: int, cell_width: int) -> int:
    """ANSI row of the first interior character (top) of the cell."""
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
    """ANSI row of the North wall (horizontal row above the cell)."""
    ch = cell_height(cell_width)
    return 1 + cell_y * (ch + 1)


def wall_row_s(cell_y: int, cell_width: int) -> int:
    """ANSI row of the South wall (horizontal row below the cell)."""
    ch = cell_height(cell_width)
    return 1 + (cell_y + 1) * (ch + 1)


def wall_col_e(cell_x: int, cell_width: int) -> int:
    """Colonne ANSI du mur Est de la cellule."""
    return (cell_x + 1) * (cell_width + 1) * WALL_WIDTH + 1


def wall_col_w(cell_x: int, cell_width: int) -> int:
    """Colonne ANSI du mur Ouest de la cellule."""
    return cell_x * (cell_width + 1) * WALL_WIDTH + 1


def move_to(row: int, col: int) -> str:
    """ANSI CSI sequence to position the cursor (1-based)."""
    return f"\033[{row};{col}H"


# ---------------------------------------------------------------------------
# Lecture de touche (POSIX uniquement)
# ---------------------------------------------------------------------------

def read_key() -> str:
    """Read a key without waiting for Enter (raw mode, POSIX only)."""
    fd = sys.stdin.fileno()
    saved = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)


@contextlib.contextmanager
def raw_stdin() -> Iterator[None]:
    """Context manager: stdin in raw mode, restored on exit.

    Useful for interactive loops calling read_key_or_timeout()
    repeatedly (reduces tcgetattr/tcsetattr calls).
    """
    fd = sys.stdin.fileno()
    saved = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)


def read_key_or_timeout(timeout: float | None) -> str | None:
    """Read a key with timeout (stdin must be in raw mode).

    timeout=None  : blocking until a key is pressed.
    timeout=0.0   : non-blocking, returns None immediately.
    Returns None if the delay expires without a key.
    """
    ready, _, _ = _select.select([sys.stdin], [], [], timeout)
    return sys.stdin.read(1) if ready else None
