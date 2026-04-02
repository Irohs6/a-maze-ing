# mazegen/maze_generator.py — Module réutilisable de génération de labyrinthe.
# Contient la classe MazeGenerator, conçue pour être importée dans n'importe quel projet.
# La classe encapsule la logique complète de génération et expose une API claire :
#   - __init__(width, height, seed, perfect, algorithm) : initialise le générateur
#   - generate() : génère le labyrinthe et le stocke en interne
#   - get_maze() : retourne la grille de cellules sous forme de tableau 2D
#   - get_solution() : retourne le chemin le plus court sous forme de liste de directions
#   - reset(seed) : réinitialise et régénère avec une nouvelle graine
# Implémente au moins un algorithme de génération (ex. : recursive backtracker ou Prim)
# qui garantit les contraintes du sujet (connectivité, largeur max de couloir, motif 42).
# Contient une documentation complète avec exemples d'utilisation (conforme PEP 257).

import random
from model.maze import Maze
from model.maze_validator import MazeValidator


class MazeGenerator:
    """Generates a maze based on specified parameters.

    This class encapsulates the entire maze generation logic, allowing for
    easy reuse in any project. It supports multiple algorithms and ensures
    that generated mazes meet the required constraints.

    Example usage:
        generator = MazeGenerator(width=10, height=10, seed=42, perfect=True, 
        algorithm='backtracker
        generator.generate()
        maze_grid = generator.get_maze()
        solution_path = generator.get_solution()
    """

    def __init__(self, width: int, height: int, seed: int = None,
                 perfect: bool = True, algorithm: str = 'backtracker') -> None:
        """Initialize the maze generator with given parameters."""
        self.width = width
        self.height = height
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self.perfect = perfect
        self.algorithm = algorithm
        self.maze = Maze(self.width, self.height)
        self.solution_path = None
        self.track: list[str] = []

    def generate(self) -> None:
        """Generate the maze using the specified algorithm."""
        if self.algorithm == 'backtracker':
            self._generate_backtracker()
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")

        # Validate only AFTER generation
        validator = MazeValidator(self.maze)
        if not validator.validate():
            raise ValueError("Generated maze is invalid.")

    def get_maze(self) -> list[list[int]]:
        """Return the generated maze grid as a 2D list of cell values."""
        return self.maze

    def get_solution(self) -> list[str]:
        """Return the solution path as a list of directions (e.g., ['N', 'E', 'S'])."""
        if self.solution_path is None:
            raise ValueError("Solution not generated yet. Call generate() first.")
        return self.solution_path

    def reset(self, seed: int = None) -> None:
        if seed is not None:
            self.seed = seed
            random.seed(seed)

        self.maze = Maze(self.width, self.height)
        self.solution_path = None
        self.track = []

    def _generate_backtracker(self) -> list[str]:
        """Internal method to generate the maze using the recursive backtracker
         algorithm."""
        # Implementation of the backtracker algorithm goes here.
        # This method should modify self.maze to create the maze and
        # set self.solution_path to the correct path from start to finish.

        directions = {
            'N': (0, -1),
            'E': (1, 0),
            'S': (0, 1),
            'W': (-1, 0),
        }

        start = (0, 0)
        visited = set()
        stack = []
        track = []

        visited.add(start)
        stack.append(start)

        while stack:
            current_cell = stack[-1]
            x, y = current_cell

            neighbors = []  # ← tu dois la créer ici

            for direction, (offset_x, offset_y) in directions.items():
                nx = x + offset_x
                ny = y + offset_y

                # Check boundaries
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        neighbors.append((nx, ny, direction))

            if not neighbors:
                stack.pop()
                track.append("BACK")
                continue
            else:
                nx, ny, direction = random.choice(neighbors)
                self.maze.remove_wall(x, y, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
                track.append(direction)

        self.track = track
        return track
