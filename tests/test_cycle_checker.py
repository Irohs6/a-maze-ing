# tests/test_cycle_checker.py — Unit tests for CycleChecker.
# Verifies cycle detection in the maze graph.
# Method: edges >= nodes (spanning tree = nodes-1 edges, cycle = nodes+)
# Cells of the "42" pattern (value 15 = isolated) are excluded from the count.

import sys
try:
    import pytest
except ImportError:
    print("\033c", end="")
    print(
        "Pytest not found, try starting the program with 'make run' command."
    )
    sys.exit(7)
from mazegen.model.maze import Maze
from mazegen.model.cycle_checker import CycleChecker
from mazegen.generation.maze_generator import MazeGenerator

# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def perfect_11x11() -> Maze:
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=True)
    gen.generate()
    return gen.get_maze()


@pytest.fixture
def imperfect_kruksal_11x11() -> Maze:
    gen = MazeGenerator(
        width=11, height=11, seed=1, perfect=False, algorithm="kruksal"
    )
    gen.generate()
    return gen.get_maze()


@pytest.fixture
def imperfect_backtracker_11x11() -> Maze:
    gen = MazeGenerator(
        width=11, height=11, seed=5, perfect=False, algorithm="backtracker"
    )
    gen.generate()
    return gen.get_maze()


# ── Full-wall maze (no passages) ─────────────────────────────────────


def test_full_wall_maze_has_no_cycle() -> None:
    """No passage → edges=0, nodes>0 → no cycle."""
    maze = Maze(5, 5)
    assert CycleChecker(maze).has_cycle() is False


def test_single_cell_has_no_cycle() -> None:
    maze = Maze(1, 1)
    assert CycleChecker(maze).has_cycle() is False


# ── Perfect maze (spanning tree) ─────────────────────────────────────


def test_perfect_maze_has_no_cycle(perfect_11x11: Maze) -> None:
    """Perfect maze = spanning tree → edges = nodes-1 → no cycle."""
    assert CycleChecker(perfect_11x11).has_cycle() is False


def test_perfect_small_maze_has_no_cycle() -> None:
    gen = MazeGenerator(width=5, height=5, seed=42, perfect=True)
    gen.generate()
    assert CycleChecker(gen.get_maze()).has_cycle() is False


# ── Imperfect maze (cycles present) ─────────────────────────────────────


def test_imperfect_kruksal_has_cycle(imperfect_kruksal_11x11: Maze) -> None:
    """Imperfect Kruksal: second_loop creates cycles."""
    assert CycleChecker(imperfect_kruksal_11x11).has_cycle() is True


def test_imperfect_backtracker_has_cycle(
    imperfect_backtracker_11x11: Maze,
) -> None:
    """Imperfect Backtracker: second_loop creates cycles."""
    assert CycleChecker(imperfect_backtracker_11x11).has_cycle() is True


# ── Manually constructed cases ───────────────────────────────────────


def test_two_cells_one_connection_no_cycle() -> None:
    """2 cells, 1 connection: edges=1, nodes=2 → 1 < 2 → no cycle."""
    maze = Maze(2, 1)
    maze.remove_wall(0, 0, "E")
    assert CycleChecker(maze).has_cycle() is False


def test_2x2_loop_creates_cycle() -> None:
    """2x2 loop: 4 E/S connections, 4 nodes -> edges=4 >= nodes=4 -> cycle."""
    maze = Maze(2, 2)
    maze.remove_wall(0, 0, "E")
    maze.remove_wall(0, 0, "S")
    maze.remove_wall(1, 0, "S")
    maze.remove_wall(0, 1, "E")
    assert CycleChecker(maze).has_cycle() is True


def test_linear_chain_no_cycle() -> None:
    """Linear chain 4x1: 3 connections, 4 nodes -> no cycle."""
    maze = Maze(4, 1)
    maze.remove_wall(0, 0, "E")
    maze.remove_wall(1, 0, "E")
    maze.remove_wall(2, 0, "E")
    assert CycleChecker(maze).has_cycle() is False


def test_tree_3x3_no_cycle() -> None:
    """Spanning tree 3x3: 8 connections, 9 nodes -> no cycle."""
    maze = Maze(3, 3)
    # Construction d'un arbre : chemin en serpentin
    maze.remove_wall(0, 0, "E")
    maze.remove_wall(1, 0, "E")
    maze.remove_wall(2, 0, "S")
    maze.remove_wall(2, 1, "W")
    maze.remove_wall(1, 1, "W")
    maze.remove_wall(0, 1, "S")
    maze.remove_wall(0, 2, "E")
    maze.remove_wall(1, 2, "E")
    assert CycleChecker(maze).has_cycle() is False


# ── 42-pattern cells excluded from node count ───────────────────────────────


def test_42_cells_excluded_from_node_count() -> None:
    """Cells with the 42 pattern (value=15) are excluded from the node count.
    A perfect maze with the 42 pattern must always be cycle-free."""
    gen = MazeGenerator(width=11, height=11, seed=7, perfect=True)
    gen.generate()
    maze = gen.get_maze()
    assert len(maze.forty_two_cells) > 0
    assert CycleChecker(maze).has_cycle() is False
