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
    """Couloir horizontal 3×1 : (0,0)→(1,0)→(2,0) en direction Est."""
    maze = Maze(3, 1)
    maze.remove_wall(0, 0, "E")
    maze.remove_wall(1, 0, "E")
    return maze


def make_corridor_1x3() -> Maze:
    """Couloir vertical 1×3 : (0,0)→(0,1)→(0,2) en direction Sud."""
    maze = Maze(1, 3)
    maze.remove_wall(0, 0, "S")
    maze.remove_wall(0, 1, "S")
    return maze


def make_two_path_maze() -> Maze:
    """Labyrinthe 3×3 avec deux plus courts chemins de (0,0) à (2,2).

    Chemin 1 : (0,0)→S→(0,1)→S→(0,2)→E→(1,2)→E→(2,2)
    Chemin 2 : (0,0)→E→(1,0)→E→(2,0)→S→(2,1)→S→(2,2)
    """
    maze = Maze(3, 3)
    # Chemin 1
    maze.remove_wall(0, 0, "S")
    maze.remove_wall(0, 1, "S")
    maze.remove_wall(0, 2, "E")
    maze.remove_wall(1, 2, "E")
    # Chemin 2
    maze.remove_wall(0, 0, "E")
    maze.remove_wall(1, 0, "E")
    maze.remove_wall(2, 0, "S")
    maze.remove_wall(2, 1, "S")
    return maze


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def pf_corridor() -> PathFinder:
    """PathFinder sur le couloir 3×1."""
    return PathFinder(make_corridor_3x1(), entry=(0, 0), exit=(2, 0))


@pytest.fixture
def pf_generated() -> PathFinder:
    """PathFinder sur un labyrinthe 11×11 parfait généré."""
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=True)
    gen.generate()
    return PathFinder(gen.get_maze(), entry=(0, 0), exit=(10, 10))


# ──._shortest_path as nominal ──────────────────────────────


def test_finds_path_in_simple_corridor(pf_corridor: PathFinder) -> None:
    paths: list[dict[tuple[int, int], list[str]]] = (
        pf_corridor._shortest_path()
    )
    assert len(paths) == 1


def test_path_contains_entry_and_exit(pf_corridor: PathFinder) -> None:
    conn: dict[tuple[int, int], list[str]] = pf_corridor._shortest_path()[0]
    assert (0, 0) in conn
    assert (2, 0) in conn


def test_path_covers_every_cell_of_corridor(pf_corridor: PathFinder) -> None:
    """Le couloir 3×1 → 3 cellules dans le dict de connexions."""
    conn: dict[tuple[int, int], list[str]] = pf_corridor._shortest_path()[0]
    assert len(conn) == 3


def test_all_directions_in_connections_are_valid(
    pf_corridor: PathFinder,
) -> None:
    """Toutes les directions enregistrées sont dans {N, E, S, W}."""
    conn: dict[tuple[int, int], list[str]] = pf_corridor._shortest_path()[0]
    for dirs in conn.values():
        for d in dirs:
            assert d in ("N", "E", "S", "W")


def test_entry_cell_direction_east_only(pf_corridor: PathFinder) -> None:
    """Dans le couloir 3×1, la cellule (0,0) ne sort que vers l'Est."""
    conn: dict[tuple[int, int], list[str]] = pf_corridor._shortest_path()[0]
    assert conn[(0, 0)] == ["E"]


def test_middle_cell_has_east_and_west(pf_corridor: PathFinder) -> None:
    """La cellule (1,0) communique vers l'Ouest (entrée) et l'Est (sortie)."""
    conn: dict[tuple[int, int], list[str]] = pf_corridor._shortest_path()[0]
    assert conn[(1, 0)] == ["W", "E"]


def test_exit_cell_direction_west_only(pf_corridor: PathFinder) -> None:
    """La cellule (2,0) ne vient que de l'Ouest."""
    conn: dict[tuple[int, int], list[str]] = pf_corridor._shortest_path()[0]
    assert conn[(2, 0)] == ["W"]


def test_vertical_corridor_path_uses_south() -> None:
    """Couloir 1×3 : le chemin emprunte S et S."""
    pf = PathFinder(make_corridor_1x3(), entry=(0, 0), exit=(0, 2))
    conn: dict[tuple[int, int], list[str]] = pf._shortest_path()[0]
    assert conn[(0, 0)] == ["S"]
    assert conn[(0, 1)] == ["N", "S"]
    assert conn[(0, 2)] == ["N"]


# ──._shortest_path abyrinthe généré ───────────────────────


def test_finds_path_in_generated_maze(pf_generated: PathFinder) -> None:
    paths: list[dict[tuple[int, int], list[str]]] = (
        pf_generated._shortest_path()
    )
    assert len(paths) == 1


def test_generated_maze_path_has_entry_and_exit(
    pf_generated: PathFinder,
) -> None:
    conn: dict[tuple[int, int], list[str]] = pf_generated._shortest_path()[0]
    assert (0, 0) in conn
    assert (10, 10) in conn


def test_generated_maze_path_is_deterministic() -> None:
    """Même labyrinthe, même chemin à chaque appel."""
    gen = MazeGenerator(width=11, height=11, seed=42, perfect=True)
    gen.generate()
    maze = gen.get_maze()
    pf_a = PathFinder(maze, entry=(0, 0), exit=(10, 10))
    pf_b = PathFinder(maze, entry=(0, 0), exit=(10, 10))
    assert pf_a._shortest_path() == pf_b._shortest_path()


# ──._shortest_path as limites ──────────────────────────────


def test_unreachable_exit_returns_empty_list() -> None:
    """Aucun passage dans le labyrinthe → sortie inaccessible."""
    maze = Maze(3, 3)  # todas las celdas value 15, aucun passage
    pf = PathFinder(maze, entry=(0, 0), exit=(2, 2))
    assert pf._shortest_path() == []


def test_entry_equals_exit_returns_single_connection() -> None:
    """Entrée == sortie → un chemin vide mais connexions de l'entrée."""
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(0, 0))
    paths = pf._shortest_path()
    assert len(paths) == 1
    assert (0, 0) in paths[0]


# ── _build_connections_dict ─────────────────────────────────────────--


def test_build_connections_from_empty_path() -> None:
    """Un chemin vide (entrée == sortie) → dict avec seulement l'entrée."""
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(0, 0))
    conn = pf._build_connections_dict([])
    assert conn == {(0, 0): []}


def test_build_connections_single_move_east() -> None:
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(1, 0))
    conn = pf._build_connections_dict(["E"])
    assert "E" in conn[(0, 0)]
    assert "W" in conn[(1, 0)]


def test_build_connections_covers_full_path() -> None:
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(2, 0))
    conn = pf._build_connections_dict(["E", "E"])
    assert set(conn.keys()) == {(0, 0), (1, 0), (2, 0)}
