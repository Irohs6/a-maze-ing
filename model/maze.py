# model/maze.py — Structure de données représentant le labyrinthe.
# Contient la classe Maze qui stocke la grille de cellules et leurs murs.
# Chaque cellule est représentée par un entier sur 4 bits (Nord, Est, Sud, Ouest).
# La classe fournit des méthodes pour :
#   - accéder et modifier les murs d'une cellule donnée
#   - vérifier la validité des données (cohérence des murs entre cellules voisines)
#   - détecter les zones ouvertes interdites (aucune zone 3x3 sans murs)
#   - encoder le labyrinthe en hexadécimal pour l'écriture dans le fichier de sortie
#   - placer et vérifier le motif "42" dans la grille
# Utilise des annotations de type et des docstrings conformes à PEP 257.


class Maze:
    """Represents a maze as a grid of cells with walls.

    Each cell is encoded as a 4-bit integer:
        - bit 0 (1): wall to the North
        - bit 1 (2): wall to the East
        - bit 2 (4): wall to the South
        - bit 3 (8): wall to the West

    Provides methods to access and modify cell walls, validate maze structure,
    detect forbidden open areas, encode the maze for output, and handle the "42" pattern.
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialize an empty maze with given dimensions."""
        self.width: int = width
        self.height: int = height

        FULL_WALL = 1 | 2 | 4 | 8  # = 15
        self.grid = [[FULL_WALL for _ in range(width)] for _ in range(height)]

    def set_wall(self, x: int, y: int, direction: str) -> None:
        """Set a wall in the specified direction for the cell at (x, y)."""
        if direction == 'N':
            self.grid[y][x] |= 1
        elif direction == 'E':
            self.grid[y][x] |= 2
        elif direction == 'S':
            self.grid[y][x] |= 4
        elif direction == 'W':
            self.grid[y][x] |= 8
        else:
            raise ValueError(f"Invalid direction: {direction}")

    def has_wall(self, x: int, y: int, direction: str) -> bool:
        """Check if there is a wall in the specified direction for the cell at (x, y)."""
        if direction == 'N':
            return (self.grid[y][x] & 1) != 0
        elif direction == 'E':
            return (self.grid[y][x] & 2) != 0
        elif direction == 'S':
            return (self.grid[y][x] & 4) != 0
        elif direction == 'W':
            return (self.grid[y][x] & 8) != 0
        else:
            raise ValueError(f"Invalid direction: {direction}")


if __name__ == "__main__":
    maze = Maze(5, 5)
    for row in maze.grid:
        print(row)
