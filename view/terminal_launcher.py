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
    """Retourne le premier backend disponible, en priorisant le bureau courant.

    Consulte XDG_CURRENT_DESKTOP et préfère le terminal natif du bureau
    (GNOME → gnome-terminal, KDE → konsole…), puis tombe en fallback sur
    le premier binaire trouvé via shutil.which() dans l'ordre de BACKENDS.
    """
    import shutil

    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()

    # 1. Terminal natif du bureau courant
    for backend in BACKENDS:
        hints = backend.desktop_hints
        if hints and any(h in desktop for h in hints):
            if shutil.which(backend.name):
                return backend

    # 2. Premier binaire disponible (ordre du registre)
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
    """Ouvre une fenêtre de terminal dimensionnée à (columns × rows) chars.

    Lance view.terminal_spawn_runner dans le processus enfant.
    Retourne True si le lancement a réussi, False sinon.
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
    # zoom calibré pour police Mono 12pt ; augmenter si trop petit
    zoom: float = 0.28,
    entry: tuple[int, int] = (0, 0),
    exit_pos: tuple[int, int] = (0, 0),
    solution_cells: list[tuple[int, int]] | None = None,
    forty_two_cells: list[tuple[int, int]] | None = None,
) -> bool:
    """Sérialise la config dans un fichier JSON temporaire et ouvre le terminal.

    Le fichier est passé au runner via --config <path>.
    Le runner est responsable de supprimer le fichier après lecture.
    """
    backend = _find_backend()
    if not backend:
        return False

    config = {
        "width": maze_width,
        "height": maze_height,
        "cell_width": cell_width,
        "tracks": tracks,
        "entry": list(entry),
        "exit": list(exit_pos),
        "solution": solution_cells or [],
        "forty_two": [list(c) for c in (forty_two_cells or [])],
    }

    # delete=False : le fichier doit survivre jusqu'à ce que le runner le lise
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
