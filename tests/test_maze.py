# tests/test_maze.py — Unit tests for the Maze data structure.
# Verifies the correct behaviour of the Maze class, in particular:
#   - maze creation with correct dimensions
#   - access and modification of cell walls
#   - detection of inconsistencies between neighbouring cells
#   - detection of forbidden 3x3 open areas
#   - correct placement of the "42" pattern and its detection
#   - hexadecimal encoding of the grid (bits/directions correspondence)
#   - edge cases: 1x1 maze, minimum dimensions, too small for "42"

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


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def maze_5x5() -> Maze:
    return Maze(5, 5, entry=(0, 0), exit=(4, 4))


@pytest.fixture
def maze_3x3() -> Maze:
    return Maze(3, 3, entry=(0, 0), exit=(2, 2))


# ── Initialization ────────────────────────────────────────────────────


def test_init_dimensions(maze_5x5: Maze) -> None:
    assert maze_5x5.width == 5
    assert maze_5x5.height == 5
    assert len(maze_5x5.grid) == 5
    assert len(maze_5x5.grid[0]) == 5


def test_init_all_cells_full_wall(maze_5x5: Maze) -> None:
    """All cells must start at 15 (4 walls)."""
    for row in maze_5x5.grid:
        for cell in row:
            assert cell == 15


def test_init_1x1() -> None:
    maze = Maze(1, 1, entry=(0, 0), exit=(0, 0))
    assert maze.width == 1
    assert maze.height == 1
    assert maze.grid[0][0] == 15


def test_init_rectangular() -> None:
    maze = Maze(10, 3, entry=(0, 0), exit=(9, 2))
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
    """Removing the East wall of (1,1) must also remove the West wall
        of (2,1)."""
    maze_5x5.remove_wall(1, 1, 'E')
    assert maze_5x5.has_wall(1, 1, 'E') is False
    assert maze_5x5.has_wall(2, 1, 'W') is False
    # Other walls must not be affected
    assert maze_5x5.has_wall(1, 1, 'N') is True
    assert maze_5x5.has_wall(1, 1, 'S') is True


def test_remove_wall_west_is_symmetric(maze_5x5: Maze) -> None:
    """Removing the West wall of (2,2) must also remove the East wall
        of (1,2)."""
    maze_5x5.remove_wall(2, 2, 'W')
    assert maze_5x5.has_wall(2, 2, 'W') is False
    assert maze_5x5.has_wall(1, 2, 'E') is False


def test_remove_wall_north_is_symmetric(maze_5x5: Maze) -> None:
    """Removing the North wall of (2,2) must also remove the South wall
         of (2,1)."""
    maze_5x5.remove_wall(2, 2, 'N')
    assert maze_5x5.has_wall(2, 2, 'N') is False
    assert maze_5x5.has_wall(2, 1, 'S') is False


def test_remove_wall_south_is_symmetric(maze_5x5: Maze) -> None:
    """Removing the South wall of (1,1) must also remove the North wall
        of (1,2)."""
    maze_5x5.remove_wall(1, 1, 'S')
    assert maze_5x5.has_wall(1, 1, 'S') is False
    assert maze_5x5.has_wall(1, 2, 'N') is False


def test_remove_wall_east_at_boundary_raises(maze_5x5: Maze) -> None:
    """Removing the East wall of the last column must raise ValueError."""
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
    """set_wall must restore the wall after a remove_wall."""
    maze_5x5.remove_wall(1, 1, 'E')
    assert maze_5x5.has_wall(1, 1, 'E') is False
    maze_5x5.set_wall(1, 1, 'E')
    assert maze_5x5.has_wall(1, 1, 'E') is True


def test_set_wall_invalid_direction_raises(maze_5x5: Maze) -> None:
    with pytest.raises(ValueError):
        maze_5x5.set_wall(1, 1, 'Z')


# ── encode_hex ────────────────────────────────────────────────────────


def test_encode_hex_initial_all_f(maze_3x3: Maze) -> None:
    """Full maze -> all cells encoded as 'F'."""
    hex_str = maze_3x3.encode_hex()
    lines = hex_str.strip().split('\n')
    assert len(lines) == 3
    for line in lines:
        assert line == 'FFF'


def test_encode_hex_changes_after_remove(maze_3x3: Maze) -> None:
    """Removing a wall must change the corresponding hex value."""
    before = maze_3x3.encode_hex()
    maze_3x3.remove_wall(1, 1, 'E')
    after = maze_3x3.encode_hex()
    assert before != after


def test_encode_hex_format(maze_3x3: Maze) -> None:
    """encode_hex returns WIDTH characters per line + \\n."""
    hex_str = maze_3x3.encode_hex()
    lines = hex_str.split('\n')
    # The last line may be empty due to the trailing \n
    non_empty = [li for li in lines if li]
    assert len(non_empty) == 3
    for line in non_empty:
        assert len(line) == 3


# ── add_wall ──────────────────────────────────────────────────────────


def test_add_wall_east_is_symmetric(maze_5x5: Maze) -> None:
    """add_wall(E) must also restore the West wall of the neighbour."""
    maze_5x5.remove_wall(1, 1, 'E')
    maze_5x5.add_wall(1, 1, 'E')
    assert maze_5x5.has_wall(1, 1, 'E') is True
    assert maze_5x5.has_wall(2, 1, 'W') is True


def test_add_wall_south_is_symmetric(maze_5x5: Maze) -> None:
    maze_5x5.remove_wall(2, 2, 'S')
    maze_5x5.add_wall(2, 2, 'S')
    assert maze_5x5.has_wall(2, 2, 'S') is True
    assert maze_5x5.has_wall(2, 3, 'N') is True


def test_add_wall_north_is_symmetric(maze_5x5: Maze) -> None:
    maze_5x5.remove_wall(2, 2, 'N')
    maze_5x5.add_wall(2, 2, 'N')
    assert maze_5x5.has_wall(2, 2, 'N') is True
    assert maze_5x5.has_wall(2, 1, 'S') is True


def test_add_wall_west_is_symmetric(maze_5x5: Maze) -> None:
    maze_5x5.remove_wall(2, 2, 'W')
    maze_5x5.add_wall(2, 2, 'W')
    assert maze_5x5.has_wall(2, 2, 'W') is True
    assert maze_5x5.has_wall(1, 2, 'E') is True


def test_add_wall_invalid_direction_raises(maze_5x5: Maze) -> None:
    with pytest.raises(ValueError):
        maze_5x5.add_wall(1, 1, 'X')


def test_add_wall_at_border_raises(maze_5x5: Maze) -> None:
    """add_wall on a boundary raises ValueError
    (guard condition not met)."""
    with pytest.raises(ValueError):
        maze_5x5.add_wall(0, 0, 'N')  # y=0, condition y>0 is False


# ── place_42_center ───────────────────────────────────────────────────


def test_place_42_center_empty_for_small_maze() -> None:
    """A 4×4 maze is too small → forty_two_cells must be empty."""
    maze = Maze(4, 4)
    assert maze.forty_two_cells == set()


def test_place_42_center_populates_for_large_maze() -> None:
    """An 11×11 maze (≥ pw+4, ph+4) → forty_two_cells must be non-empty."""
    maze = Maze(11, 11)
    assert len(maze.forty_two_cells) > 0


def test_place_42_center_cells_have_value_15() -> None:
    """All cells of the 42 pattern must have value 15."""
    maze = Maze(11, 11)
    for (x, y) in maze.forty_two_cells:
        assert maze.grid[y][x] == 15


def test_place_42_center_is_horizontally_centered() -> None:
    """The pattern is centered: start_x == (width - pattern_width) // 2."""
    maze = Maze(11, 11)
    pw = len(maze.PATTERN_42[0])
    expected_start_x = (11 - pw) // 2
    xs = {x for (x, _) in maze.forty_two_cells}
    assert min(xs) == expected_start_x


def test_place_42_center_is_vertically_centered() -> None:
    maze = Maze(11, 11)
    ph = len(maze.PATTERN_42)
    expected_start_y = (11 - ph) // 2
    ys = {y for (_, y) in maze.forty_two_cells}
    assert min(ys) == expected_start_y


def test_place_42_center_minimum_size() -> None:
    """pw+4 colonnes et ph+4 lignes = taille minimale pour le motif."""
    ph = len(Maze.PATTERN_42)
    pw = len(Maze.PATTERN_42[0])
    maze = Maze(pw + 4, ph + 4)
    assert len(maze.forty_two_cells) > 0


def test_place_42_center_just_below_minimum_empty() -> None:
    """Un pixel en dessous du minimum → aucune cellule 42."""
    ph = len(Maze.PATTERN_42)
    pw = len(Maze.PATTERN_42[0])
    maze = Maze(pw + 3, ph + 4)  # une colonne de moins
    assert maze.forty_two_cells == set()
