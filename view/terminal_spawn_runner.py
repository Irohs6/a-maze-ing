"""Autonomous runner for separate terminal animation.

This module is launched in a new terminal window via Popen.
It reads its configuration from a temporary JSON file (--config),
performs the complete rendering, and then handles keyboard interaction.
"""

import argparse
import json
import os
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from view.terminal_renderer import (
    _draw_grid, _animate, _draw_final, _erase_solution,
    COLOR_THEMES, COLOR_THEMES_42
)
from view import ansi_utils


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Separate terminal animation runner"
    )
    parser.add_argument(
        "--config", metavar="FILE", required=True,
        help="JSON configuration file (deleted after reading)",
    )
    return parser.parse_args()


def _load_config(path: str) -> dict[str, any]:
    """Reads the JSON config file and then deletes the file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    try:
        os.unlink(path)
    except OSError:
        pass
    return data


def _run_render(
    cfg: dict,
    wall_color: str,
    forty_two_color: str,
    perfect: bool,
    delay: float = 0.01,
) -> None:
    """Performs the complete rendering: grid + animation + final solution."""

    tracks = [(int(x), int(y), d) for x, y, d in cfg["tracks"]]
    solution_cells = [
        (int(x), int(y), dirs) for x, y, dirs in cfg["solution"]
    ]
    forty_two_cells: set[tuple[int, int]] = {
        (int(x), int(y)) for x, y in cfg["forty_two"]
    }
    entry = tuple(cfg["entry"])
    exit_pos = tuple(cfg["exit"])
    w, h, cw = cfg["width"], cfg["height"], cfg["cell_width"]

    _draw_grid(w, h, cw, wall_color=wall_color,
               forty_two_cells=forty_two_cells, forty_two_color=forty_two_color)
    _animate(tracks, w, h, cw, delay=delay,
             forty_two_cells=forty_two_cells, forty_two_color=forty_two_color)
    _draw_final(w, h, cw, entry, exit_pos, solution_cells, perfect,
                solution_visible=True)


def _show_hint(end_row: int) -> None:
    sys.stdout.write(
        f"\033[{end_row};1H\033[2K"
        "  [C] COLORS  [S] SOLUTION  [Q/ENTER] EXIT"
    )
    sys.stdout.flush()


def _run_interaction(cfg: dict[str, any], initial_theme_idx: int,
                     solution_cells: list[tuple[int, int, set[str]]],
                     entry: tuple, exit_pos: tuple,) -> None:
    """Keyboard interaction loop.

    [C] cycles the color theme and reruns the rendering without delay.
    [Q / Enter / Esc / Ctrl-C] exits.
    """
    perfect = cfg["is_perfect"]
    theme_idx = initial_theme_idx % len(COLOR_THEMES)
    theme_idx_42 = initial_theme_idx % len(COLOR_THEMES_42)
    w, h, cw = cfg["width"], cfg["height"], cfg["cell_width"]
    end_row = ansi_utils.grid_rows(h, cw) + 1
    solution_visible = True
    _show_hint(end_row)

    while True:
        key = ansi_utils.read_key()
        if key.lower() == "c":
            theme_idx = (theme_idx + 1) % len(COLOR_THEMES)
            theme_idx_42 = (theme_idx_42 + 1) % len(COLOR_THEMES_42)
            _run_render(
                cfg,
                COLOR_THEMES[theme_idx],
                COLOR_THEMES_42[theme_idx_42],
                perfect,
                delay=0.0,
            )
            solution_visible = True
            _show_hint(end_row)
        elif key in ("s", "S"):
            if solution_visible:
                _erase_solution(cw, solution_cells, entry, exit_pos)
            else:
                # Redraw path + entry/exit + info bar
                _draw_final(w, h, cw, entry, exit_pos, solution_cells, perfect,
                            solution_visible=True)
                sys.stdout.write("\033[?25l")
                sys.stdout.flush()
                _show_hint(end_row)
            solution_visible = not solution_visible
        elif key in ("\r", "\n", "q", "Q", "\x03", "\x1b"):
            break


def main() -> None:
    try:
        try:
            args = _parse_args()
            cfg = _load_config(args.config)
        except Exception:
            import traceback
            print("[ERROR] Exception while loading config or arguments:",
                  file=sys.stderr)
            traceback.print_exc()
            input("Press Enter to exit...")
            return

        solution_cells = [
            (int(x), int(y), dirs) for x, y, dirs in cfg["solution"]
        ]
        entry = tuple(cfg["entry"])
        exit_pos = tuple(cfg["exit"])

        theme_idx = 0
        _run_render(cfg, COLOR_THEMES[theme_idx], COLOR_THEMES_42[theme_idx],
                    cfg["is_perfect"])
        _run_interaction(cfg, theme_idx, solution_cells, entry, exit_pos)
    except Exception:
        import traceback
        print("[ERROR] Exception during main execution:", file=sys.stderr)
        traceback.print_exc()
        input("Press Enter to exit...")
        return


if __name__ == "__main__":
    main()
