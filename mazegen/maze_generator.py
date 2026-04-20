# mazegen/maze_generator.py — Module réutilisable de génération de labyrinthe.
# Contient la classe MazeGenerator,
# conçue pour être importée dans n'importe quel projet.
# La classe encapsule la logique complète de
# génération et expose une API claire :
#   - __init__(width, height, seed, perfect, algorithm) : initialise
#   - generate() : génère le labyrinthe et le stocke en interne
#   - get_maze() : retourne la grille de cellules
#   - get_solution() : retourne le chemin solution (liste de directions)
#   - reset(seed) : réinitialise et régénère avec une nouvelle graine
# La logique est déléguée aux classes Backtracker et Kruksal
# qui héritent toutes deux de Algorithm (classe abstraite).

import random
from typing import Any
from model.maze import Maze
from model.maze_validator import MazeValidator
from .algorithm import Algorithm
from .backtracker import Backtracker
from .kruksal import Kruksal


class MazeGenerator:
    """Generates a maze based on specified parameters.

    This class encapsulates the entire maze generation logic, allowing for
    easy reuse in any project. It supports multiple algorithms and ensures
    that generated mazes meet the required constraints.

    Example usage:
        generator = MazeGenerator(width=10, height=10, seed=42, perfect=True,
        algorithm='backtracker')
        generator.generate()
        maze_grid = generator.get_maze()
        solution_path = generator.get_solution()
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
        perfect: bool = True,
    ) -> None:
        """Initialize the maze generator with given parameters."""
        self.algorithms = [Backtracker, Kruksal]
        self.width = width
        self.height = height
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self.perfect = perfect
        self.maze = Maze(self.width, self.height)
        self.solution_path: list[Any] | None = None
        self.tracks: list[Any] = []
        self.forty_two_cells: set[tuple[int, int]] = set()

    def generate(self) -> None:
        """Generate the maze using the specified algorithm."""
        if self.seed is not None:
            random.seed(self.seed)
        algo = self._build_algorithm()
        self.tracks = algo.generate()
        self.forty_two_cells = algo.forty_two_cells
        self.maze = algo.maze

        validator = MazeValidator(self.maze)
        if not validator.validate():
            raise ValueError("Generated maze is invalid.")

    def _build_algorithm(self) -> Algorithm:
        """Instantiate the algorithm class based on self.algorithm."""
        for algorithm in self.algorithms:
            if self.perfect == algorithm.perfect:
                return algorithm(self.maze)
        else:
            raise ValueError(
                f"Unsupported algorithm: perfect={self.perfect!r}"
            )

    def get_maze(self) -> Maze:
        """Return the generated maze."""
        return self.maze

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            self.seed = seed
            random.seed(seed)

        for i in range(len(self.maze.grid)):
            for j in range(len(self.maze.grid[i])):
                self.maze.grid[i][j] = 15

        self.solution_path = None
        self.tracks = []
        self.forty_two_cells = set()
