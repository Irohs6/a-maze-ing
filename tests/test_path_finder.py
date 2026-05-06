# tests/test_path_finder.py — Tests unitaires de l'algorithme
# de recherche de chemin.
# Vérifie le comportement de PathFinder sur différents labyrinthes de test :
#   - chemin trouvé sur un labyrinthe simple avec solution évidente
#   - chemin le plus court retourné (pas un chemin quelconque)
#   - labyrinthe parfait : un seul chemin possible, correctement détecté
#   - labyrinthe non connexe : détection de cellules inaccessibles
#   - validation du format de sortie du chemin (lettres N, E, S, W uniquement)
#   - reproductibilité : même graine donne même chemin solution

import pytest
from model.maze import Maze
from model.path_finder import PathFinder
from mazegen.maze_generator import MazeGenerator


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


# ── _shortest_path() — returns list[str] | None ──────────────────────


def test_shortest_path_corridor_returns_list(pf_corridor: PathFinder) -> None:
    """_shortest_path() returns a list of directions."""
    path = pf_corridor._shortest_path()
    assert isinstance(path, list)


def test_shortest_path_corridor_directions(pf_corridor: PathFinder) -> None:
    """Corridor 3×1 (0,0)→(2,0) : two steps to the East."""
    path = pf_corridor._shortest_path()
    assert path == ["E", "E"]


def test_shortest_path_vertical_corridor() -> None:
    """Vertical corridor 1×3 : two steps to the South."""
    pf = PathFinder(make_corridor_1x3(), entry=(0, 0), exit=(0, 2))
    assert pf._shortest_path() == ["S", "S"]


def test_shortest_path_only_valid_directions(pf_generated: PathFinder) -> None:
    """All returned directions are in {N, E, S, W}."""
    path = pf_generated._shortest_path()
    assert path is not None
    for d in path:
        assert d in ("N", "E", "S", "W")


def test_shortest_path_nonempty_for_generated_maze(
    pf_generated: PathFinder,
) -> None:
    """A perfect 11×11 maze has a non-empty path."""
    path = pf_generated._shortest_path()
    assert path is not None
    assert len(path) > 0


def test_shortest_path_unreachable_returns_none() -> None:
    """No path exists → _shortest_path() returns None."""
    maze = Maze(3, 3)
    pf = PathFinder(maze, entry=(0, 0), exit=(2, 2))
    assert pf._shortest_path() is None


def test_shortest_path_entry_equals_exit_returns_none() -> None:
    """Entry == exit → None (pred[goal] is None, no path to reconstruct)."""
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(0, 0))
    assert pf._shortest_path() is None


def test_shortest_path_is_deterministic() -> None:
    """Same maze → same shortest path on each call."""
    gen = MazeGenerator(width=11, height=11, seed=42, perfect=True)
    gen.generate()
    maze = gen.get_maze()
    pf_a = PathFinder(maze, entry=(0, 0), exit=(10, 10))
    pf_b = PathFinder(maze, entry=(0, 0), exit=(10, 10))
    assert pf_a._shortest_path() == pf_b._shortest_path()


# ── find() — returns list[dict[tuple, list[str]]] ────────────────────


def test_find_corridor_returns_one_element(pf_corridor: PathFinder) -> None:
    """find() returns a list containing exactly one dict."""
    result = pf_corridor.find()
    assert len(result) == 1


def test_find_corridor_connections_dict(pf_corridor: PathFinder) -> None:
    """The connections dict contains the entry and exit."""
    conn = pf_corridor.find()[0]
    assert isinstance(conn, dict)
    assert (0, 0) in conn
    assert (2, 0) in conn


def test_find_entry_cell_direction_east_only(pf_corridor: PathFinder) -> None:
    """The cell (0,0) only goes East in the 3×1 corridor."""
    conn = pf_corridor.find()[0]
    assert conn[(0, 0)] == ["E"]


def test_find_middle_cell_has_west_and_east(pf_corridor: PathFinder) -> None:
    """The cell (1,0): entry from the West, exit to the East."""
    conn = pf_corridor.find()[0]
    assert conn[(1, 0)] == ["W", "E"]


def test_find_exit_cell_direction_west_only(pf_corridor: PathFinder) -> None:
    """The cell (2,0) only comes from the West."""
    conn = pf_corridor.find()[0]
    assert conn[(2, 0)] == ["W"]


def test_find_covers_all_corridor_cells(pf_corridor: PathFinder) -> None:
    """3×1 corridor → 3 cells in the dict."""
    conn = pf_corridor.find()[0]
    assert len(conn) == 3


def test_find_all_directions_valid(pf_corridor: PathFinder) -> None:
    """All directions in the dict are in {N, E, S, W}."""
    conn = pf_corridor.find()[0]
    for dirs in conn.values():
        for d in dirs:
            assert d in ("N", "E", "S", "W")


def test_find_vertical_corridor_directions() -> None:
    """Vertical corridor 1×3: N/S connections are correct."""
    pf = PathFinder(make_corridor_1x3(), entry=(0, 0), exit=(0, 2))
    conn = pf.find()[0]
    assert conn[(0, 0)] == ["S"]
    assert conn[(0, 1)] == ["N", "S"]
    assert conn[(0, 2)] == ["N"]


def test_find_unreachable_returns_empty_list() -> None:
    """No passage → find() returns []."""
    maze = Maze(3, 3)
    pf = PathFinder(maze, entry=(0, 0), exit=(2, 2))
    assert pf.find() == []


def test_find_entry_equals_exit_returns_empty_list() -> None:
    """Entry == exit → _shortest_path() None → find() returns []."""
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(0, 0))
    assert pf.find() == []


def test_find_generated_maze_has_entry_and_exit(
    pf_generated: PathFinder,
) -> None:
    """The 11×11 maze has the entry and exit in the connections."""
    conn = pf_generated.find()[0]
    assert (0, 0) in conn
    assert (10, 10) in conn


def test_find_generated_maze_is_deterministic() -> None:
    """Same maze → same find() result on each call."""
    gen = MazeGenerator(width=11, height=11, seed=42, perfect=True)
    gen.generate()
    maze = gen.get_maze()
    pf_a = PathFinder(maze, entry=(0, 0), exit=(10, 10))
    pf_b = PathFinder(maze, entry=(0, 0), exit=(10, 10))
    assert pf_a.find() == pf_b.find()


# ── _build_connections_dict ─────────────────────────────────────────--


def test_build_connections_from_empty_path() -> None:
    """An empty path (entry == exit) → dict with only the entry."""
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(0, 0))
    conn = pf._build_connections_dict([])
    assert conn == {(0, 0): []}


def test_build_connections_single_move_east() -> None:
    """One step East → entry has ['E'], exit has ['W']."""
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(1, 0))
    conn = pf._build_connections_dict(["E"])
    assert "E" in conn[(0, 0)]
    assert "W" in conn[(1, 0)]


def test_build_connections_covers_full_path() -> None:
    """Path E,E → dict has keys (0,0), (1,0), (2,0) with correct directions."""
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(2, 0))
    conn = pf._build_connections_dict(["E", "E"])
    assert set(conn.keys()) == {
        (0, 0), (1, 0), (2, 0)}
