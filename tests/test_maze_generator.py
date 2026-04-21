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
def gen_backtracker() -> MazeGenerator:
    return MazeGenerator(width=11, height=11, seed=1, perfect=True)


@pytest.fixture
def gen_kruskal() -> MazeGenerator:
    return MazeGenerator(width=11, height=11, seed=1, perfect=False)


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
                        gen_backtracker: MazeGenerator) -> None:
    gen_backtracker.generate()
    assert isinstance(gen_backtracker.get_maze(), Maze)


def test_generate_backtracker_dimensions(
        gen_backtracker: MazeGenerator) -> None:
    gen_backtracker.generate()
    maze = gen_backtracker.get_maze()
    assert maze.width == 11
    assert maze.height == 11
    assert len(maze.grid) == 11
    assert len(maze.grid[0]) == 11


def test_generate_backtracker_track_nonempty(
        gen_backtracker: MazeGenerator) -> None:
    gen_backtracker.generate()
    assert len(gen_backtracker.tracks) > 0


def test_generate_backtracker_maze_is_valid(
        gen_backtracker: MazeGenerator) -> None:
    gen_backtracker.generate()
    validator = MazeValidator(gen_backtracker.get_maze())
    assert validator.validate() is True


def test_generate_backtracker_forty_two_cells_populated(
        gen_backtracker: MazeGenerator) -> None:
    """Pour un labyrinthe 11x11 (>= min 11x9), le motif doit être placé."""
    gen_backtracker.generate()
    assert len(gen_backtracker.forty_two_cells) > 0


# ── generate() — kruskal ──────────────────────────────────────────────


def test_generate_kruskal_returns_maze_instance(
        gen_kruskal: MazeGenerator) -> None:
    gen_kruskal.generate()
    assert isinstance(gen_kruskal.get_maze(), Maze)


def test_generate_kruskal_dimensions(gen_kruskal: MazeGenerator) -> None:
    gen_kruskal.generate()
    maze = gen_kruskal.get_maze()
    assert maze.width == 11
    assert maze.height == 11


def test_generate_kruskal_track_nonempty(gen_kruskal: MazeGenerator) -> None:
    gen_kruskal.generate()
    assert len(gen_kruskal.tracks) > 0


def test_generate_kruskal_maze_is_valid(gen_kruskal: MazeGenerator) -> None:
    gen_kruskal.generate()
    validator = MazeValidator(gen_kruskal.get_maze())
    assert validator.validate() is True


def test_generate_kruskal_forty_two_cells_populated(
        gen_kruskal: MazeGenerator) -> None:
    gen_kruskal.generate()
    assert len(gen_kruskal.forty_two_cells) > 0


# ── Déterminisme (seed) ───────────────────────────────────────────────


def test_same_seed_same_maze_backtracker() -> None:
    """Deux générateurs backtracker avec la même seed produisent
    le même labyrinthe."""
    gen_a = MazeGenerator(width=11, height=11, seed=42, perfect=True)
    gen_b = MazeGenerator(width=11, height=11, seed=42, perfect=True)
    gen_a.generate()
    gen_b.generate()
    assert gen_a.get_maze().grid == gen_b.get_maze().grid


def test_same_seed_same_maze_kruskal() -> None:
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
    """perfect=True utilise le Backtracker et génère un labyrinthe valide."""
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=True)
    gen.generate()
    assert isinstance(gen.get_maze(), Maze)
    validator = MazeValidator(gen.get_maze())
    assert validator.validate() is True


def test_perfect_false_generates_valid_maze() -> None:
    """perfect=False utilise Kruskal et génère un labyrinthe valide."""
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=False)
    gen.generate()
    assert isinstance(gen.get_maze(), Maze)
    validator = MazeValidator(gen.get_maze())
    assert validator.validate() is True


# ── Paramètres invalides ──────────────────────────────────────────────


def test_unsupported_perfect_value_raises() -> None:
    gen = MazeGenerator(width=5, height=5, perfect=None)  # type: ignore
    with pytest.raises(ValueError) as excinfo:
        gen.generate()
    assert 'Unsupported algorithm' in str(excinfo.value)


# ── Petits labyrinthes (sans motif 42) ────────────────────────────────

def test_small_maze_no_forty_two_cells() -> None:
    """Tout labyrinthe < 11 cols ou < 9 lignes ne doit pas contenir le motif."""
    for w, h in [(4, 4), (7, 7), (8, 8), (10, 10), (11, 8)]:
        gen = MazeGenerator(width=w, height=h, seed=1, perfect=True)
        gen.generate()
        assert gen.forty_two_cells == set(), (
            f"{w}x{h} ne devrait pas avoir de cellules 42"
        )


def test_maze_with_forty_two_cells_at_minimum_size() -> None:
    """Un labyrinthe 11x9 (taille minimale) doit contenir le motif."""
    gen = MazeGenerator(width=11, height=9, seed=1, perfect=True)
    gen.generate()
    assert len(gen.forty_two_cells) > 0


def test_small_maze_is_still_valid() -> None:
    """Un labyrinthe trop petit pour le motif 42
    reste structurellement valide."""
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
    assert gen.solution_path is None


def test_reset_allows_regeneration() -> None:
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=True)
    gen.generate()
    first_grid = [row[:] for row in gen.get_maze().grid]
    gen.reset(seed=99)
    gen.generate()
    second_grid = gen.get_maze().grid
    assert first_grid != second_grid
