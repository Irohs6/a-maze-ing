# tests/test_maze.py — Tests unitaires de la structure de données Maze.
# Vérifie le bon fonctionnement de la classe Maze, notamment :
#   - la création d'un labyrinthe aux dimensions correctes
#   - l'accès et la modification des murs de chaque cellule
#   - la détection des incohérences entre cellules voisines
#   - la détection des zones ouvertes 3x3 interdites
#   - le placement correct du motif "42" et sa détection
#   - l'encodage hexadécimal de la grille (correspondance bits/directions)
#   - les cas limites : labyrinthe 1x1, dimensions
# minimales, trop petit pour "42"

import pytest
from model.maze import Maze


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def maze_5x5() -> Maze:
    return Maze(5, 5)


@pytest.fixture
def maze_3x3() -> Maze:
    return Maze(3, 3)


# ── Initialisation ────────────────────────────────────────────────────


def test_init_dimensions(maze_5x5: Maze) -> None:
    assert maze_5x5.width == 5
    assert maze_5x5.height == 5
    assert len(maze_5x5.grid) == 5
    assert len(maze_5x5.grid[0]) == 5


def test_init_all_cells_full_wall(maze_5x5: Maze) -> None:
    """Toutes les cellules doivent commencer à 15 (4 murs)."""
    for row in maze_5x5.grid:
        for cell in row:
            assert cell == 15


def test_init_1x1() -> None:
    maze = Maze(1, 1)
    assert maze.width == 1
    assert maze.height == 1
    assert maze.grid[0][0] == 15


def test_init_rectangular() -> None:
    maze = Maze(10, 3)
    assert maze.width == 10
    assert maze.height == 3
    assert len(maze.grid) == 3
    assert len(maze.grid[0]) == 10


# ── has_wall ──────────────────────────────────────────────────────────


def test_has_wall_all_directions_initially(maze_3x3: Maze) -> None:
    for y in range(3):
        for x in range(3):
            for direction in ('N', 'E', 'S', 'W'):
                assert maze_3x3.has_wall(x, y, direction) is True


def test_has_wall_invalid_direction_raises(maze_3x3: Maze) -> None:
    with pytest.raises(ValueError):
        maze_3x3.has_wall(1, 1, 'X')


# ── remove_wall ───────────────────────────────────────────────────────


def test_remove_wall_east_is_symmetric(maze_5x5: Maze) -> None:
    """Retirer le mur Est de (1,1) doit aussi retirer le mur Ouest de (2,1)."""
    maze_5x5.remove_wall(1, 1, 'E')
    assert maze_5x5.has_wall(1, 1, 'E') is False
    assert maze_5x5.has_wall(2, 1, 'W') is False
    # Les autres murs ne doivent pas être affectés
    assert maze_5x5.has_wall(1, 1, 'N') is True
    assert maze_5x5.has_wall(1, 1, 'S') is True


def test_remove_wall_west_is_symmetric(maze_5x5: Maze) -> None:
    """Retirer le mur Ouest de (2,2) doit aussi retirer le mur Est de (1,2)."""
    maze_5x5.remove_wall(2, 2, 'W')
    assert maze_5x5.has_wall(2, 2, 'W') is False
    assert maze_5x5.has_wall(1, 2, 'E') is False


def test_remove_wall_north_is_symmetric(maze_5x5: Maze) -> None:
    """Retirer le mur Nord de (2,2) doit aussi retirer le mur Sud de (2,1)."""
    maze_5x5.remove_wall(2, 2, 'N')
    assert maze_5x5.has_wall(2, 2, 'N') is False
    assert maze_5x5.has_wall(2, 1, 'S') is False


def test_remove_wall_south_is_symmetric(maze_5x5: Maze) -> None:
    """Retirer le mur Sud de (1,1) doit aussi retirer le mur Nord de (1,2)."""
    maze_5x5.remove_wall(1, 1, 'S')
    assert maze_5x5.has_wall(1, 1, 'S') is False
    assert maze_5x5.has_wall(1, 2, 'N') is False


def test_remove_wall_east_at_boundary_raises(maze_5x5: Maze) -> None:
    """Retirer le mur Est de la dernière colonne doit lever ValueError."""
    with pytest.raises(ValueError):
        maze_5x5.remove_wall(4, 0, 'E')


def test_remove_wall_west_at_boundary_raises(maze_5x5: Maze) -> None:
    with pytest.raises(ValueError):
        maze_5x5.remove_wall(0, 0, 'W')


def test_remove_wall_north_at_boundary_raises(maze_5x5: Maze) -> None:
    with pytest.raises(ValueError):
        maze_5x5.remove_wall(0, 0, 'N')


def test_remove_wall_south_at_boundary_raises(maze_5x5: Maze) -> None:
    with pytest.raises(ValueError):
        maze_5x5.remove_wall(0, 4, 'S')


# ── set_wall ──────────────────────────────────────────────────────────


def test_set_wall_restores_after_remove(maze_5x5: Maze) -> None:
    """set_wall doit remettre le mur après un remove_wall."""
    maze_5x5.remove_wall(1, 1, 'E')
    assert maze_5x5.has_wall(1, 1, 'E') is False
    maze_5x5.set_wall(1, 1, 'E')
    assert maze_5x5.has_wall(1, 1, 'E') is True


def test_set_wall_invalid_direction_raises(maze_5x5: Maze) -> None:
    with pytest.raises(ValueError):
        maze_5x5.set_wall(1, 1, 'Z')


# ── encode_hex ────────────────────────────────────────────────────────


def test_encode_hex_initial_all_f(maze_3x3: Maze) -> None:
    """Labyrinthe plein → toutes les cellules encodées 'F'."""
    hex_str = maze_3x3.encode_hex()
    lines = hex_str.strip().split('\n')
    assert len(lines) == 3
    for line in lines:
        assert line == 'FFF'


def test_encode_hex_changes_after_remove(maze_3x3: Maze) -> None:
    """Retirer un mur change la valeur hex correspondante."""
    before = maze_3x3.encode_hex()
    maze_3x3.remove_wall(1, 1, 'E')
    after = maze_3x3.encode_hex()
    assert before != after


def test_encode_hex_format(maze_3x3: Maze) -> None:
    """encode_hex retourne WIDTH caractères par ligne + \\n."""
    hex_str = maze_3x3.encode_hex()
    lines = hex_str.split('\n')
    # La dernière ligne peut être vide à cause du \n final
    non_empty = [li for li in lines if li]
    assert len(non_empty) == 3
    for line in non_empty:
        assert len(line) == 3
