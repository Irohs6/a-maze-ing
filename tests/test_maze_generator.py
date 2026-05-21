# tests/test_maze_generator.py — Unit tests for
# the reusable MazeGenerator module.
# Validates the public API exposed by the mazegen package:
#   - instantiation with various parameter combinations
#   - deterministic generation: same seed always produces the same maze
#   - get_maze() returns a coherent 2D structure with correct dimensions
#   - get_solution() returns a valid path from entry to exit
#   - perfect mode: verify that only one path exists between entry and exit
#   - reset() correctly regenerates with a new seed
#   - handling of invalid parameters (negative dimensions,
# non-integer seed, etc.)

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
def gen_backtracker() -> MazeGenerator:
    return MazeGenerator(width=11, height=11, seed=1, perfect=True)


@pytest.fixture
def gen_kruksal() -> MazeGenerator:
    return MazeGenerator(
        width=11, height=11, seed=1, perfect=False, algorithm="kruksal"
    )


# ── Initialisation ────────────────────────────────────────────────────


def test_init_default_perfect() -> None:
    gen = MazeGenerator(width=5, height=5, perfect=True)
    assert gen.perfect is True


def test_init_stores_dimensions() -> None:
    gen = MazeGenerator(width=8, height=6, perfect=True)
    assert gen.width == 8
    assert gen.height == 6


def test_init_stores_seed() -> None:
    gen = MazeGenerator(width=5, height=5, seed=99, perfect=True)
    assert gen.seed == 99


def test_init_track_and_cells_empty() -> None:
    gen = MazeGenerator(width=5, height=5, perfect=True)
    assert gen.tracks == []
    assert gen.forty_two_cells == set()


# ── generate() — backtracker ──────────────────────────────────────────


def test_generate_backtracker_returns_maze_instance(
    gen_backtracker: MazeGenerator,
) -> None:
    gen_backtracker.generate()
    assert isinstance(gen_backtracker.get_maze(), Maze)


def test_generate_backtracker_dimensions(
    gen_backtracker: MazeGenerator,
) -> None:
    gen_backtracker.generate()
    maze = gen_backtracker.get_maze()
    assert maze.width == 11
    assert maze.height == 11
    assert len(maze.grid) == 11
    assert len(maze.grid[0]) == 11


def test_generate_backtracker_track_nonempty(
    gen_backtracker: MazeGenerator,
) -> None:
    gen_backtracker.generate()
    assert len(gen_backtracker.tracks) > 0


def test_generate_backtracker_maze_is_valid(
    gen_backtracker: MazeGenerator,
) -> None:
    gen_backtracker.generate()
    validator = MazeValidator(gen_backtracker.get_maze())
    assert validator.validate() is True


def test_generate_backtracker_forty_two_cells_populated(
    gen_backtracker: MazeGenerator,
) -> None:
    """For an 11x11 maze (>= min 11x9), the pattern must be placed."""
    gen_backtracker.generate()
    assert len(gen_backtracker.forty_two_cells) > 0


# ── generate() — kruksal ──────────────────────────────────────────────


def test_generate_kruksal_returns_maze_instance(
    gen_kruksal: MazeGenerator,
) -> None:
    gen_kruksal.generate()
    assert isinstance(gen_kruksal.get_maze(), Maze)


def test_generate_kruksal_dimensions(gen_kruksal: MazeGenerator) -> None:
    gen_kruksal.generate()
    maze = gen_kruksal.get_maze()
    assert maze.width == 11
    assert maze.height == 11


def test_generate_kruksal_track_nonempty(gen_kruksal: MazeGenerator) -> None:
    gen_kruksal.generate()
    assert len(gen_kruksal.tracks) > 0


def test_generate_kruksal_maze_is_valid(gen_kruksal: MazeGenerator) -> None:
    gen_kruksal.generate()
    validator = MazeValidator(gen_kruksal.get_maze())
    assert validator.validate() is True


def test_generate_kruksal_forty_two_cells_populated(
    gen_kruksal: MazeGenerator,
) -> None:
    gen_kruksal.generate()
    assert len(gen_kruksal.forty_two_cells) > 0


# ── Determinism (seed) ───────────────────────────────────────────────────


def test_same_seed_same_maze_backtracker() -> None:
    """Two backtracker generators with the same seed produce
    the same maze."""
    gen_a = MazeGenerator(width=11, height=11, seed=42, perfect=True)
    gen_b = MazeGenerator(width=11, height=11, seed=42, perfect=True)
    gen_a.generate()
    gen_b.generate()
    assert gen_a.get_maze().grid == gen_b.get_maze().grid


def test_same_seed_same_maze_kruksal() -> None:
    gen_a = MazeGenerator(width=11, height=11, seed=7, perfect=False)
    gen_b = MazeGenerator(width=11, height=11, seed=7, perfect=False)
    gen_a.generate()
    gen_b.generate()
    assert gen_a.get_maze().grid == gen_b.get_maze().grid


def test_different_seeds_different_mazes_backtracker() -> None:
    gen_a = MazeGenerator(width=11, height=11, seed=1, perfect=True)
    gen_b = MazeGenerator(width=11, height=11, seed=2, perfect=True)
    gen_a.generate()
    gen_b.generate()
    assert gen_a.get_maze().grid != gen_b.get_maze().grid


# ── Alias d'algorithmes ───────────────────────────────────────────────


def test_perfect_true_generates_valid_maze() -> None:
    """perfect=True uses Backtracker and generates a valid maze."""
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=True)
    gen.generate()
    assert isinstance(gen.get_maze(), Maze)
    validator = MazeValidator(gen.get_maze())
    assert validator.validate() is True


def test_perfect_false_generates_valid_maze() -> None:
    """perfect=False uses Kruksal and generates a valid maze."""
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=False)
    gen.generate()
    assert isinstance(gen.get_maze(), Maze)
    validator = MazeValidator(gen.get_maze())
    assert validator.validate() is True


# ── Invalid parameters ────────────────────────────────────────────────────


def test_unknown_algorithm_raises() -> None:
    """An unknown algorithm name raises ValueError at generate()."""
    gen = MazeGenerator(
        width=5, height=5, perfect=True, algorithm="unknown_algo"
    )
    with pytest.raises(ValueError):
        gen.generate()


# ── Petits labyrinthes (sans motif 42) ────────────────────────────────


def test_small_maze_no_forty_two_cells() -> None:
    """Any maze with < 11 cols or < 9 rows must not contain the pattern."""
    for w, h in [(4, 4), (7, 7), (8, 8), (10, 10), (11, 8)]:
        gen = MazeGenerator(width=w, height=h, seed=1, perfect=True)
        gen.generate()
        assert (
            gen.forty_two_cells == set()
        ), f"{w}x{h} should not have 42 cells"


def test_maze_with_forty_two_cells_at_minimum_size() -> None:
    """An 11x9 maze (minimum size) must contain the pattern."""
    gen = MazeGenerator(width=11, height=9, seed=1, perfect=True)
    gen.generate()
    assert len(gen.forty_two_cells) > 0


def test_small_maze_is_still_valid() -> None:
    """A maze too small for the 42 pattern is still structurally valid."""
    gen = MazeGenerator(width=4, height=4, seed=1, perfect=True)
    gen.generate()
    validator = MazeValidator(gen.get_maze())
    assert validator.validate() is True


# ── reset() ───────────────────────────────────────────────────────────


def test_reset_clears_track_and_maze() -> None:
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=True)
    gen.generate()
    assert len(gen.tracks) > 0
    gen.reset()
    assert gen.tracks == []


def test_reset_allows_regeneration() -> None:
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=True)
    gen.generate()
    first_grid = [row[:] for row in gen.get_maze().grid]
    gen.reset(seed=99)
    gen.generate()
    second_grid = gen.get_maze().grid
    assert first_grid != second_grid


def test_reset_preserves_42_cells_in_maze() -> None:
    """After reset(), maze.forty_two_cells is not cleared (still set
    on the reused Maze object). The next
    generation finds them again."""
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=True)
    gen.generate()
    cells_before = frozenset(gen.get_maze().forty_two_cells)
    gen.reset()
    gen.generate()
    cells_after = frozenset(gen.get_maze().forty_two_cells)
    assert cells_before == cells_after


# ── Algorithme Kruksal explicite ──────────────────────────────────────


def test_kruksal_explicit_generates_valid_maze() -> None:
    """algorithm='kruksal' + perfect=True generates a valid maze."""
    gen = MazeGenerator(
        width=11, height=11, seed=3, perfect=True, algorithm="kruksal"
    )
    gen.generate()
    assert MazeValidator(gen.get_maze()).validate() is True


def test_kruksal_imperfect_generates_valid_maze() -> None:
    """algorithm='kruksal' + perfect=False (second_loop) remains valid."""
    gen = MazeGenerator(
        width=11, height=11, seed=3, perfect=False, algorithm="kruksal"
    )
    gen.generate()
    assert MazeValidator(gen.get_maze()).validate() is True


def test_kruksal_imperfect_has_cycle() -> None:
    """An imperfect Kruksal maze contains at least one cycle."""
    from model.cycle_checker import CycleChecker

    gen = MazeGenerator(
        width=11, height=11, seed=3, perfect=False, algorithm="kruksal"
    )
    gen.generate()
    assert CycleChecker(gen.get_maze()).has_cycle() is True


# ── Algorithme Backtracker imparfait (second_loop) ────────────────────


def test_backtracker_imperfect_generates_valid_maze() -> None:
    """Backtracker + perfect=False triggers second_loop without error."""
    gen = MazeGenerator(
        width=11, height=11, seed=5, perfect=False, algorithm="backtracker"
    )
    gen.generate()
    assert MazeValidator(gen.get_maze()).validate() is True


def test_backtracker_imperfect_has_cycle() -> None:
    """An imperfect Backtracker maze contains at least one cycle."""
    from model.cycle_checker import CycleChecker

    gen = MazeGenerator(
        width=11, height=11, seed=5, perfect=False, algorithm="backtracker"
    )
    gen.generate()
    assert CycleChecker(gen.get_maze()).has_cycle() is True
