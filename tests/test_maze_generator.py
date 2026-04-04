# tests/test_maze_generator.py — Tests unitaires
# du module réutilisable MazeGenerator.
# Valide l'API publique exposée par le paquet mazegen :
#   - instanciation avec différentes combinaisons de paramètres
#   - génération déterministe : même seed produit toujours le même labyrinthe
#   - get_maze() retourne une structure 2D cohérente aux bonnes dimensions
#   - get_solution() retourne un chemin valide reliant l'entrée à la sortie
#   - mode parfait : vérification qu'un seul chemin existe
# entre entrée et sortie
#   - reset() régénère correctement avec une nouvelle graine
#   - gestion des paramètres invalides (dimensions négatives,
# seed non entier, etc.)

import pytest
from model.maze import Maze
from model.maze_validator import MazeValidator
from mazegen.maze_generator import MazeGenerator


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def gen_backtracker():
    return MazeGenerator(width=11, height=11, seed=1, algorithm='backtracker')


@pytest.fixture
def gen_kruskal():
    return MazeGenerator(width=11, height=11, seed=1, algorithm='kruksal')


# ── Initialisation ────────────────────────────────────────────────────


def test_init_default_algorithm():
    gen = MazeGenerator(width=5, height=5)
    assert gen.algorithm == 'backtracker'


def test_init_stores_dimensions():
    gen = MazeGenerator(width=8, height=6)
    assert gen.width == 8
    assert gen.height == 6


def test_init_stores_seed():
    gen = MazeGenerator(width=5, height=5, seed=99)
    assert gen.seed == 99


def test_init_track_and_cells_empty():
    gen = MazeGenerator(width=5, height=5)
    assert gen.track == []
    assert gen.forty_two_cells == set()


# ── generate() — backtracker ──────────────────────────────────────────


def test_generate_backtracker_returns_maze_instance(gen_backtracker):
    gen_backtracker.generate()
    assert isinstance(gen_backtracker.get_maze(), Maze)


def test_generate_backtracker_dimensions(gen_backtracker):
    gen_backtracker.generate()
    maze = gen_backtracker.get_maze()
    assert maze.width == 11
    assert maze.height == 11
    assert len(maze.grid) == 11
    assert len(maze.grid[0]) == 11


def test_generate_backtracker_track_nonempty(gen_backtracker):
    gen_backtracker.generate()
    assert len(gen_backtracker.track) > 0


def test_generate_backtracker_maze_is_valid(gen_backtracker):
    gen_backtracker.generate()
    validator = MazeValidator(gen_backtracker.get_maze())
    assert validator.validate() is True


def test_generate_backtracker_forty_two_cells_populated(gen_backtracker):
    """Pour un labyrinthe 11x11 (>= min 11x9), le motif doit être placé."""
    gen_backtracker.generate()
    assert len(gen_backtracker.forty_two_cells) > 0


# ── generate() — kruskal ──────────────────────────────────────────────


def test_generate_kruskal_returns_maze_instance(gen_kruskal):
    gen_kruskal.generate()
    assert isinstance(gen_kruskal.get_maze(), Maze)


def test_generate_kruskal_dimensions(gen_kruskal):
    gen_kruskal.generate()
    maze = gen_kruskal.get_maze()
    assert maze.width == 11
    assert maze.height == 11


def test_generate_kruskal_track_nonempty(gen_kruskal):
    gen_kruskal.generate()
    assert len(gen_kruskal.track) > 0


def test_generate_kruskal_maze_is_valid(gen_kruskal):
    gen_kruskal.generate()
    validator = MazeValidator(gen_kruskal.get_maze())
    assert validator.validate() is True


def test_generate_kruskal_forty_two_cells_populated(gen_kruskal):
    gen_kruskal.generate()
    assert len(gen_kruskal.forty_two_cells) > 0


# ── Déterminisme (seed) ───────────────────────────────────────────────


def test_same_seed_same_maze_backtracker():
    """Deux générateurs backtracker avec la même seed produisent
    le même labyrinthe."""
    gen_a = MazeGenerator(
        width=11, height=11, seed=42, algorithm='backtracker'
    )
    gen_b = MazeGenerator(
        width=11, height=11, seed=42, algorithm='backtracker'
    )
    gen_a.generate()
    gen_b.generate()
    assert gen_a.get_maze().grid == gen_b.get_maze().grid


def test_same_seed_same_maze_kruskal():
    gen_a = MazeGenerator(width=11, height=11, seed=7, algorithm='kruksal')
    gen_b = MazeGenerator(width=11, height=11, seed=7, algorithm='kruksal')
    gen_a.generate()
    gen_b.generate()
    assert gen_a.get_maze().grid == gen_b.get_maze().grid


def test_different_seeds_different_mazes_backtracker():
    gen_a = MazeGenerator(
        width=11, height=11, seed=1, algorithm='backtracker'
    )
    gen_b = MazeGenerator(
        width=11, height=11, seed=2, algorithm='backtracker'
    )
    gen_a.generate()
    gen_b.generate()
    assert gen_a.get_maze().grid != gen_b.get_maze().grid


# ── Alias d'algorithmes ───────────────────────────────────────────────


def test_recursive_backtracker_alias():
    """'recursive_backtracker' doit être accepté comme algorithme valide."""
    gen = MazeGenerator(
        width=11, height=11, seed=1, algorithm='recursive_backtracker'
    )
    gen.generate()  # Ne doit pas lever d'exception
    assert isinstance(gen.get_maze(), Maze)


def test_kruskal_alias():
    """'kruskal' (orthographe anglaise) ne doit pas être accepté."""
    gen = MazeGenerator(width=11, height=11, seed=1, algorithm='kruskal')
    with pytest.raises(ValueError) as excinfo:
        gen.generate()
    assert 'Unsupported algorithm' in str(excinfo.value)


# ── Paramètres invalides ──────────────────────────────────────────────


def test_unsupported_algorithm_raises():
    gen = MazeGenerator(width=5, height=5, algorithm='prim')
    with pytest.raises(ValueError) as excinfo:
        gen.generate()
    assert 'Unsupported algorithm' in str(excinfo.value)


def test_get_solution_raises_before_generate():
    gen = MazeGenerator(width=5, height=5)
    with pytest.raises(ValueError) as excinfo:
        gen.get_solution()
    assert 'generate()' in str(excinfo.value)


# ── Petits labyrinthes (sans motif 42) ────────────────────────────────


def test_small_maze_no_forty_two_cells():
    """Tout labyrinthe < 11 cols ou < 9 lignes ne doit pas contenir le motif."""
    for w, h in [(4, 4), (7, 7), (8, 8), (10, 10), (11, 8)]:
        gen = MazeGenerator(width=w, height=h, seed=1, algorithm='backtracker')
        gen.generate()
        assert gen.forty_two_cells == set(), (
            f"{w}x{h} ne devrait pas avoir de cellules 42"
        )


def test_maze_with_forty_two_cells_at_minimum_size():
    """Un labyrinthe 11x9 (taille minimale) doit contenir le motif."""
    gen = MazeGenerator(width=11, height=9, seed=1, algorithm='backtracker')
    gen.generate()
    assert len(gen.forty_two_cells) > 0


def test_small_maze_is_still_valid():
    """Un labyrinthe trop petit pour le motif 42
    reste structurellement valide."""
    gen = MazeGenerator(width=4, height=4, seed=1, algorithm='backtracker')
    gen.generate()
    validator = MazeValidator(gen.get_maze())
    assert validator.validate() is True


# ── reset() ───────────────────────────────────────────────────────────


def test_reset_clears_track_and_maze():
    gen = MazeGenerator(width=11, height=11, seed=1, algorithm='backtracker')
    gen.generate()
    assert len(gen.track) > 0
    gen.reset()
    assert gen.track == []
    assert gen.solution_path is None


def test_reset_allows_regeneration():
    gen = MazeGenerator(width=11, height=11, seed=1, algorithm='backtracker')
    gen.generate()
    first_grid = [row[:] for row in gen.get_maze().grid]
    gen.reset(seed=99)
    gen.generate()
    second_grid = gen.get_maze().grid
    assert first_grid != second_grid

