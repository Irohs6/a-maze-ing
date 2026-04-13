"""Spawn runner for the terminal eighth-block animation.

This module is executed in a newly opened terminal window.
It is intentionally separate from terminal_view's __main__ flow so
project runtime does not depend on that block.
"""

import argparse
import json
import sys
import termios
import tty

from view.terminal_renderer import _draw_grid, _animate, _draw_final, COLOR_THEMES, COLOR_THEMES_42


def _read_key() -> str:
    """Lit une touche sans attendre Entrée (mode raw)."""
    fd = sys.stdin.fileno()
    saved = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run spawned terminal animation")
    parser.add_argument('--width', type=int, required=True)
    parser.add_argument('--height', type=int, required=True)
    parser.add_argument('--cell-width', type=int, default=2)
    parser.add_argument('--tracks-json', type=str, required=True)
    parser.add_argument('--entry-x', type=int, default=0)
    parser.add_argument('--entry-y', type=int, default=0)
    parser.add_argument('--exit-x', type=int, default=0)
    parser.add_argument('--exit-y', type=int, default=0)
    parser.add_argument('--solution-json', type=str, default='[]')
    parser.add_argument('--forty-two-json', type=str, default='[]')
    parser.add_argument('--color-theme-idx', type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    tracks = [(int(x), int(y), str(d)) for x, y, d in json.loads(args.tracks_json)]
    solution_cells = [(int(x), int(y), set(dirs)) for x, y, dirs in json.loads(args.solution_json)]
    forty_two_cells: set[tuple[int, int]] = {
        (int(x), int(y)) for x, y in json.loads(args.forty_two_json)
    }
    entry = (args.entry_x, args.entry_y)
    exit_pos = (args.exit_x, args.exit_y)

    theme_idx = args.color_theme_idx % len(COLOR_THEMES)
    theme_idx_42 = args.color_theme_idx % len(COLOR_THEMES_42)
    wall_color = COLOR_THEMES[theme_idx]
    forty_two_color = COLOR_THEMES_42[theme_idx_42]

    _draw_grid(args.width, args.height, args.cell_width, wall_color=wall_color,
               forty_two_cells=forty_two_cells, forty_two_color=forty_two_color)
    _animate(tracks, args.width, args.height, args.cell_width,
             forty_two_cells=forty_two_cells, forty_two_color=forty_two_color)
    _draw_final(
        args.width, args.height, args.cell_width,
        entry, exit_pos, solution_cells,
        forty_two_cells=forty_two_cells,
        forty_two_color=forty_two_color,
    )

    sys.stdout.write("  [C] couleurs  [Q/Entrée] quitter")
    sys.stdout.flush()

    while True:
        key = _read_key()
        if key.lower() == 'c':
            theme_idx = (theme_idx + 1) % len(COLOR_THEMES)
            theme_idx_42 = (theme_idx_42 + 1) % len(COLOR_THEMES_42)
            wall_color = COLOR_THEMES[theme_idx]
            forty_two_color = COLOR_THEMES_42[theme_idx_42]
            _draw_grid(args.width, args.height, args.cell_width, wall_color=wall_color,
                       forty_two_cells=forty_two_cells, forty_two_color=forty_two_color)
            _animate(tracks, args.width, args.height, args.cell_width, delay=0.0,
                     forty_two_cells=forty_two_cells, forty_two_color=forty_two_color)
            _draw_final(
                args.width, args.height, args.cell_width,
                entry, exit_pos, solution_cells,
                forty_two_cells=forty_two_cells,
                forty_two_color=forty_two_color,
            )
            sys.stdout.write("  [C] couleurs  [Q/Entrée] quitter")
            sys.stdout.flush()
        elif key in ('\r', '\n', 'q', 'Q', '\x03', '\x1b'):
            break


if __name__ == '__main__':
    main()
