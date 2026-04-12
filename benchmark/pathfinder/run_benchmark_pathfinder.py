#!/usr/bin/env python3
"""
benchmark/run_benchmark_pathfinder.py — Benchmark de PathFinder (A-Maze-ing).

Mesure pour chaque taille de labyrinthe :
  - Temps de recherche moyen / min / max (1 plus court chemin)
  - Temps de recherche avec chemins alternatifs (n_extra=2)
  - Longueur moyenne du chemin solution
  - Nombre de cellules visitées par le BFS
  - Comportement parfait vs imparfait (nb de chemins retournés)

Usage :
  python3 benchmark/run_benchmark_pathfinder.py              # benchmark standard
  python3 benchmark/run_benchmark_pathfinder.py --seeds 20   # 20 seeds par taille
  python3 benchmark/run_benchmark_pathfinder.py --no-csv     # sans export CSV
  python3 benchmark/run_benchmark_pathfinder.py --max 201    # taille max 201x201

Résultats exportés dans benchmark/results/benchmark_pf_<timestamp>.csv
et benchmark/results/benchmark_pf_<timestamp>.md
"""

import sys
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

from mazegen.maze_generator import MazeGenerator
from model.path_finder import PathFinder

# =============================================================================
# Configuration
# =============================================================================

DEFAULT_SIZES = [
    (5,   5),
    (11,  9),    # taille minimale avec motif 42
    (11,  11),
    (21,  21),
    (31,  31),
    (51,  51),
    (71,  71),
    (101, 101),
    (151, 151),
    (201, 201),
]

DEFAULT_SEEDS_PER_SIZE = 10


# =============================================================================
# Benchmark d'une configuration (w × h, seed, perfect)
# =============================================================================

def bench_one(width: int, height: int, seed: int, perfect: bool) -> dict:
    """Génère un labyrinthe puis mesure PathFinder dessus."""

    # --- Génération ---
    try:
        gen = MazeGenerator(width=width, height=height, seed=seed, perfect=perfect)
        gen.generate()
        maze = gen.get_maze()
    except Exception as e:
        return {
            "width": width, "height": height, "cells": width * height,
            "seed": seed, "perfect": perfect,
            "gen_ok": False,
            "time_shortest_s": None, "time_with_extra_s": None,
            "path_len": None, "bfs_visited": None,
            "n_paths_returned": None, "has_alternative": None,
            "error": f"GEN: {type(e).__name__}: {str(e)[:60]}",
        }

    entry = (0, 0)
    exit_pos = (width - 1, height - 1)
    pf = PathFinder(maze, entry=entry, exit=exit_pos)

    # --- Mesure : 1 plus court chemin uniquement ---
    t0 = time.perf_counter()
    paths_short = pf.find_k_shortest_paths(k=1, n_extra=0)
    time_shortest = time.perf_counter() - t0

    path_len = None
    bfs_visited = None
    if paths_short:
        # Longueur du chemin = nombre de cellules dans le dict de connexions
        path_len = len(paths_short[0])

    # Compter les cellules visitées par BFS (via distances)
    dist, _ = pf._compute_distance_and_predecessors()
    bfs_visited = len(dist)

    # --- Mesure : 1 plus court + 2 alternatifs ---
    t0 = time.perf_counter()
    paths_extra = pf.find_k_shortest_paths(k=1, n_extra=2)
    time_with_extra = time.perf_counter() - t0

    n_paths = len(paths_extra)
    has_alternative = n_paths > 1

    return {
        "width": width,
        "height": height,
        "cells": width * height,
        "seed": seed,
        "perfect": perfect,
        "gen_ok": True,
        "time_shortest_s": round(time_shortest, 7),
        "time_with_extra_s": round(time_with_extra, 7),
        "path_len": path_len,
        "bfs_visited": bfs_visited,
        "n_paths_returned": n_paths,
        "has_alternative": has_alternative,
        "error": "",
    }


# =============================================================================
# Agrégation
# =============================================================================

def aggregate(results: list[dict]) -> dict:
    ok = [r for r in results if r["gen_ok"] and r["time_shortest_s"] is not None]
    n = len(results)

    times_s  = [r["time_shortest_s"]   for r in ok]
    times_e  = [r["time_with_extra_s"] for r in ok]
    lens     = [r["path_len"]          for r in ok if r["path_len"] is not None]
    visited  = [r["bfs_visited"]       for r in ok if r["bfs_visited"] is not None]
    alt      = [r["has_alternative"]   for r in ok]

    def st(lst): return round(statistics.stdev(lst), 7) if len(lst) > 1 else 0.0
    def mn(lst): return round(min(lst), 7)              if lst else None
    def mx(lst): return round(max(lst), 7)              if lst else None
    def avg(lst): return round(statistics.mean(lst), 4) if lst else None

    return {
        "n_runs":           n,
        "n_ok":             len(ok),
        "time_s_mean":      avg(times_s),
        "time_s_min":       mn(times_s),
        "time_s_max":       mx(times_s),
        "time_s_stdev":     st(times_s),
        "time_e_mean":      avg(times_e),
        "path_len_mean":    avg(lens),
        "bfs_visited_mean": avg(visited),
        "alt_rate":         round(sum(alt) / len(alt) * 100, 1) if alt else 0.0,
    }


# =============================================================================
# Affichage terminal
# =============================================================================

HEADER = (
    f"{'Size':>9} | {'Mode':>9} | {'Runs':>4} | "
    f"{'Mean(s)':>9} | {'Min(s)':>9} | {'Max(s)':>9} | {'StdDev':>9} | "
    f"{'+Extra(s)':>9} | {'PathLen':>7} | {'BFSvisit':>8} | {'Alt%':>5}"
)
SEP = "-" * len(HEADER)


def fmt_row(w: int, h: int, mode: str, agg: dict) -> str:
    size   = f"{w}x{h}"
    mean   = f"{agg['time_s_mean']:.5f}"   if agg['time_s_mean']   is not None else "   FAIL"
    mn     = f"{agg['time_s_min']:.5f}"    if agg['time_s_min']    is not None else "   FAIL"
    mx     = f"{agg['time_s_max']:.5f}"    if agg['time_s_max']    is not None else "   FAIL"
    sd     = f"{agg['time_s_stdev']:.5f}"  if agg['time_s_mean']   is not None else "   FAIL"
    extra  = f"{agg['time_e_mean']:.5f}"   if agg['time_e_mean']   is not None else "   FAIL"
    plen   = f"{agg['path_len_mean']:.0f}" if agg['path_len_mean'] is not None else "      -"
    vis    = f"{agg['bfs_visited_mean']:.0f}" if agg['bfs_visited_mean'] is not None else "       -"
    alt    = f"{agg['alt_rate']:.0f}%"
    return (
        f"{size:>9} | {mode:>9} | {agg['n_runs']:>4} | "
        f"{mean:>9} | {mn:>9} | {mx:>9} | {sd:>9} | "
        f"{extra:>9} | {plen:>7} | {vis:>8} | {alt:>5}"
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


def export_markdown(
    summary_rows: list[tuple],
    path: Path,
    n_seeds: int,
    max_size: int,
    total_elapsed: float,
) -> None:
    lines = [
        "# Benchmark PathFinder — A-Maze-ing",
        "",
        f"> Généré le {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  ",
        f"> Seeds par taille : **{n_seeds}** | Taille max : **{max_size}×{max_size}**  ",
        f"> Durée totale du benchmark : **{total_elapsed:.2f}s**",
        "",
        "## Résultats par taille",
        "",
        "| Taille | Mode | Runs | Moy(s) | Min(s) | Max(s) | StdDev | +Extra(s) | PathLen | BFSvisit | Alt% |",
        "|--------|------|------|--------|--------|--------|--------|-----------|---------|----------|------|",
    ]

    for w, h, mode, agg in summary_rows:
        size   = f"{w}×{h}"
        mean   = f"{agg['time_s_mean']:.5f}"   if agg['time_s_mean']   is not None else "—"
        mn     = f"{agg['time_s_min']:.5f}"    if agg['time_s_min']    is not None else "—"
        mx     = f"{agg['time_s_max']:.5f}"    if agg['time_s_max']    is not None else "—"
        sd     = f"{agg['time_s_stdev']:.5f}"  if agg['time_s_mean']   is not None else "—"
        extra  = f"{agg['time_e_mean']:.5f}"   if agg['time_e_mean']   is not None else "—"
        plen   = f"{agg['path_len_mean']:.0f}" if agg['path_len_mean'] is not None else "—"
        vis    = f"{agg['bfs_visited_mean']:.0f}" if agg['bfs_visited_mean'] is not None else "—"
        alt    = f"{agg['alt_rate']:.0f}%"
        lines.append(
            f"| {size} | {mode} | {agg['n_runs']} | {mean} | {mn} | {mx} | {sd} | "
            f"{extra} | {plen} | {vis} | {alt} |"
        )

    lines += [
        "",
        "## Légende",
        "",
        "- **Moy/Min/Max(s)** : temps du BFS pour 1 plus court chemin",
        "- **+Extra(s)** : temps du BFS + recherche DFS de 2 chemins alternatifs",
        "- **PathLen** : nombre de cellules dans le chemin solution",
        "- **BFSvisit** : nombre de cellules visitées par le BFS",
        "- **Alt%** : pourcentage de runs où au moins 1 chemin alternatif a été trouvé",
        "  - Alt% ≈ 0% → labyrinthe parfait (un seul chemin)",
        "  - Alt% > 0% → labyrinthe imparfait (plusieurs chemins possibles)",
        "",
    ]

    slow = [(w, h) for w, h, _, a in summary_rows
            if a['time_s_mean'] is not None and a['time_s_mean'] > 0.01]
    if slow:
        slow_str = ", ".join(f"{w}×{h}" for w, h in slow[:3])
        lines.append(f"> ⚠️ Tailles > 10ms en moyenne : **{slow_str}**")
    else:
        lines.append("> ✅ Toutes les tailles testées sont < 10ms en moyenne.")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[MD]  {path}")


# =============================================================================
# Point d'entrée principal
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark de PathFinder (A-Maze-ing)"
    )
    parser.add_argument(
        "--seeds", type=int, default=DEFAULT_SEEDS_PER_SIZE,
        help=f"Nombre de seeds par taille (défaut: {DEFAULT_SEEDS_PER_SIZE})"
    )
    parser.add_argument(
        "--max", type=int, default=201,
        help="Taille maximale à tester (côté, défaut: 201)"
    )
    parser.add_argument(
        "--no-csv", action="store_true",
        help="Ne pas exporter les résultats bruts en CSV"
    )
    parser.add_argument(
        "--perfect-only", action="store_true",
        help="Tester uniquement les labyrinthes parfaits (Backtracker)"
    )
    parser.add_argument(
        "--imperfect-only", action="store_true",
        help="Tester uniquement les labyrinthes imparfaits (Kruskal)"
    )
    args = parser.parse_args()

    sizes = [(w, h) for (w, h) in DEFAULT_SIZES if w <= args.max and h <= args.max]
    seeds = list(range(1, args.seeds + 1))

    modes: list[tuple[str, bool]] = []
    if not args.imperfect_only:
        modes.append(("parfait", True))
    if not args.perfect_only:
        modes.append(("imparfait", False))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(__file__).parent / "results" / f"pathfinder_{timestamp}"
    results_dir.mkdir(parents=True, exist_ok=True)

    total_runs = len(sizes) * len(seeds) * len(modes)
    print(f"\n{'='*len(HEADER)}")
    print(f"  BENCHMARK PATHFINDER — A-Maze-ing")
    print(f"  Tailles : {len(sizes)} | Seeds/taille : {args.seeds} | Modes : {len(modes)} | Total runs : {total_runs}")
    print(f"{'='*len(HEADER)}\n")
    print(HEADER)
    print(SEP)

    all_raw: list[dict] = []
    summary_rows: list[tuple] = []
    benchmark_start = time.perf_counter()

    for mode_name, perfect in modes:
        for w, h in sizes:
            size_results = []
            for seed in seeds:
                r = bench_one(w, h, seed, perfect)
                all_raw.append(r)
                size_results.append(r)
                if not r["gen_ok"]:
                    print(f"  !! {w}x{h} {mode_name} seed={seed} FAIL: {r['error']}")

            agg = aggregate(size_results)
            summary_rows.append((w, h, mode_name, agg))
            print(fmt_row(w, h, mode_name, agg))

        print(SEP)

    total_elapsed = time.perf_counter() - benchmark_start
    print(f"\nDurée totale : {total_elapsed:.2f}s | {len(all_raw)} runs")

    # Export
    if not args.no_csv:
        csv_path = results_dir / f"benchmark_pf_{timestamp}.csv"
        export_csv(all_raw, csv_path)

    md_path = results_dir / f"benchmark_pf_{timestamp}.md"
    export_markdown(summary_rows, md_path, args.seeds,
                    max(w for w, h in sizes), total_elapsed)

    # Résumé Alt% par mode
    print("\n--- Résumé Alt% (validation parfait/imparfait) ---")
    for w, h, mode_name, agg in summary_rows:
        perfect_flag = "✓ parfait" if agg["alt_rate"] == 0.0 else f"~ imparfait (alt={agg['alt_rate']:.0f}%)"
        print(f"  {w:>3}x{h:<3} [{mode_name:>9}] → {perfect_flag}")


if __name__ == "__main__":
    main()
