# tests/test_maze_validator.py — Unit tests for MazeValidator.
# Verifies the validation rules applied to the maze structure:
#   - _validate_cell_values     : bounds [0, 15]
#   - _validate_maze_boundaries : outer walls intact
#   - _validate_adjacent_cells  : symmetry N↔S, E↔W
#   - _has_forbidden_open_areas : forbidden 3×3 areas
#   - _validate_maze_connectivity : all non-isolated cells reachable from (0,0)
#   - _validate_42_pattern      : "42" pattern correctly placed (or absent
# if too small)
#   - validate()                : global orchestration

import sys
try:
    import pytest
except ImportError:
    print("\033c", end="")
    print(
        "Pytest not found, try starting the program with 'make run' command."
    )
    sys.exit(7)
from model.maze import Maze
from model.maze_validator import MazeValidator
from mazegen.maze_generator import MazeGenerator

# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def valid_11x11() -> Maze:
    """Perfect 11x11 maze generated with a fixed seed."""
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=True)
    gen.generate()
    return gen.get_maze()


@pytest.fixture
def valid_5x5() -> Maze:
    """Perfect 5x5 maze generated (too small for the 42 pattern)."""
    gen = MazeGenerator(width=5, height=5, seed=1, perfect=True)
    gen.generate()
    return gen.get_maze()


# ── validate() — orchestration globale ───────────────────────────────


def test_validate_perfect_maze_11x11(valid_11x11: Maze) -> None:
    assert MazeValidator(valid_11x11).validate() is True


def test_validate_perfect_maze_5x5(valid_5x5: Maze) -> None:
    assert MazeValidator(valid_5x5).validate() is True


def test_validate_kruksal_maze_is_valid() -> None:
    gen = MazeGenerator(width=11, height=11, seed=3, perfect=False)
    gen.generate()
    assert MazeValidator(gen.get_maze()).validate() is True


def test_validate_full_wall_maze_passes_as_all_isolated() -> None:
    """All cells equal 15 -> all are 'isolated' -> connectivity OK."""
    maze = Maze(3, 3)
    assert MazeValidator(maze).validate() is True


# ── _validate_cell_values ─────────────────────────────────────────────


def test_cell_values_all_valid_initially() -> None:
    maze = Maze(4, 4)
    assert MazeValidator(maze)._validate_cell_values() is True


def test_cell_value_16_invalid() -> None:
    maze = Maze(4, 4)
    maze.grid[1][1] = 16
    assert MazeValidator(maze)._validate_cell_values() is False


def test_cell_value_negative_invalid() -> None:
    maze = Maze(4, 4)
    maze.grid[0][0] = -1
    assert MazeValidator(maze)._validate_cell_values() is False


def test_cell_value_zero_valid() -> None:
    """Value 0 (no wall) is in [0, 15] -> valid."""
    maze = Maze(4, 4)
    maze.grid[2][2] = 0
    assert MazeValidator(maze)._validate_cell_values() is True


def test_cell_value_15_valid() -> None:
    maze = Maze(4, 4)
    assert MazeValidator(maze)._validate_cell_values() is True


# ── _validate_maze_boundaries ─────────────────────────────────────────


def test_boundaries_full_wall_maze_valid() -> None:
    maze = Maze(4, 4)
    assert MazeValidator(maze)._validate_maze_boundaries() is True


def test_boundary_north_wall_removed_fails() -> None:
    maze = Maze(4, 4)
    maze.grid[0][1] &= ~1  # directly remove the N wall of cell (1, 0)
    assert MazeValidator(maze)._validate_maze_boundaries() is False


def test_boundary_south_wall_removed_fails() -> None:
    maze = Maze(4, 4)
    maze.grid[3][2] &= ~4  # remove the S wall of (2, 3)
    assert MazeValidator(maze)._validate_maze_boundaries() is False


def test_boundary_west_wall_removed_fails() -> None:
    maze = Maze(4, 4)
    maze.grid[1][0] &= ~8  # remove the W wall of (0, 1)
    assert MazeValidator(maze)._validate_maze_boundaries() is False


def test_boundary_east_wall_removed_fails() -> None:
    maze = Maze(4, 4)
    maze.grid[1][3] &= ~2  # remove the E wall of (3, 1)
    assert MazeValidator(maze)._validate_maze_boundaries() is False


def test_boundaries_valid_in_generated_maze(valid_11x11: Maze) -> None:
    assert MazeValidator(valid_11x11)._validate_maze_boundaries() is True


# ── _validate_adjacent_cells ──────────────────────────────────────────


def test_adjacent_cells_consistent_after_remove_wall() -> None:
    maze = Maze(5, 5)
    maze.remove_wall(2, 2, "E")
    assert MazeValidator(maze)._validate_adjacent_cells() is True


def test_adjacent_cells_asymmetric_east_west_fails() -> None:
    """Remove the East wall of (1,1) without
        removing the West wall of (2,1)."""
    maze = Maze(5, 5)
    maze.grid[1][1] &= ~2  # direct manipulation, no symmetry
    assert MazeValidator(maze)._validate_adjacent_cells() is False


def test_adjacent_cells_asymmetric_north_south_fails() -> None:
    """Remove the South wall of (1,1) without removing
    the North wall of (1,2)."""
    maze = Maze(5, 5)
    maze.grid[1][1] &= ~4  # only remove S from (1,1)
    assert MazeValidator(maze)._validate_adjacent_cells() is False


def test_adjacent_cells_valid_in_generated_maze(valid_11x11: Maze) -> None:
    assert MazeValidator(valid_11x11)._validate_adjacent_cells() is True


# ── _has_forbidden_open_areas ─────────────────────────────────────────


def test_no_forbidden_areas_in_full_wall_maze() -> None:
    maze = Maze(5, 5)
    assert MazeValidator(maze)._has_forbidden_open_areas() is False


def test_3x3_open_area_detected() -> None:
    """Fully open 3x3 block at (1,1) -> forbidden area."""
    maze = Maze(5, 5)
    # Open all East horizontal walls of the block (columns 1->2 and 2->3)
    for y in range(1, 4):
        for x in range(1, 3):
            maze.remove_wall(x, y, "E")
    # Open all South vertical walls of the block (rows 1->2 and 2->3)
    for y in range(1, 3):
        for x in range(1, 4):
            maze.remove_wall(x, y, "S")
    assert MazeValidator(maze)._has_forbidden_open_areas() is True


def test_2x2_open_area_not_forbidden() -> None:
    """An open 2x2 block is allowed (only 3x3 is forbidden)."""
    maze = Maze(5, 5)
    maze.remove_wall(1, 1, "E")
    maze.remove_wall(1, 1, "S")
    maze.remove_wall(2, 1, "S")
    maze.remove_wall(1, 2, "E")
    assert MazeValidator(maze)._has_forbidden_open_areas() is False


def test_no_forbidden_areas_in_generated_maze(valid_11x11: Maze) -> None:
    assert MazeValidator(valid_11x11)._has_forbidden_open_areas() is False


# ── _validate_maze_connectivity ───────────────────────────────────────


def test_connectivity_passes_for_generated_maze(valid_11x11: Maze) -> None:
    assert MazeValidator(valid_11x11)._validate_maze_connectivity() is True


def test_connectivity_passes_for_full_wall_maze() -> None:
    """All cells are isolated (15) -> connectivity passes automatically."""
    maze = Maze(4, 4)
    assert MazeValidator(maze)._validate_maze_connectivity() is True


def test_connectivity_fails_when_cells_unreachable() -> None:
    """Opening (3,3)<->(4,3) creates two non-15 cells
    unreachable from (0,0)."""
    maze = Maze(5, 5)
    maze.remove_wall(3, 3, "E")
    assert MazeValidator(maze)._validate_maze_connectivity() is False


def test_connectivity_fails_for_partial_generation() -> None:
    """An isolated passage far from the top-left corner breaks connectivity."""
    maze = Maze(7, 7)
    maze.remove_wall(5, 5, "S")
    assert MazeValidator(maze)._validate_maze_connectivity() is False


# ── _validate_42_pattern ──────────────────────────────────────────────


def test_42_pattern_valid_in_large_maze(valid_11x11: Maze) -> None:
    assert MazeValidator(valid_11x11)._validate_42_pattern() is True


def test_42_pattern_skipped_for_too_narrow_maze() -> None:
    """Maze width < 7 (pattern width) -> validation skipped."""
    maze = Maze(5, 5)
    assert MazeValidator(maze)._validate_42_pattern() is True


def test_42_pattern_skipped_when_no_isolated_cell() -> None:
    """Without any cell with value 15, pattern check is skipped."""
    maze = Maze(11, 11)
    for y in range(maze.height):
        for x in range(maze.width):
            maze.grid[y][x] = 0
    assert MazeValidator(maze)._validate_42_pattern() is True


def test_42_pattern_fails_when_pattern_missing_in_large_maze() -> None:
    """An 11x11 with cells valued 15 but without the '42' pattern
    - validation fails."""
    maze = Maze(11, 11)
    # Clear all cells of the 42 pattern placed by __init__
    # but leave one isolated cell elsewhere
    for y in range(maze.height):
        for x in range(maze.width):
            maze.grid[y][x] = 0
    maze.grid[0][0] = 15  # isolated cell, but not at the 42 pattern position
    assert MazeValidator(maze)._validate_42_pattern() is False
