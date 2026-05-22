#!/usr/bin/env python3
"""
benchmark/run_benchmark.py — Full benchmark of the Kruksal algorithm
(A-Maze-ing).

Measurement for each maze size:
  - Average / min / max generation time
  - Success rate (over N seeds)
  - Number of cells and opened walls
  - Average number of internal iterations (second_loop)
  - Number of entries in the track

Usage:
  python3 benchmark/run_benchmark.py              # standard benchmark
  python3 benchmark/run_benchmark.py --seeds 20   # 20 seeds per size
  python3 benchmark/run_benchmark.py --no-csv     # skip CSV export
  python3 benchmark/run_benchmark.py --max 71     # max size 71x71

Results exported to benchmark/results/benchmark_<timestamp>.csv
and benchmark/results/benchmark_<timestamp>.md
"""

import sys
import time
import random
import csv
import argparse
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any

# --- Path to the project root (script lives inside benchmark/) --------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mazegen.generation.kruksal import Kruksal  # noqa: E402
from model.maze import Maze  # noqa: E402
from model.maze_validator import MazeValidator  # noqa: E402

# =============================================================================
# Configuration
# =============================================================================

# Tested maze sizes (width, height)
# Kruksal is very slow on mazes > 101×101
DEFAULT_SIZES = [
    (5, 5),
    (7, 7),
    (9, 9),
    (11, 9),  # minimum size with 42 pattern
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
TIMEOUT_SECONDS = 5.0  # abort if generation > N seconds


# =============================================================================
# Instrumented Kruksal (counts _second_loop iterations)
# =============================================================================


class InstrumentedKruksal(Kruksal):
    """Kruksal with instrumentation counters."""

    def __init__(self, maze: Maze, is_perfect: bool = False) -> None:
        super().__init__(maze, is_perfect=is_perfect)
        self.second_loop_calls: int = 0
        self.global_attempts: int = 0

    def second_loop(self) -> None:
        self.second_loop_calls += 1
        super().second_loop()

    def generate(self) -> list[tuple[int, int, str]]:
        self.second_loop_calls = 0
        self.global_attempts = 1  # default value
        return super().generate()


# =============================================================================
# Benchmark of a single configuration (w x h, seed)
# =============================================================================


def bench_one(
    width: int, height: int, seed: int, timeout: float
) -> dict[str, Any]:
    """
    benchmark a single configuration (w × h, seed)
    """
    maze = Maze(width, height, entry=(0, 0), exit=(width - 1, height - 1))
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
            # Generated but too slow - still recorded
            pass

        success = True
        track_len = len(track)
        second_loop_calls = algo.second_loop_calls
        global_attempts = algo.global_attempts

        # Count opened walls (cells with value < 15)
        final_maze = algo.maze
        walls_opened = sum(
            bin(final_maze.grid[y][x]).count("0") - bin(15).count("0")
            for y in range(height)
            for x in range(width)
            if final_maze.grid[y][x] != 15
        )

        # Final validation
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
# Aggregate results for one size
# =============================================================================


def aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute aggregated statistics for a set of runs."""
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]
    n = len(results)

    times = [r["elapsed_s"] for r in successes]
    tracks = [r["track_len"] for r in successes]
    loops = [r["second_loop_calls"] for r in successes]

    return {
        "n_runs": n,
        "n_success": len(successes),
        "n_failure": len(failures),
        "success_rate": round(len(successes) / n * 100, 1) if n else 0,
        "time_mean": round(statistics.mean(times), 6) if times else None,
        "time_min": round(min(times), 6) if times else None,
        "time_max": round(max(times), 6) if times else None,
        "time_stdev": (
            round(statistics.stdev(times), 6) if len(times) > 1 else 0
        ),
        "track_mean": round(statistics.mean(tracks), 1) if tracks else None,
        "loops_mean": round(statistics.mean(loops), 2) if loops else None,
    }


# =============================================================================
# Terminal display
# =============================================================================

HEADER = (
    f"{'Size':>9} | {'Runs':>4} | {'Succ':>4} | {'Fail':>4} | "
    f"{'Rate%':>6} | {'Mean(s)':>8} | {'Min(s)':>8} | {'Max(s)':>8} | "
    f"{'StdDev':>8} | {'TrackAvg':>8} | {'LoopAvg':>7}"
)
SEP = "-" * len(HEADER)


def fmt_row(w: int, h: int, agg: dict[str, Any]) -> str:
    size = f"{w}x{h}"
    rate = f"{agg['success_rate']:.1f}"
    mean = (
        f"{agg['time_mean']:.4f}" if agg["time_mean"] is not None else "  FAIL"
    )
    mn = f"{agg['time_min']:.4f}" if agg["time_min"] is not None else "  FAIL"
    mx = f"{agg['time_max']:.4f}" if agg["time_max"] is not None else "  FAIL"
    sd = (
        f"{agg['time_stdev']:.4f}"
        if agg["time_mean"] is not None
        else "  FAIL"
    )
    trk = (
        f"{agg['track_mean']:.0f}"
        if agg["track_mean"] is not None
        else "  FAIL"
    )
    lp = (
        f"{agg['loops_mean']:.1f}"
        if agg["loops_mean"] is not None
        else "  FAIL"
    )
    return (
        f"{size:>9} | {agg['n_runs']:>4} | {agg['n_success']:>4} | "
        f"{agg['n_failure']:>4} | {rate:>6} | {mean:>8} | {mn:>8} | "
        f"{mx:>8} | {sd:>8} | {trk:>8} | {lp:>7}"
    )


# =============================================================================
# CSV + Markdown export
# =============================================================================


def export_csv(all_raw: list[dict[str, Any]], path: Path) -> None:
    if not all_raw:
        return
    fieldnames = list(all_raw[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
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
        "# Benchmark Kruksal — A-Maze-ing",
        "",
        f"> Generated on {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  ",
        f"> Seeds per size: **{n_seeds}** | Max size: **{
            max_size}×{max_size}**  ",
        f"> Total benchmark duration: **{total_elapsed:.2f}s**",
        "",
        "## Results by size",
        "",
        "| Size | Runs | Success | Failures | Rate% | Mean(s) | Min(s) |"
        "  Max(s) |StdDev | Track avg | Loops avg |",
        "|------|------|---------|----------|-------|---------|--------|"
        "--------|--------|-----------|-----------|",
    ]
    for w, h, agg in summary_rows:
        size = f"{w}×{h}"
        rate = f"{agg['success_rate']:.1f}"
        mean = (
            f"{agg['time_mean']:.4f}" if agg["time_mean"] is not None else "—"
        )
        mn = f"{agg['time_min']:.4f}" if agg["time_min"] is not None else "—"
        mx = f"{agg['time_max']:.4f}" if agg["time_max"] is not None else "—"
        sd = (
            f"{agg['time_stdev']:.4f}" if agg["time_mean"] is not None else "—"
        )
        trk = (
            f"{agg['track_mean']:.0f}"
            if agg["track_mean"] is not None
            else "—"
        )
        lp = (
            f"{agg['loops_mean']:.1f}"
            if agg["loops_mean"] is not None
            else "—"
        )
        lines.append(
            f"| {size} | {agg['n_runs']} | {agg['n_success']} | "
            f"{agg['n_failure']} | {rate} | {mean} | {mn} | {mx} "
            f"| {sd} | {trk} | {lp} |"
        )

    # Find tipping point (first size with time_mean > 1s)
    slow_sizes = [
        (w, h)
        for w, h, a in summary_rows
        if a["time_mean"] is not None and a["time_mean"] > 1.0
    ]

    lines += [
        "",
        "## Interpretation notes",
        "",
        "- **Track**: total number of wall openings performed",
        "- **Loops avg**: average number of `second_loop` iterations "
        "to fix connectivity",
        "- **Rate%**: percentage of seeds that produced a valid maze "
        "in <= 30 global attempts",
        "",
    ]
    if slow_sizes:
        slow_str = ", ".join(f"{w}×{h}" for w, h in slow_sizes[:3])
        lines.append(
            f"> WARNING Slow sizes (>1s average): **{slow_str}** "
            "- not recommended for interactive use."
        )
    else:
        lines.append("> OK All tested sizes are < 1s on average.")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[MD]  {path}")


# =============================================================================
# Main entry point
# =============================================================================


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark of the Kruksal algorithm (A-Maze-ing)"
    )
    parser.add_argument(
        "--seeds",
        type=int,
        default=DEFAULT_SEEDS_PER_SIZE,
        help=f"Number of seeds per size (default: {DEFAULT_SEEDS_PER_SIZE})",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=101,
        help="Maximum size to test (side length, default: 101)",
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Do not export raw results to CSV",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=TIMEOUT_SECONDS,
        help=f"Timeout per generation in seconds (default: {TIMEOUT_SECONDS})",
    )
    args = parser.parse_args()

    sizes = [
        (w, h) for (w, h) in DEFAULT_SIZES if w <= args.max and h <= args.max
    ]
    n_seeds = args.seeds
    seeds = list(range(1, n_seeds + 1))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(__file__).parent / "results" / f"kruksal_{timestamp}"
    results_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*72}")
    print("  BENCHMARK KRUSKAL — A-Maze-ing")
    print(
        f"  Sizes: {len(sizes)} | Seeds/size: {n_seeds} "
        f"| Total runs: {len(sizes)*n_seeds}"
    )
    print(f"  Timeout per run: {args.timeout}s")
    print(f"{'='*72}\n")
    print(HEADER)
    print(SEP)

    all_raw: list[dict[str, Any]] = []
    summary_rows: list[tuple[int, int, dict[str, Any]]] = []
    benchmark_start = time.perf_counter()

    for w, h in sizes:
        size_results = []
        for seed in seeds:
            r = bench_one(w, h, seed, args.timeout)
            all_raw.append(r)
            size_results.append(r)

            # Real-time display on failure
            if not r["success"]:
                print(f"  !! {w}x{h} seed={seed} FAIL: {r['error']}")

        agg = aggregate(size_results)
        summary_rows.append((w, h, agg))
        print(fmt_row(w, h, agg))

    total_elapsed = time.perf_counter() - benchmark_start
    print(SEP)
    print(f"\nTotal duration: {total_elapsed:.2f}s | {len(all_raw)} runs")

    # Export
    if not args.no_csv:
        csv_path = results_dir / f"benchmark_{timestamp}.csv"
        export_csv(all_raw, csv_path)

    md_path = results_dir / f"benchmark_{timestamp}.md"
    export_markdown(
        summary_rows, md_path, n_seeds, max(w for w, h in sizes), total_elapsed
    )

    # Limit summary
    print("\n--- Limit summary ---")
    for w, h, agg in summary_rows:
        if agg["n_failure"] > 0 or (
            agg["time_mean"] is not None and agg["time_mean"] > 1.0
        ):
            status = []
            if agg["n_failure"] > 0:
                status.append(f"{agg['n_failure']} failure(s)")
            if agg["time_mean"] and agg["time_mean"] > 1.0:
                status.append(f"slow ({agg['time_mean']:.2f}s avg)")
            print(f"  {w:>3}x{h:<3} -> " + ", ".join(status))


if __name__ == "__main__":
    main()
