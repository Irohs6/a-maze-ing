# tests/test_maze_validator.py — Tests unitaires de MazeValidator.
# Vérifie les règles de validation appliquées à la structure du labyrinthe :
#   - _validate_cell_values     : bornes [0, 15]
#   - _validate_maze_boundaries : murs extérieurs intacts
#   - _validate_adjacent_cells  : symétrie N↔S, E↔W
#   - _has_forbidden_open_areas : zones 3×3 interdites
#   - _validate_maze_connectivity : tous les non-isolés accessibles depuis (0,0)
#   - _validate_42_pattern      : motif "42" bien placé (ou absent
# si trop petit)
#   - validate()                : orchestration globale

import pytest
from model.maze import Maze
from model.maze_validator import MazeValidator
from mazegen.maze_generator import MazeGenerator


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def valid_11x11() -> Maze:
    """Labyrinthe parfait 11×11 généré (seed fixe)."""
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=True)
    gen.generate()
    return gen.get_maze()


@pytest.fixture
def valid_5x5() -> Maze:
    """Labyrinthe parfait 5×5 généré (trop petit pour le motif 42)."""
    gen = MazeGenerator(width=5, height=5, seed=1, perfect=True)
    gen.generate()
    return gen.get_maze()


# ── validate() — orchestration globale ───────────────────────────────


def test_validate_perfect_maze_11x11(valid_11x11: Maze) -> None:
    assert MazeValidator(valid_11x11).validate() is True


def test_validate_perfect_maze_5x5(valid_5x5: Maze) -> None:
    assert MazeValidator(valid_5x5).validate() is True


def test_validate_kruskal_maze_is_valid() -> None:
    gen = MazeGenerator(width=11, height=11, seed=3, perfect=False)
    gen.generate()
    assert MazeValidator(gen.get_maze()).validate() is True


def test_validate_full_wall_maze_passes_as_all_isolated() -> None:
    """Toutes les cellules valent 15 → toutes sont 'isolées' → connexité OK."""
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
    """Valeur 0 (aucun mur) est dans [0, 15] → valide."""
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
    maze.grid[0][1] &= ~1  # retire le mur N de la cellule (1, 0) directement
    assert MazeValidator(maze)._validate_maze_boundaries() is False


def test_boundary_south_wall_removed_fails() -> None:
    maze = Maze(4, 4)
    maze.grid[3][2] &= ~4  # retire le mur S de (2, 3)
    assert MazeValidator(maze)._validate_maze_boundaries() is False


def test_boundary_west_wall_removed_fails() -> None:
    maze = Maze(4, 4)
    maze.grid[1][0] &= ~8  # retire le mur W de (0, 1)
    assert MazeValidator(maze)._validate_maze_boundaries() is False


def test_boundary_east_wall_removed_fails() -> None:
    maze = Maze(4, 4)
    maze.grid[1][3] &= ~2  # retire le mur E de (3, 1)
    assert MazeValidator(maze)._validate_maze_boundaries() is False


def test_boundaries_valid_in_generated_maze(valid_11x11: Maze) -> None:
    assert MazeValidator(valid_11x11)._validate_maze_boundaries() is True


# ── _validate_adjacent_cells ──────────────────────────────────────────


def test_adjacent_cells_consistent_after_remove_wall() -> None:
    maze = Maze(5, 5)
    maze.remove_wall(2, 2, 'E')
    assert MazeValidator(maze)._validate_adjacent_cells() is True


def test_adjacent_cells_asymmetric_east_west_fails() -> None:
    """Retirer le mur Est de (1,1) sans retirer le mur Ouest de (2,1)."""
    maze = Maze(5, 5)
    maze.grid[1][1] &= ~2  # manipulation directe, pas de symétrie
    assert MazeValidator(maze)._validate_adjacent_cells() is False


def test_adjacent_cells_asymmetric_north_south_fails() -> None:
    """Retirer le mur Sud de (1,1) sans retirer le mur Nord de (1,2)."""
    maze = Maze(5, 5)
    maze.grid[1][1] &= ~4  # retire seulement S de (1,1)
    assert MazeValidator(maze)._validate_adjacent_cells() is False


def test_adjacent_cells_valid_in_generated_maze(valid_11x11: Maze) -> None:
    assert MazeValidator(valid_11x11)._validate_adjacent_cells() is True


# ── _has_forbidden_open_areas ─────────────────────────────────────────


def test_no_forbidden_areas_in_full_wall_maze() -> None:
    maze = Maze(5, 5)
    assert MazeValidator(maze)._has_forbidden_open_areas() is False


def test_3x3_open_area_detected() -> None:
    """Bloc 3×3 entièrement ouvert en (1,1) → zone interdite."""
    maze = Maze(5, 5)
    # Ouvrir tous les murs horizontaux Est du bloc (colonnes 1→2 et 2→3)
    for y in range(1, 4):
        for x in range(1, 3):
            maze.remove_wall(x, y, 'E')
    # Ouvrir tous les murs verticaux Sud du bloc (lignes 1→2 et 2→3)
    for y in range(1, 3):
        for x in range(1, 4):
            maze.remove_wall(x, y, 'S')
    assert MazeValidator(maze)._has_forbidden_open_areas() is True


def test_2x2_open_area_not_forbidden() -> None:
    """Un bloc 2×2 ouvert est autorisé (seul le 3×3 est interdit)."""
    maze = Maze(5, 5)
    maze.remove_wall(1, 1, 'E')
    maze.remove_wall(1, 1, 'S')
    maze.remove_wall(2, 1, 'S')
    maze.remove_wall(1, 2, 'E')
    assert MazeValidator(maze)._has_forbidden_open_areas() is False


def test_no_forbidden_areas_in_generated_maze(valid_11x11: Maze) -> None:
    assert MazeValidator(valid_11x11)._has_forbidden_open_areas() is False


# ── _validate_maze_connectivity ───────────────────────────────────────


def test_connectivity_passes_for_generated_maze(valid_11x11: Maze) -> None:
    assert MazeValidator(valid_11x11)._validate_maze_connectivity() is True


def test_connectivity_passes_for_full_wall_maze() -> None:
    """Toutes les cellules sont isolées (15) → connexité automatique."""
    maze = Maze(4, 4)
    assert MazeValidator(maze)._validate_maze_connectivity() is True


def test_connectivity_fails_when_cells_unreachable() -> None:
    """Ouvrir (3,3)↔(4,3) crée deux cellules non-15
    inaccessibles depuis (0,0)."""
    maze = Maze(5, 5)
    maze.remove_wall(3, 3, 'E')
    assert MazeValidator(maze)._validate_maze_connectivity() is False


def test_connectivity_fails_for_partial_generation() -> None:
    """Un passage isolé loin du coin haut-gauche brise la connexité."""
    maze = Maze(7, 7)
    maze.remove_wall(5, 5, 'S')
    assert MazeValidator(maze)._validate_maze_connectivity() is False


# ── _validate_42_pattern ──────────────────────────────────────────────


def test_42_pattern_valid_in_large_maze(valid_11x11: Maze) -> None:
    assert MazeValidator(valid_11x11)._validate_42_pattern() is True


def test_42_pattern_skipped_for_too_narrow_maze() -> None:
    """Labyrinthe width < 7 (largeur du motif) → validation ignorée."""
    maze = Maze(5, 5)
    assert MazeValidator(maze)._validate_42_pattern() is True


def test_42_pattern_skipped_when_no_isolated_cell() -> None:
    """Sans aucune cellule à valeur 15, la vérification du motif est ignorée."""
    maze = Maze(11, 11)
    for y in range(maze.height):
        for x in range(maze.width):
            maze.grid[y][x] = 0
    assert MazeValidator(maze)._validate_42_pattern() is True


def test_42_pattern_fails_when_pattern_missing_in_large_maze() -> None:
    """Un 11×11 avec des cellules 15 mais sans motif '42'
    — validation échoue."""
    maze = Maze(11, 11)
    # Effacer toutes les cellules du motif 42 placé par __init__
    # mais laisser une cellule isolée ailleurs
    for y in range(maze.height):
        for x in range(maze.width):
            maze.grid[y][x] = 0
    maze.grid[0][0] = 15  # cellule isolée, mais pas en position motif 42
    assert MazeValidator(maze)._validate_42_pattern() is False
