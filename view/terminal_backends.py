# view/terminal_backends.py — Backends d'émulateurs de terminal.
#
# Each TerminalBackend describes:
#   - name          : binary name (used with shutil.which)
#   - desktop_hints : fragments of XDG_CURRENT_DESKTOP to prioritize
#     this backend
#   - build_cmd     : builds the argument list for Popen
#
# To add a new emulator, create a _xxx() function and register it
# in BACKENDS. The rest of the code adapts automatically.

import shlex
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class TerminalBackend:
    """Describes how to detect and launch a terminal emulator."""

    name: str
    desktop_hints: tuple[str, ...]  # fragments XDG_CURRENT_DESKTOP (lowercase)
    build_cmd: Callable[[int, int, list[str], float], list[str]]


# ---------------------------------------------------------------------------
# Command builders by emulator
# ---------------------------------------------------------------------------

def _xterm(cols: int, rows: int, child: list[str], zoom: float) -> list[str]:
    return [
        "xterm", "--fullscreen",
        "-geometry", f"{cols}x{rows}",
        "-fs", str(int(9 * zoom)),
        "-e", *child,
    ]


def _gnome(cols: int, rows: int, child: list[str], zoom: float) -> list[str]:
    return [
        "gnome-terminal", "--window", "--full-screen",
        f"--geometry={cols}x{rows}",
        f"--zoom={zoom}",
        "--", *child,
    ]


def _konsole(cols: int, rows: int, child: list[str], zoom: float) -> list[str]:
    # -p Font= : Qt font description (fixedPitch=1, pointSize from zoom)
    font_pt = max(4, int(9 * zoom))
    font_desc = f"Monospace,{font_pt},-1,5,50,0,0,0,1,0"
    return [
        "konsole",
        "--fullscreen",
        "-p", f"Font={font_desc}",
        "--geometry", f"{cols}x{rows}",
        "-e", " ".join(shlex.quote(a) for a in child),
    ]


def _xfce(cols: int, rows: int, child: list[str], zoom: float) -> list[str]:
    # --zoom=-7 corresponds to ≈28 % of the base size (1.2^-7 ≈ 0.279),
    # which aligns the behavior with gnome-terminal --zoom=0.28.
    return [
        "xfce4-terminal",
        "--fullscreen",
        "--zoom=-7",
        "-e", " ".join(shlex.quote(a) for a in child),
    ]


def _alacritty(
    cols: int, rows: int, child: list[str], zoom: float
) -> list[str]:
    return [
        "alacritty",
        "--option", f"window.dimensions.columns={cols}",
        "--option", f"window.dimensions.lines={rows}",
        "--option", f"font.size={9 * zoom:.1f}",
        "-e", *child,
    ]


def _kitty(cols: int, rows: int, child: list[str], zoom: float) -> list[str]:
    return [
        "kitty",
        "--override", f"initial_window_width={cols}c",
        "--override", f"initial_window_height={rows}c",
        "--override", f"font_size={9 * zoom:.1f}",
        *child,
    ]


# ---------------------------------------------------------------------------
# Registre des backends
# (ordre = priorité lors de la détection générique, sans bureau détecté)
# ---------------------------------------------------------------------------

BACKENDS: list[TerminalBackend] = [
    TerminalBackend("gnome-terminal", ("gnome", "unity"), _gnome),
    TerminalBackend("konsole",        ("kde",),           _konsole),
    TerminalBackend("xfce4-terminal", ("xfce",),          _xfce),
    TerminalBackend("xterm",          (),                  _xterm),
    TerminalBackend("alacritty",      (),                  _alacritty),
    TerminalBackend("kitty",          (),                  _kitty),
]

# Lookup O(1) par nom de binaire
BACKEND_BY_NAME: dict[str, TerminalBackend] = {b.name: b for b in BACKENDS}
