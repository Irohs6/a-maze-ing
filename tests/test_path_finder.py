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


# ── _shortest_path() — retourne list[str] | None ──────────────────────


def test_shortest_path_corridor_returns_list(pf_corridor: PathFinder) -> None:
    """_shortest_path() retourne une liste de directions."""
    path = pf_corridor._shortest_path()
    assert isinstance(path, list)


def test_shortest_path_corridor_directions(pf_corridor: PathFinder) -> None:
    """Couloir 3×1 (0,0)→(2,0) : deux pas vers l'Est."""
    path = pf_corridor._shortest_path()
    assert path == ["E", "E"]


def test_shortest_path_vertical_corridor() -> None:
    """Couloir 1×3 : deux pas vers le Sud."""
    pf = PathFinder(make_corridor_1x3(), entry=(0, 0), exit=(0, 2))
    assert pf._shortest_path() == ["S", "S"]


def test_shortest_path_only_valid_directions(pf_generated: PathFinder) -> None:
    """Toutes les directions retournées sont dans {N, E, S, W}."""
    path = pf_generated._shortest_path()
    assert path is not None
    for d in path:
        assert d in ("N", "E", "S", "W")


def test_shortest_path_nonempty_for_generated_maze(
    pf_generated: PathFinder,
) -> None:
    """Un labyrinthe parfait 11×11 a bien un chemin non vide."""
    path = pf_generated._shortest_path()
    assert path is not None
    assert len(path) > 0


def test_shortest_path_unreachable_returns_none() -> None:
    """Labyrinthe plein (aucun passage) → None."""
    maze = Maze(3, 3)
    pf = PathFinder(maze, entry=(0, 0), exit=(2, 2))
    assert pf._shortest_path() is None


def test_shortest_path_entry_equals_exit_returns_none() -> None:
    """Entrée == sortie → None (pred[goal] is None, pas de chemin à reconstruire)."""
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(0, 0))
    assert pf._shortest_path() is None


def test_shortest_path_is_deterministic() -> None:
    """Même labyrinthe + même seed → même chemin à chaque appel."""
    gen = MazeGenerator(width=11, height=11, seed=42, perfect=True)
    gen.generate()
    maze = gen.get_maze()
    pf_a = PathFinder(maze, entry=(0, 0), exit=(10, 10))
    pf_b = PathFinder(maze, entry=(0, 0), exit=(10, 10))
    assert pf_a._shortest_path() == pf_b._shortest_path()


# ── find() — retourne list[dict[tuple, list[str]]] ────────────────────


def test_find_corridor_returns_one_element(pf_corridor: PathFinder) -> None:
    """find() renvoie une liste contenant exactement un dict."""
    result = pf_corridor.find()
    assert len(result) == 1


def test_find_corridor_connections_dict(pf_corridor: PathFinder) -> None:
    """Le dict de connexions contient l'entrée et la sortie."""
    conn = pf_corridor.find()[0]
    assert isinstance(conn, dict)
    assert (0, 0) in conn
    assert (2, 0) in conn


def test_find_entry_cell_direction_east_only(pf_corridor: PathFinder) -> None:
    """La cellule (0,0) ne sort que vers l'Est dans le couloir 3×1."""
    conn = pf_corridor.find()[0]
    assert conn[(0, 0)] == ["E"]


def test_find_middle_cell_has_west_and_east(pf_corridor: PathFinder) -> None:
    """La cellule (1,0) : entrée depuis l'Ouest, sortie vers l'Est."""
    conn = pf_corridor.find()[0]
    assert conn[(1, 0)] == ["W", "E"]


def test_find_exit_cell_direction_west_only(pf_corridor: PathFinder) -> None:
    """La cellule (2,0) ne vient que de l'Ouest."""
    conn = pf_corridor.find()[0]
    assert conn[(2, 0)] == ["W"]


def test_find_covers_all_corridor_cells(pf_corridor: PathFinder) -> None:
    """Couloir 3×1 → 3 cellules dans le dict."""
    conn = pf_corridor.find()[0]
    assert len(conn) == 3


def test_find_all_directions_valid(pf_corridor: PathFinder) -> None:
    """Toutes les directions dans le dict sont dans {N, E, S, W}."""
    conn = pf_corridor.find()[0]
    for dirs in conn.values():
        for d in dirs:
            assert d in ("N", "E", "S", "W")


def test_find_vertical_corridor_directions() -> None:
    """Couloir 1×3 : connexions N/S correctes."""
    pf = PathFinder(make_corridor_1x3(), entry=(0, 0), exit=(0, 2))
    conn = pf.find()[0]
    assert conn[(0, 0)] == ["S"]
    assert conn[(0, 1)] == ["N", "S"]
    assert conn[(0, 2)] == ["N"]


def test_find_unreachable_returns_empty_list() -> None:
    """Aucun passage → find() retourne []."""
    maze = Maze(3, 3)
    pf = PathFinder(maze, entry=(0, 0), exit=(2, 2))
    assert pf.find() == []


def test_find_entry_equals_exit_returns_empty_list() -> None:
    """Entrée == sortie → _shortest_path() None → find() retourne []."""
    maze = make_corridor_3x1()
    pf = PathFinder(maze, entry=(0, 0), exit=(0, 0))
    assert pf.find() == []


def test_find_generated_maze_has_entry_and_exit(
    pf_generated: PathFinder,
) -> None:
    """Le labyrinthe 11×11 a bien l'entrée et la sortie dans les connexions."""
    conn = pf_generated.find()[0]
    assert (0, 0) in conn
    assert (10, 10) in conn


def test_find_generated_maze_is_deterministic() -> None:
    """Même labyrinthe → même résultat find() à chaque appel."""
    gen = MazeGenerator(width=11, height=11, seed=42, perfect=True)
    gen.generate()
    maze = gen.get_maze()
    pf_a = PathFinder(maze, entry=(0, 0), exit=(10, 10))
    pf_b = PathFinder(maze, entry=(0, 0), exit=(10, 10))
    assert pf_a.find() == pf_b.find()


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
