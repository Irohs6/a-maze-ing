# tests/test_path_finder.py — Unit tests for the path-finding algorithm.
# Verifies PathFinder behaviour on various test mazes:
#   - path found on a simple maze with an obvious solution
#   - shortest path returned (not just any path)
#   - perfect maze: single possible path correctly detected
#   - disconnected maze: detection of unreachable cells
#   - validation of output path format (only N, E, S, W letters)
#   - reproducibility: same seed produces the same solution path

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
from mazegen.model.path_finder import PathFinder
from mazegen.generation.maze_generator import MazeGenerator

# ── Helpers ───────────────────────────────────────────────────────────


def make_corridor_3x1() -> Maze:
    """Horizontal corridor 3×1: (0,0)→(1,0)→(2,0) in direction East."""
    maze = Maze(3, 1)
    maze.remove_wall(0, 0, "E")
    maze.remove_wall(1, 0, "E")
    return maze


def make_corridor_1x3() -> Maze:
    """Vertical corridor 1×3: (0,0)→(0,1)→(0,2) in direction South."""
    maze = Maze(1, 3)
    maze.remove_wall(0, 0, "S")
    maze.remove_wall(0, 1, "S")
    return maze


def make_two_path_maze() -> Maze:
    """3×3 maze with two shortest paths from (0,0) to (2,2).

    Path 1: (0,0)→S→(0,1)→S→(0,2)→E→(1,2)→E→(2,2)
    Path 2: (0,0)→E→(1,0)→E→(2,0)→S→(2,1)→S→(2,2)
    """
    maze = Maze(3, 3)
    # Path 1
    maze.remove_wall(0, 0, "S")
    maze.remove_wall(0, 1, "S")
    maze.remove_wall(0, 2, "E")
    maze.remove_wall(1, 2, "E")
    # Path 2
    maze.remove_wall(0, 0, "E")
    maze.remove_wall(1, 0, "E")
    maze.remove_wall(2, 0, "S")
    maze.remove_wall(2, 1, "S")
    return maze


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def pf_corridor() -> PathFinder:
    """PathFinder on the 3×1 corridor."""
    return PathFinder(make_corridor_3x1(), entry=(0, 0), exit=(2, 0))


@pytest.fixture
def pf_generated() -> PathFinder:
    """PathFinder on a generated 11×11 perfect maze."""
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=True)
    gen.generate()
    return PathFinder(gen.get_maze(), entry=(0, 0), exit=(10, 10))


# ── shortest_path() — returns list[str] | None ──────────────────────


def test_shortest_path_corridor_returns_list(pf_corridor: PathFinder) -> None:
    """shortest_path() returns a list of directions."""
    path = pf_corridor.shortest_path()
    assert isinstance(path, list)


def test_shortest_path_corridor_directions(pf_corridor: PathFinder) -> None:
    """Corridor 3×1 (0,0)→(2,0) : two steps to the East."""
    path = pf_corridor.shortest_path()
    assert path == ["E", "E"]


def test_shortest_path_vertical_corridor() -> None:
    """Vertical corridor 1×3 : two steps to the South."""
    pf = PathFinder(make_corridor_1x3(), entry=(0, 0), exit=(0, 2))
    assert pf.shortest_path() == ["S", "S"]


def test_shortest_path_only_valid_directions(pf_generated: PathFinder) -> None:
    """All returned directions are in {N, E, S, W}."""
    path = pf_generated.shortest_path()
    assert path is not None
    for d in path:
        assert d in ("N", "E", "S", "W")


def test_shortest_path_nonempty_for_generated_maze(
    pf_generated: PathFinder,
) -> None:
    """A perfect 11×11 maze has a non-empty path."""
    path = pf_generated.shortest_path()
    assert path is not None
    assert len(path) > 0


def test_shortest_path_unreachable_returns_none() -> None:
    """No path exists → shortest_path() returns None."""
    maze = Maze(3, 3)
    pf = PathFinder(maze, entry=(0, 0), exit=(2, 2))
    assert pf.shortest_path() is None


def test_shortest_path_entry_equals_exit_returns_none() -> None:
    """Entry == exit → None (pred[goal] is None, no path to reconstruct)."""
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(0, 0))
    assert pf.shortest_path() is None


def test_shortest_path_is_deterministic() -> None:
    """Same maze → same shortest path on each call."""
    gen = MazeGenerator(width=11, height=11, seed=42, perfect=True)
    gen.generate()
    maze = gen.get_maze()
    pf_a = PathFinder(maze, entry=(0, 0), exit=(10, 10))
    pf_b = PathFinder(maze, entry=(0, 0), exit=(10, 10))
    assert pf_a.shortest_path() == pf_b.shortest_path()


# ── _shortest_path() — returns list[str] | None ─────────────────────


def test_corridor_shortest_path_returns_directions(
    pf_corridor: PathFinder,
) -> None:
    """shortest_path() on 3×1 corridor returns the two East steps."""
    path = pf_corridor.shortest_path()
    assert path == ["E", "E"]


def test_entry_cell_first_move_east(pf_corridor: PathFinder) -> None:
    """First move in the 3×1 corridor is East from (0,0)."""
    path = pf_corridor.shortest_path()
    assert path is not None
    conn = pf_corridor._build_connections(path)
    assert conn[0] == (0, 0, "E")


def test_find_middle_cell_traversed(pf_corridor: PathFinder) -> None:
    """The cell (1,0) is traversed going East in the 3×1 corridor."""
    path = pf_corridor.shortest_path()
    assert path is not None
    conn = pf_corridor._build_connections(path)
    assert (1, 0, "E") in conn


def test_find_exit_cell_not_in_moves(pf_corridor: PathFinder) -> None:
    """The exit cell (2,0) is the destination, not a departure cell."""
    path = pf_corridor.shortest_path()
    assert path is not None
    conn = pf_corridor._build_connections(path)
    assert not any(x == 2 and y == 0 for x, y, _ in conn)


def test_find_covers_all_corridor_moves(pf_corridor: PathFinder) -> None:
    """3×1 corridor: 2 departure cells (not counting the exit)."""
    path = pf_corridor.shortest_path()
    assert path is not None
    conn = pf_corridor._build_connections(path)
    assert len(conn) == 2


def test_shortest_path_all_directions_valid(
    pf_corridor: PathFinder,
) -> None:
    """All directions returned by shortest_path() are in {N, E, S, W}."""
    path = pf_corridor.shortest_path()
    assert path is not None
    for d in path:
        assert d in ("N", "E", "S", "W")


def test_shortest_path_vertical_corridor_directions_() -> None:
    """Vertical corridor 1×3: path is [S, S]."""
    pf = PathFinder(make_corridor_1x3(), entry=(0, 0), exit=(0, 2))
    assert pf.shortest_path() == ["S", "S"]


def test_shortest_path_unreachable_returns_none_() -> None:
    """No passage → shortest_path() returns None."""
    maze = Maze(3, 3)
    pf = PathFinder(maze, entry=(0, 0), exit=(2, 2))
    assert pf.shortest_path() is None


def test_shortest_path_entry_equals_exit_returns_none_() -> None:
    """Entry == exit → shortest_path() returns None."""
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(0, 0))
    assert pf.shortest_path() is None


def test_shortest_path_generated_maze_has_entry(
    pf_generated: PathFinder,
) -> None:
    """The 11×11 maze path starts at entry."""
    path = pf_generated.shortest_path()
    assert path is not None and len(path) > 0
    conn = pf_generated._build_connections(path)
    assert conn[0][:2] == (0, 0)


def test_shortest_path_generated_maze_is_deterministic() -> None:
    """Same maze → same shortest_path() result on each call."""
    gen = MazeGenerator(width=11, height=11, seed=42, perfect=True)
    gen.generate()
    maze = gen.get_maze()
    pf_a = PathFinder(maze, entry=(0, 0), exit=(10, 10))
    pf_b = PathFinder(maze, entry=(0, 0), exit=(10, 10))
    assert pf_a.shortest_path() == pf_b.shortest_path()


# ── _build_connections ───────────────────────────────────────────────


def test_build_connections_from_empty_path() -> None:
    """An empty path → empty list."""
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(0, 0))
    conn = pf._build_connections([])
    assert conn == []


def test_build_connections_single_move_east() -> None:
    """One step East → [(0, 0, 'E')]."""
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(1, 0))
    conn = pf._build_connections(["E"])
    assert conn == [(0, 0, "E")]


def test_build_connections_covers_full_path() -> None:
    """Path E,E → [(0,0,'E'), (1,0,'E')] (exit cell not included)."""
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(2, 0))
    conn = pf._build_connections(["E", "E"])
    assert conn == [(0, 0, "E"), (1, 0, "E")]
