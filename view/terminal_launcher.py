# view/terminal_launcher.py — Détection et lancement de l'émulateur de terminal.
#
# Fonctions :
#   _find_terminal()         : détecte l'émulateur installé (XDG_CURRENT_DESKTOP)
#   _open_terminal()         : ouvre une nouvelle fenêtre aux bonnes dimensions
#   _spawn_solution_window() : prépare et lance la fenêtre d'animation

import json
import os
import shlex
import shutil
import subprocess
import sys


def _find_terminal() -> str | None:
    """Retourne le nom du premier émulateur de terminal installé sur le système.

    Consulte XDG_CURRENT_DESKTOP pour prioriser le terminal natif du bureau
    en cours (GNOME → gnome-terminal, KDE → konsole, etc.), puis vérifie
    que le binaire est réellement présent via shutil.which().
    """
    desktop_environment = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()

    if "gnome" in desktop_environment or "unity" in desktop_environment:
        candidates = ["gnome-terminal", "xterm"]
    elif "kde" in desktop_environment:
        candidates = ["konsole", "xterm"]
    elif "xfce" in desktop_environment:
        candidates = ["xfce4-terminal", "xterm"]
    else:
        candidates = [
            "xterm",
            "gnome-terminal",
            "konsole",
            "xfce4-terminal",
            "alacritty",
            "kitty",
        ]

    for terminal_name in candidates:
        if shutil.which(terminal_name):
            return terminal_name
    return None


def _open_terminal(
    terminal_name: str,
    columns: int,
    rows: int,
    child_args: list[str] | None = None,
    zoom: float = 0.28,
) -> bool:
    """Ouvre une nouvelle fenêtre de terminal dimensionnée à (columns × rows) chars.

    Lance le module view.terminal_spawn_runner dans le processus enfant.
    Retourne True si le lancement a réussi, False sinon.
    """
    python_executable = sys.executable
    run_args = child_args or []
    runner_cmd = [
        python_executable,
        "-m",
        "view.terminal_spawn_runner",
        *run_args,
    ]

    # xfce4-terminal et konsole interprètent -e comme une string shell.
    shell_command = " ".join(shlex.quote(arg) for arg in runner_cmd)

    launch_args: dict[str, list[str]] = {
        "xterm": [
            "xterm",
            "--fullscreen",
            "-geometry",
            f"{columns}x{rows}",
            "-fs",
            str(int(9 * zoom)),
            "-e",
            *runner_cmd,
        ],
        "gnome-terminal": [
            "gnome-terminal",
            "--window",
            "--full-screen",
            f"--geometry={columns}x{rows}",
            f"--zoom={zoom}",
            "--",
            *runner_cmd,
        ],
        "konsole": [
            "konsole",
            "--geometry",
            f"{columns}x{rows}",
            "-e",
            shell_command,
        ],
        "xfce4-terminal": [
            "xfce4-terminal",
            "--fullscreen",
            "-e",
            shell_command,
        ],
        "alacritty": [
            "alacritty",
            "--option",
            f"window.dimensions.columns={columns}",
            "--option",
            f"window.dimensions.lines={rows}",
            "--option",
            f"font.size={9 * zoom:.1f}",
            "-e",
            *runner_cmd,
        ],
        "kitty": [
            "kitty",
            "--override",
            f"initial_window_width={columns}c",
            "--override",
            f"initial_window_height={rows}c",
            "--override",
            f"font_size={9 * zoom:.1f}",
            *runner_cmd,
        ],
    }

    args = launch_args.get(terminal_name)
    if args is None:
        return False

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
    zoom: float = 0.28,
    entry: tuple[int, int] = (0, 0),
    exit_pos: tuple[int, int] = (0, 0),
    solution_cells: list[list] | None = None,
    forty_two_cells: list[tuple[int, int]] | None = None,
) -> bool:
    """Ouvre un nouveau terminal et lance l'animation dans le processus enfant."""
    terminal_name = _find_terminal()
    if not terminal_name:
        return False

    needed_columns = ((cell_width + 1) * maze_width + 1) * 2
    needed_rows = (max(1, cell_width // 2) + 1) * maze_height + 1 + 2
    tracks_json = json.dumps(tracks, separators=(",", ":"))
    solution_json = json.dumps(solution_cells or [], separators=(",", ":"))
    forty_two_json = json.dumps(list(forty_two_cells or []), separators=(",", ":"))
    child_args = [
        "--width",
        str(maze_width),
        "--height",
        str(maze_height),
        "--cell-width",
        str(cell_width),
        "--tracks-json",
        tracks_json,
        "--entry-x",
        str(entry[0]),
        "--entry-y",
        str(entry[1]),
        "--exit-x",
        str(exit_pos[0]),
        "--exit-y",
        str(exit_pos[1]),
        "--solution-json",
        solution_json,
        "--forty-two-json",
        forty_two_json,
    ]
    return _open_terminal(
        terminal_name, needed_columns, needed_rows, child_args, zoom
    )
