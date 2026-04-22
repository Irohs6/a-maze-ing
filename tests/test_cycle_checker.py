# tests/test_cycle_checker.py — Tests unitaires de Cycle_Checker.
# Vérifie la détection de cycles dans le graphe du labyrinthe.
# Méthode : edges >= nodes (arbre couvrant = nodes-1 edges, cycle = nodes+)
# Les cellules du motif "42" (value 15 = isolées) sont exclues du compte.

import pytest
from model.maze import Maze
from model.cycle_cheker import Cycle_Checker
from mazegen.maze_generator import MazeGenerator


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def perfect_11x11() -> Maze:
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=True)
    gen.generate()
    return gen.get_maze()


@pytest.fixture
def imperfect_kruskal_11x11() -> Maze:
    gen = MazeGenerator(width=11, height=11, seed=1, perfect=False,
                        algorithm='kruksal')
    gen.generate()
    return gen.get_maze()


@pytest.fixture
def imperfect_backtracker_11x11() -> Maze:
    gen = MazeGenerator(width=11, height=11, seed=5, perfect=False,
                        algorithm='backtracker')
    gen.generate()
    return gen.get_maze()


# ── Labyrinthe plein (aucun passage) ──────────────────────────────────


def test_full_wall_maze_has_no_cycle() -> None:
    """Aucun passage → edges=0, nodes>0 → pas de cycle."""
    maze = Maze(5, 5)
    assert Cycle_Checker(maze).has_cycle() is False


def test_single_cell_has_no_cycle() -> None:
    maze = Maze(1, 1)
    assert Cycle_Checker(maze).has_cycle() is False


# ── Labyrinthe parfait (arbre couvrant) ───────────────────────────────


def test_perfect_maze_has_no_cycle(perfect_11x11: Maze) -> None:
    """Labyrinthe parfait = arbre → edges = nodes-1 → pas de cycle."""
    assert Cycle_Checker(perfect_11x11).has_cycle() is False


def test_perfect_small_maze_has_no_cycle() -> None:
    gen = MazeGenerator(width=5, height=5, seed=42, perfect=True)
    gen.generate()
    assert Cycle_Checker(gen.get_maze()).has_cycle() is False


# ── Labyrinthe imparfait (cycles présents) ────────────────────────────


def test_imperfect_kruskal_has_cycle(imperfect_kruskal_11x11: Maze) -> None:
    """Kruskal imparfait : second_loop crée des cycles."""
    assert Cycle_Checker(imperfect_kruskal_11x11).has_cycle() is True


def test_imperfect_backtracker_has_cycle(
    imperfect_backtracker_11x11: Maze,
) -> None:
    """Backtracker imparfait : second_loop crée des cycles."""
    assert Cycle_Checker(imperfect_backtracker_11x11).has_cycle() is True


# ── Cas construits manuellement ───────────────────────────────────────


def test_two_cells_one_connection_no_cycle() -> None:
    """2 cellules, 1 connexion : edges=1, nodes=2 → 1 < 2 → pas de cycle."""
    maze = Maze(2, 1)
    maze.remove_wall(0, 0, 'E')
    assert Cycle_Checker(maze).has_cycle() is False


def test_2x2_loop_creates_cycle() -> None:
    """Boucle 2×2 : 4 connexions E/S, 4 nœuds → edges=4 >= nodes=4 → cycle."""
    maze = Maze(2, 2)
    maze.remove_wall(0, 0, 'E')
    maze.remove_wall(0, 0, 'S')
    maze.remove_wall(1, 0, 'S')
    maze.remove_wall(0, 1, 'E')
    assert Cycle_Checker(maze).has_cycle() is True


def test_linear_chain_no_cycle() -> None:
    """Chaîne linéaire 4×1 : 3 connexions, 4 nœuds → pas de cycle."""
    maze = Maze(4, 1)
    maze.remove_wall(0, 0, 'E')
    maze.remove_wall(1, 0, 'E')
    maze.remove_wall(2, 0, 'E')
    assert Cycle_Checker(maze).has_cycle() is False


def test_tree_3x3_no_cycle() -> None:
    """Arbre couvrant 3×3 : 8 connexions, 9 nœuds → pas de cycle."""
    maze = Maze(3, 3)
    # Construction d'un arbre : chemin en serpentin
    maze.remove_wall(0, 0, 'E')
    maze.remove_wall(1, 0, 'E')
    maze.remove_wall(2, 0, 'S')
    maze.remove_wall(2, 1, 'W')
    maze.remove_wall(1, 1, 'W')
    maze.remove_wall(0, 1, 'S')
    maze.remove_wall(0, 2, 'E')
    maze.remove_wall(1, 2, 'E')
    assert Cycle_Checker(maze).has_cycle() is False


# ── Exclusion des cellules 42 ─────────────────────────────────────────


def test_42_cells_excluded_from_node_count() -> None:
    """Les cellules du motif 42 (value=15) sont exclues du compte de nœuds.
    Un labyrinthe parfait avec motif 42 doit toujours être sans cycle."""
    gen = MazeGenerator(width=11, height=11, seed=7, perfect=True)
    gen.generate()
    maze = gen.get_maze()
    assert len(maze.forty_two_cells) > 0
    assert Cycle_Checker(maze).has_cycle() is False
