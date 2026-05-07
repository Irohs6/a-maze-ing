# view/terminal_launcher.py — Terminal emulator detection and launch.
#
# Provides:
#   MazeRenderConfig         : dataclass grouping all render parameters
#   _find_backend()          : detect the installed backend (XDG priority)
#   _open_terminal()         : open a window with the correct dimensions
#   _spawn_solution_window() : serialise JSON config and open the window

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field

from view.terminal_backends import BACKENDS, TerminalBackend
from view.ansi_utils import terminal_cols, terminal_rows


@dataclass
class MazeRenderConfig:
    """Groups all parameters needed to render and animate a maze window."""
    width: int
    height: int
    cell_width: int
    is_perfect: bool
    tracks: list[tuple[int, int, str]]
    entry: tuple[int, int]
    exit_pos: tuple[int, int]
    solution_cells: list[tuple[int, int, list[str]]] = field(
        default_factory=list
    )
    forty_two_cells: list[tuple[int, int]] = field(default_factory=list)
    maze_grid: list[list[int]] = field(default_factory=list)


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
    cfg: MazeRenderConfig,
    # zoom calibrated for Mono 12pt font; increase if too small
    zoom: float = 0.28,
) -> bool:
    """Serializes cfg into a temporary JSON file and opens the terminal.

    The file is passed to the runner via --config <path>.
    The runner is responsible for deleting the file after reading.
    """
    backend = _find_backend()
    if not backend:
        return False

    config = {
        "width": cfg.width,
        "height": cfg.height,
        "cell_width": cfg.cell_width,
        "is_perfect": cfg.is_perfect,
        "tracks": cfg.tracks,
        "entry": list(cfg.entry),
        "exit": list(cfg.exit_pos),
        "solution": cfg.solution_cells,
        "forty_two": [list(c) for c in cfg.forty_two_cells],
        "grid": cfg.maze_grid,
    }

    # delete=False : the file must survive until the runner reads it
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, prefix="amaze_"
    )
    json.dump(config, tmp)
    tmp.flush()
    tmp.close()

    cols = terminal_cols(cfg.width, cfg.cell_width)
    rows = terminal_rows(cfg.height, cfg.cell_width, extra=2)
    success = _open_terminal(backend, cols, rows, ["--config", tmp.name], zoom)
    if not success:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
    return success
