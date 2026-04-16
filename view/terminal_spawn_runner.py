"""Runner autonome pour l'animation en terminal séparé.

Ce module est lancé dans une nouvelle fenêtre de terminal via Popen.
Il lit sa configuration depuis un fichier JSON temporaire (--config),
effectue le rendu complet puis gère l'interaction clavier.
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
        description="Runner d'animation en terminal séparé"
    )
    parser.add_argument(
        "--config", metavar="FILE", required=True,
        help="Fichier JSON de configuration (supprimé après lecture)",
    )
    return parser.parse_args()


def _load_config(path: str) -> dict:
    """Lit le fichier JSON de config puis supprime le fichier."""
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
    delay: float = 0.01,
) -> None:
    """Effectue le rendu complet : grille + animation + solution finale."""
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
    _draw_final(w, h, cw, entry, exit_pos, solution_cells,
                solution_visible=True)


def _show_hint(end_row: int) -> None:
    sys.stdout.write(
        f"\033[{end_row};1H\033[2K"
        "  [C] COLORS  [S] SOLUTION  [Q/ENTER] EXIT"
    )
    sys.stdout.flush()


def _run_interaction(cfg: dict, initial_theme_idx: int,
                     solution_cells: list[tuple[int, int, set[str]]],
                     entry: tuple, exit_pos: tuple,) -> None:
    """Boucle d'interaction clavier.

    [C] cycle le thème de couleur et relance le rendu sans délai.
    [Q / Entrée / Échap / Ctrl-C] quitte.
    """
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
                delay=0.0,
            )
            solution_visible = True
            _show_hint(end_row)
        elif key in ("s", "S"):
            if solution_visible:
                _erase_solution(cw, solution_cells, entry, exit_pos)
            else:
                # Redessine chemin + entrée/sortie + barre info
                _draw_final(w, h, cw, entry, exit_pos, solution_cells,
                            solution_visible=True)
                sys.stdout.write("\033[?25l")
                sys.stdout.flush()
                _show_hint(end_row)
            solution_visible = not solution_visible
        elif key in ("\r", "\n", "q", "Q", "\x03", "\x1b"):
            break


def main() -> None:
    args = _parse_args()
    cfg = _load_config(args.config)

    solution_cells = [
        (int(x), int(y), dirs) for x, y, dirs in cfg["solution"]
    ]
    entry = tuple(cfg["entry"])
    exit_pos = tuple(cfg["exit"])

    theme_idx = 0
    _run_render(cfg, COLOR_THEMES[theme_idx], COLOR_THEMES_42[theme_idx])
    _run_interaction(cfg, theme_idx, solution_cells, entry, exit_pos)


if __name__ == "__main__":
    main()
