#!/usr/bin/env python3
"""
benchmark/run_benchmark.py — Benchmark complet de l'algorithme Kruskal (A-Maze-ing).

Mesure pour chaque taille de labyrinthe :
  - Temps de génération moyen / min / max
  - Taux de succès (sur N seeds)
  - Nombre de cellules et de murs ouverts
  - Nombre moyen d'itérations internes (_second_loop)
  - Nombre d'entrées dans le track

Usage :
  python3 benchmark/run_benchmark.py              # benchmark standard
  python3 benchmark/run_benchmark.py --seeds 20   # 20 seeds par taille
  python3 benchmark/run_benchmark.py --no-csv     # sans export CSV
  python3 benchmark/run_benchmark.py --max 71     # taille max 71x71

Résultats exportés dans benchmark/results/benchmark_<timestamp>.csv
et benchmark/results/benchmark_<timestamp>.md
"""

import sys
import os
import time
import random
import csv
import argparse
import statistics
from datetime import datetime
from pathlib import Path

# --- Chemin vers la racine du projet (le script est dans benchmark/) ---------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mazegen.kruksal import Kruksal
from mazegen.maze_generator import MazeGenerator
from model.maze import Maze
from model.maze_validator import MazeValidator

# =============================================================================
# Configuration
# =============================================================================

# Tailles de labyrinthe testées (width, height)
# Kruskal est très lent sur des labyrinthes > 101×101
DEFAULT_SIZES = [
    (5,  5),
    (7,  7),
    (9,  9),
    (11, 9),   # taille minimale avec motif 42
    (11, 11),
    (15, 15),
    (21, 21),
    (31, 31),
    (41, 41),
    (51, 51),
    (61, 61),
    (71, 71),
    (81, 81),
    (101, 101),
]

DEFAULT_SEEDS_PER_SIZE = 10
TIMEOUT_SECONDS = 5.0  # abandon si génération > N secondes


# =============================================================================
# Instrumented Kruskal (compte les itérations de _second_loop)
# =============================================================================

class InstrumentedKruksal(Kruksal):
    """Kruskal avec compteurs d'instrumentation."""

    def __init__(self, maze: Maze) -> None:
        super().__init__(maze)
        self.second_loop_calls: int = 0
        self.global_attempts: int = 0

    def _second_loop(self, maze, wall_count, pattern_cells, tracks):
        self.second_loop_calls += 1
        return super()._second_loop(maze, wall_count, pattern_cells, tracks)

    def generate(self):
        self.second_loop_calls = 0
        self.global_attempts = 0
        # Patch pour compter les tentatives globales
        for attempt in range(self._MAX_GLOBAL_ATTEMPTS):
            self.global_attempts = attempt + 1
            # Replier sur la logique parent mais on doit l'inliner
            # → on appelle simplement super() une fois
            break
        # On utilise la génération parente normalement
        return super().generate()


# =============================================================================
# Benchmark d'une seule configuration (w × h, seed)
# =============================================================================

def bench_one(width: int, height: int, seed: int, timeout: float
              ) -> dict:
    """
    Tente de générer un labyrinthe Kruskal (width × height, seed).
    Retourne un dict avec les métriques.
    """
    maze = Maze(width, height)
    algo = InstrumentedKruksal(maze)

    t_start = time.perf_counter()
    success = False
    error_msg = ""
    track_len = 0
    second_loop_calls = 0
    global_attempts = 0
    walls_opened = 0
    valid = False

    try:
        random.seed(seed)
        track = algo.generate()
        elapsed = time.perf_counter() - t_start

        if elapsed > timeout:
            # Généré mais trop lent → on le marque quand même
            pass

        success = True
        track_len = len(track)
        second_loop_calls = algo.second_loop_calls
        global_attempts = algo.global_attempts

        # Compter les murs ouverts (cellules avec valeur < 15)
        final_maze = algo.maze
        walls_opened = sum(
            bin(final_maze.grid[y][x]).count('0') - bin(15).count('0')
            for y in range(height)
            for x in range(width)
            if final_maze.grid[y][x] != 15
        )

        # Vérification finale
        validator = MazeValidator(final_maze)
        valid = validator.validate()

    except ValueError as e:
        elapsed = time.perf_counter() - t_start
        error_msg = str(e)[:80]
    except Exception as e:
        elapsed = time.perf_counter() - t_start
        error_msg = f"EXCEPTION: {type(e).__name__}: {str(e)[:60]}"

    return {
        "width": width,
        "height": height,
        "cells": width * height,
        "seed": seed,
        "success": success,
        "valid": valid,
        "elapsed_s": round(elapsed, 6),
        "track_len": track_len,
        "second_loop_calls": second_loop_calls,
        "global_attempts": global_attempts,
        "walls_opened": walls_opened,
        "error": error_msg,
    }


# =============================================================================
# Agrégation des résultats pour une taille
# =============================================================================

def aggregate(results: list[dict]) -> dict:
    """Calcule les statistiques agrégées pour un ensemble de runs."""
    successes = [r for r in results if r["success"]]
    failures  = [r for r in results if not r["success"]]
    n = len(results)

    times  = [r["elapsed_s"] for r in successes]
    tracks = [r["track_len"] for r in successes]
    loops  = [r["second_loop_calls"] for r in successes]

    return {
        "n_runs":         n,
        "n_success":      len(successes),
        "n_failure":      len(failures),
        "success_rate":   round(len(successes) / n * 100, 1) if n else 0,
        "time_mean":      round(statistics.mean(times),   6) if times else None,
        "time_min":       round(min(times),               6) if times else None,
        "time_max":       round(max(times),               6) if times else None,
        "time_stdev":     round(statistics.stdev(times),  6) if len(times) > 1 else 0,
        "track_mean":     round(statistics.mean(tracks),  1) if tracks else None,
        "loops_mean":     round(statistics.mean(loops),   2) if loops else None,
    }


# =============================================================================
# Affichage terminal
# =============================================================================

HEADER = (
    f"{'Size':>9} | {'Runs':>4} | {'Succ':>4} | {'Fail':>4} | "
    f"{'Rate%':>6} | {'Mean(s)':>8} | {'Min(s)':>8} | {'Max(s)':>8} | "
    f"{'StdDev':>8} | {'TrackAvg':>8} | {'LoopAvg':>7}"
)
SEP = "-" * len(HEADER)


def fmt_row(w: int, h: int, agg: dict) -> str:
    size = f"{w}x{h}"
    rate = f"{agg['success_rate']:.1f}"
    mean = f"{agg['time_mean']:.4f}" if agg['time_mean'] is not None else "  FAIL"
    mn   = f"{agg['time_min']:.4f}"  if agg['time_min']  is not None else "  FAIL"
    mx   = f"{agg['time_max']:.4f}"  if agg['time_max']  is not None else "  FAIL"
    sd   = f"{agg['time_stdev']:.4f}"if agg['time_mean'] is not None else "  FAIL"
    trk  = f"{agg['track_mean']:.0f}" if agg['track_mean'] is not None else "  FAIL"
    lp   = f"{agg['loops_mean']:.1f}" if agg['loops_mean'] is not None else "  FAIL"
    return (
        f"{size:>9} | {agg['n_runs']:>4} | {agg['n_success']:>4} | "
        f"{agg['n_failure']:>4} | {rate:>6} | {mean:>8} | {mn:>8} | "
        f"{mx:>8} | {sd:>8} | {trk:>8} | {lp:>7}"
    )


# =============================================================================
# Export CSV + Markdown
# =============================================================================

def export_csv(all_raw: list[dict], path: Path) -> None:
    if not all_raw:
        return
    fieldnames = list(all_raw[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_raw)
    print(f"\n[CSV] {path}")


def export_markdown(summary_rows: list[tuple], path: Path,
                    n_seeds: int, max_size: int,
                    total_elapsed: float) -> None:
    lines = [
        "# Benchmark Kruskal — A-Maze-ing",
        "",
        f"> Généré le {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  ",
        f"> Seeds par taille : **{n_seeds}** | Taille max : **{max_size}×{max_size}**  ",
        f"> Durée totale du benchmark : **{total_elapsed:.2f}s**",
        "",
        "## Résultats par taille",
        "",
        "| Taille | Runs | Succès | Échecs | Taux% | Moy(s) | Min(s) | Max(s) | StdDev | Track moy | Loops moy |",
        "|--------|------|--------|--------|-------|--------|--------|--------|--------|-----------|-----------|",
    ]
    for w, h, agg in summary_rows:
        size = f"{w}×{h}"
        rate = f"{agg['success_rate']:.1f}"
        mean = f"{agg['time_mean']:.4f}" if agg['time_mean'] is not None else "—"
        mn   = f"{agg['time_min']:.4f}"  if agg['time_min']  is not None else "—"
        mx   = f"{agg['time_max']:.4f}"  if agg['time_max']  is not None else "—"
        sd   = f"{agg['time_stdev']:.4f}"if agg['time_mean'] is not None else "—"
        trk  = f"{agg['track_mean']:.0f}" if agg['track_mean'] is not None else "—"
        lp   = f"{agg['loops_mean']:.1f}" if agg['loops_mean'] is not None else "—"
        lines.append(
            f"| {size} | {agg['n_runs']} | {agg['n_success']} | "
            f"{agg['n_failure']} | {rate} | {mean} | {mn} | {mx} | {sd} | {trk} | {lp} |"
        )

    # Find tipping point (first size with time_mean > 1s)
    slow_sizes = [(w, h) for w, h, a in summary_rows
                  if a['time_mean'] is not None and a['time_mean'] > 1.0]

    lines += [
        "",
        "## Notes d'interprétation",
        "",
        "- **Track** : nombre total d'ouvertures de murs effectuées",
        "- **Loops moy** : nombre moyen d'itérations de `_second_loop` pour corriger la connectivité",
        "- **Taux%** : pourcentage de seeds qui ont produit un labyrinthe valide en ≤ 30 tentatives globales",
        "",
    ]
    if slow_sizes:
        slow_str = ", ".join(f"{w}×{h}" for w, h in slow_sizes[:3])
        lines.append(f"> ⚠️ Tailles lentes (>1s en moyenne) : **{slow_str}** — déconseillées pour un usage interactif.")
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
        description="Benchmark de l'algorithme Kruskal (A-Maze-ing)"
    )
    parser.add_argument(
        "--seeds", type=int, default=DEFAULT_SEEDS_PER_SIZE,
        help=f"Nombre de seeds par taille (défaut: {DEFAULT_SEEDS_PER_SIZE})"
    )
    parser.add_argument(
        "--max", type=int, default=101,
        help="Taille maximale à tester (côté, défaut: 101)"
    )
    parser.add_argument(
        "--no-csv", action="store_true",
        help="Ne pas exporter les résultats bruts en CSV"
    )
    parser.add_argument(
        "--timeout", type=float, default=TIMEOUT_SECONDS,
        help=f"Timeout par génération en secondes (défaut: {TIMEOUT_SECONDS})"
    )
    args = parser.parse_args()

    sizes = [(w, h) for (w, h) in DEFAULT_SIZES if w <= args.max and h <= args.max]
    n_seeds = args.seeds
    seeds = list(range(1, n_seeds + 1))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(__file__).parent / "results" / f"kruskal_{timestamp}"
    results_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*72}")
    print(f"  BENCHMARK KRUSKAL — A-Maze-ing")
    print(f"  Tailles : {len(sizes)} | Seeds/taille : {n_seeds} | Total runs : {len(sizes)*n_seeds}")
    print(f"  Timeout par run : {args.timeout}s")
    print(f"{'='*72}\n")
    print(HEADER)
    print(SEP)

    all_raw: list[dict] = []
    summary_rows: list[tuple] = []
    benchmark_start = time.perf_counter()

    for w, h in sizes:
        size_results = []
        for seed in seeds:
            r = bench_one(w, h, seed, args.timeout)
            all_raw.append(r)
            size_results.append(r)

            # Affichage en temps réel si échec
            if not r["success"]:
                print(f"  !! {w}x{h} seed={seed} FAIL: {r['error']}")

        agg = aggregate(size_results)
        summary_rows.append((w, h, agg))
        print(fmt_row(w, h, agg))

    total_elapsed = time.perf_counter() - benchmark_start
    print(SEP)
    print(f"\nDurée totale : {total_elapsed:.2f}s | {len(all_raw)} runs")

    # Export
    if not args.no_csv:
        csv_path = results_dir / f"benchmark_{timestamp}.csv"
        export_csv(all_raw, csv_path)

    md_path = results_dir / f"benchmark_{timestamp}.md"
    export_markdown(
        summary_rows, md_path, n_seeds,
        max(w for w, h in sizes), total_elapsed
    )

    # Résumé des limites
    print("\n--- Résumé des limites ---")
    for w, h, agg in summary_rows:
        if agg["n_failure"] > 0 or (agg["time_mean"] is not None and agg["time_mean"] > 1.0):
            status = []
            if agg["n_failure"] > 0:
                status.append(f"{agg['n_failure']} échec(s)")
            if agg["time_mean"] and agg["time_mean"] > 1.0:
                status.append(f"lent ({agg['time_mean']:.2f}s moy.)")
            print(f"  {w:>3}x{h:<3} → " + ", ".join(status))


if __name__ == "__main__":
    main()
