# view/terminal_launcher.py — Détection et lancement de l'émulateur de terminal.
#
# Fonctions :
#   _find_backend()          : détecte le backend installé (priorité XDG)
#   _open_terminal()         : ouvre une fenêtre aux bonnes dimensions
#   _spawn_solution_window() : sérialise la config JSON et ouvre la fenêtre

import json
import os
import subprocess
import sys
import tempfile

from view.terminal_backends import BACKENDS, TerminalBackend
from view.ansi_utils import terminal_cols, terminal_rows


def _find_backend() -> TerminalBackend | None:
    """Returns the first available backend, prioritizing the current desktop.

    Consults XDG_CURRENT_DESKTOP and prefers the native terminal of the desktop
    (GNOME → gnome-terminal, KDE → konsole…), then falls back to the first
    binary found via shutil.which() in the order of BACKENDS.
    """
    import shutil

    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()

    # 1. Native terminal of the current desktop
    for backend in BACKENDS:
        hints = backend.desktop_hints
        if hints and any(h in desktop for h in hints):
            if shutil.which(backend.name):
                return backend

    # 2. First available binary (order of the registry)
    for backend in BACKENDS:
        if shutil.which(backend.name):
            return backend

    return None


def _open_terminal(
    backend: TerminalBackend,
    columns: int,
    rows: int,
    child_args: list[str],
    zoom: float = 0.28,
) -> bool:
    """Opens a terminal window sized to (columns × rows) chars.

    Launches view.terminal_spawn_runner in the child process.
    Returns True if the launch was successful, False otherwise.
    """
    runner_cmd = [
        sys.executable, "-m", "view.terminal_spawn_runner", *child_args
    ]
    args = backend.build_cmd(columns, rows, runner_cmd, zoom)

    try:
        subprocess.Popen(
            args,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        return True
    except FileNotFoundError:
        return False


def _spawn_solution_window(
    maze_width: int,
    maze_height: int,
    tracks: list[tuple[int, int, str]],
    cell_width: int,
    is_perfect: bool,
    # zoom calibrated for Mono 12pt font; increase if too small
    zoom: float = 0.28,
    entry: tuple[int, int] = (0, 0),
    exit_pos: tuple[int, int] = (0, 0),
    solution_cells: list[tuple[int, int]] | None = None,
    forty_two_cells: list[tuple[int, int]] | None = None,
) -> bool:
    """Serializes the config into a temporary JSON file and opens the terminal.

    The file is passed to the runner via --config <path>.
    The runner is responsible for deleting the file after reading.
    """
    backend = _find_backend()
    if not backend:
        return False

    config = {
        "width": maze_width,
        "height": maze_height,
        "cell_width": cell_width,
        "is_perfect": is_perfect,
        "tracks": tracks,
        "entry": list(entry),
        "exit": list(exit_pos),
        "solution": solution_cells or [],
        "forty_two": [list(c) for c in (forty_two_cells or [])],
    }

    # delete=False : the file must survive until the runner reads it
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, prefix="amaze_"
    )
    json.dump(config, tmp)
    tmp.flush()
    tmp.close()

    cols = terminal_cols(maze_width, cell_width)
    rows = terminal_rows(maze_height, cell_width, extra=2)
    success = _open_terminal(backend, cols, rows, ["--config", tmp.name], zoom)
    if not success:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
    return success
