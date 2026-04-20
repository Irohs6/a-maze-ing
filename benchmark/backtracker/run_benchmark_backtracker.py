#!/usr/bin/env python3
#
# benchmark/backtracker/run_benchmark_backtracker.py
#
# Benchmark de l'algorithme Backtracker (A-Maze-ing).
#

# Mesure pour chaque taille de labyrinthe :
#   - Temps de génération moyen / min / max
#   - Taux de succès (sur N seeds)
#   - Nombre de cellules visitées et de murs ouverts
#   - Longueur du track (nombre de passages creusés)
#   - Vérification MazeValidator


import sys
import time
import random
import csv
import argparse
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any

# --- Chemin vers la racine du projet ---
from mazegen.backtracker import Backtracker
from model.maze import Maze
from model.maze_validator import MazeValidator

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# Configuration
# =============================================================================

DEFAULT_SIZES = [
    (5,    5),
    (11,   9),    # taille minimale avec motif 42
    (11,  11),
    (21,  21),
    (31,  31),
    (51,  51),
    (71,  71),
    (101, 101),
    (151, 151),
    (201, 201),
    (301, 301),
    (501, 501),
]

DEFAULT_SEEDS_PER_SIZE = 10


# =============================================================================
# Benchmark d'une configuration (w × h, seed)
# =============================================================================

def bench_one(width: int, height: int, seed: int) -> dict[str, Any]:
    """Génère un labyrinthe Backtracker et mesure les métriques."""
    maze = Maze(width, height)
    algo = Backtracker(maze, is_perfect=True)

    success = False
    valid = False
    track_len = 0
    walls_opened = 0
    visited_cells = 0
    error_msg = ""
    elapsed = 0.0

    try:
        random.seed(seed)
        t0 = time.perf_counter()
        track = algo.generate()
        elapsed = time.perf_counter() - t0

        success = True
        track_len = len(track)
        final_maze = algo.maze

        # Cellules visitées = toutes les cellules non-42 (DFS visite tout)
        visited_cells = sum(
            1
            for y in range(height)
            for x in range(width)
            if (x, y) not in final_maze.forty_two_cells
        )

        # Murs ouverts : chaque cellule non-42 avec au moins un passage
        walls_opened = sum(
            bin(~final_maze.grid[y][x] & 0xF).count('1')
            for y in range(height)
            for x in range(width)
            if final_maze.grid[y][x] != 15
        ) // 2  # chaque mur compté des deux côtés

        validator = MazeValidator(final_maze)
        valid = validator.validate()

    except Exception as e:
        elapsed = time.perf_counter() - \
                  t0 if 'elapsed' not in dir() else elapsed
        error_msg = f"{type(e).__name__}: {str(e)[:80]}"

    return {
        "width": width,
        "height": height,
        "cells": width * height,
        "seed": seed,
        "success": success,
        "valid": valid,
        "elapsed_s": round(elapsed, 7),
        "track_len": track_len,
        "visited_cells": visited_cells,
        "walls_opened": walls_opened,
        "error": error_msg,
    }


# =============================================================================
# Agrégation
# =============================================================================

def aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [r for r in results if r["success"]]
    n = len(results)

    times = [r["elapsed_s"] for r in ok]
    tracks = [r["track_len"] for r in ok]
    visited = [r["visited_cells"] for r in ok]
    valids = [r for r in ok if r["valid"]]

    def avg(lst: list[float]) -> float | None:
        return round(statistics.mean(lst), 7) if lst else None

    def st(lst: list[float]) -> float:
        return round(statistics.stdev(lst), 7) if len(lst) > 1 else 0.0

    return {
        "n_runs":           n,
        "n_success":        len(ok),
        "n_valid":          len(valids),
        "n_failure":        n - len(ok),
        "success_rate":     round(len(ok) / n * 100, 1) if n else 0,
        "time_mean":        avg(times),
        "time_min":         round(min(times), 7) if times else None,
        "time_max":         round(max(times), 7) if times else None,
        "time_stdev":       st(times),
        "track_mean":       avg(tracks),
        "visited_mean":     avg(visited),
    }


# =============================================================================
# Affichage terminal
# =============================================================================

HEADER = (
    f"{'Size':>9} | {'Runs':>4} | {'Succ':>4} | {'Valid':>5} | "
    f"{'Mean(s)':>9} | {'Min(s)':>9} | {'Max(s)':>9} | {'StdDev':>9} | "
    f"{'TrackAvg':>8} | {'Visited':>7}"
)
SEP = "-" * len(HEADER)


def fmt_row(w: int, h: int, agg: dict[str, Any]) -> str:
    size = f"{w}x{h}"
    if agg['time_mean'] is not None:
        mean = f"{agg['time_mean']:.5f}"
    else:
        mean = "     FAIL"
    if agg['time_min'] is not None:
        mn = f"{agg['time_min']:.5f}"
    else:
        mn = "     FAIL"
    if agg['time_max'] is not None:
        mx = f"{agg['time_max']:.5f}"
    else:
        mx = "     FAIL"
    if agg['time_mean'] is not None:
        sd = f"{agg['time_stdev']:.5f}"
    else:
        sd = "     FAIL"
    if agg['track_mean'] is not None:
        trk = f"{agg['track_mean']:.0f}"
    else:
        trk = "       -"
    if agg['visited_mean'] is not None:
        vis = f"{agg['visited_mean']:.0f}"
    else:
        vis = "      -"
    return (
        f"{size:>9} | {agg['n_runs']:>4} | {agg['n_success']:>4} | "
        f"{agg['n_valid']:>5} | {mean:>9} | {mn:>9} | {mx:>9} | "
        f"{sd:>9} | {trk:>8} | {vis:>7}"
    )


# =============================================================================
# Export CSV + Markdown
# =============================================================================

def export_csv(all_raw: list[dict[str, Any]], path: Path) -> None:
    if not all_raw:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_raw[0].keys()))
        writer.writeheader()
        writer.writerows(all_raw)
    print(f"\n[CSV] {path}")


def export_markdown(
    summary_rows: list[tuple[int, int, dict[str, Any]]],
    path: Path,
    n_seeds: int,
    max_size: int,
    total_elapsed: float,
) -> None:
    lines = [
        "# Benchmark Backtracker — A-Maze-ing",
        "",
        f"> Généré le {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        (
            f"> Seeds par taille : **{n_seeds}** | Taille max : "
            f"**{max_size}×{max_size}**"
        ),
        f"> Durée totale du benchmark : **{total_elapsed:.2f}s**",
        "",
        "## Résultats par taille",
        "",
        "| Taille | Runs | Succès | Valides | Moy(s) | Min(s) | Max(s) | "
        "StdDev | Track moy | Visités |",
        "|--------|------|--------|---------|--------|--------|--------|"
        "--------|-----------|---------|",
    ]
    for w, h, agg in summary_rows:
        size = f"{w}×{h}"
        mean = (
            f"{agg['time_mean']:.5f}" if agg['time_mean'] is not None else "—"
        )
        mn = (
            f"{agg['time_min']:.5f}" if agg['time_min'] is not None else "—"
        )
        mx = (
            f"{agg['time_max']:.5f}" if agg['time_max'] is not None else "—"
        )
        sd = (
            f"{agg['time_stdev']:.5f}" if agg['time_mean'] is not None else "—"
        )
        trk = (
            f"{agg['track_mean']:.0f}" if agg['track_mean'] is not None else "—"
        )
        vis = (
            f"{agg['visited_mean']:.0f}"
            if agg['visited_mean'] is not None else "—"
        )
        lines.append(
            f"| {size} | {agg['n_runs']} | {agg['n_success']} | "
            f"{agg['n_valid']} | {mean} | {mn} | {mx} | {sd} | {trk} | {vis} |"
        )

    lines += [
        "",
        "## Légende",
        "",
        "- **Track** : nombre de murs supprimés pendant la génération "
        "(= passages creusés)",
        (
            "- **Visités** : nombre de cellules parcourues par le DFS "
            "(hors motif 42)"
        ),
        "- **Valides** : nombre de labyrinthes ayant passé MazeValidator",
        "- Le Backtracker génère toujours un labyrinthe **parfait** "
        "(un seul chemin entre deux points)",
        "",
    ]

    slow = [(w, h) for w, h, a in summary_rows
            if a['time_mean'] is not None and a['time_mean'] > 1.0]
    if slow:
        slow_str = ", ".join(f"{w}×{h}" for w, h in slow[:3])
        lines.append(f"> ⚠️ Tailles lentes (>1s en moyenne) : **{slow_str}**")
    else:
        lines.append("> ✅ Toutes les tailles testées sont < 1s en moyenne.")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[MD]  {path}")


# =============================================================================
# Point d'entrée principal
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark de l'algorithme Backtracker (A-Maze-ing)"
    )
    parser.add_argument(
        "--seeds", type=int, default=DEFAULT_SEEDS_PER_SIZE,
        help=f"Nombre de seeds par taille (défaut: {DEFAULT_SEEDS_PER_SIZE})"
    )
    parser.add_argument(
        "--max", type=int, default=501,
        help="Taille maximale à tester (côté, défaut: 501)"
    )
    parser.add_argument(
        "--no-csv", action="store_true",
        help="Ne pas exporter les résultats bruts en CSV"
    )
    args = parser.parse_args()

    sizes = [
        (w, h) for (w, h) in DEFAULT_SIZES if w <= args.max and h <= args.max
    ]
    seeds = list(range(1, args.seeds + 1))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(__file__).parent / "results" / f"backtracker_{timestamp}"
    results_dir.mkdir(parents=True, exist_ok=True)

    total_runs = len(sizes) * len(seeds)
    print("\n" + "=" * len(HEADER))
    print("  BENCHMARK BACKTRACKER — A-Maze-ing")
    print(
        f"  Tailles : {len(sizes)} | Seeds/taille : {args.seeds} | "
        f"Total runs : {total_runs}"
    )
    print("=" * len(HEADER) + "\n")
    print(HEADER)
    print(SEP)

    all_raw: list[dict[str, Any]] = []
    summary_rows: list[tuple[int, int, dict[str, Any]]] = []
    benchmark_start = time.perf_counter()

    for w, h in sizes:
        size_results = []
        for seed in seeds:
            r = bench_one(w, h, seed)
            all_raw.append(r)
            size_results.append(r)
            if not r["success"]:
                print(f"  !! {w}x{h} seed={seed} FAIL: {r['error']}")

        agg = aggregate(size_results)
        summary_rows.append((w, h, agg))
        print(fmt_row(w, h, agg))

    total_elapsed = time.perf_counter() - benchmark_start
    print(SEP)
    print(f"\nDurée totale : {total_elapsed:.2f}s | {len(all_raw)} runs")

    if not args.no_csv:
        csv_path = results_dir / f"benchmark_bt_{timestamp}.csv"
        export_csv(all_raw, csv_path)

    md_path = results_dir / f"benchmark_bt_{timestamp}.md"
    export_markdown(summary_rows, md_path, args.seeds,
                    max(w for w, h in sizes), total_elapsed)

    # Résumé des tailles lentes
    slow = [(w, h, a) for w, h, a in summary_rows
            if a['time_mean'] is not None and a['time_mean'] > 1.0]
    if slow:
        print("\n--- Tailles > 1s ---")
        for w, h, a in slow:
            print(f"  {w:>3}x{h:<3} → moy. {a['time_mean']:.3f}s")


if __name__ == "__main__":
    main()
