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
        self.perfect = perfect
        self.algorithm = algorithm
        self.maze_grid = None
        self.solution_path = None
