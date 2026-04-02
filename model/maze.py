# model/maze.py — Structure de données représentant le labyrinthe.
# Contient la classe Maze qui stocke la grille de cellules et leurs murs.
# Chaque cellule est un entier sur 4 bits (Nord, Est, Sud, Ouest).
# La classe fournit des méthodes pour :
#   - accéder et modifier les murs d'une cellule donnée
#   - encoder le labyrinthe en hexadécimal pour la sortie
# La validation est déléguée à MazeValidator (model/maze_validator.py).
# Utilise des annotations de type et des docstrings conformes à PEP 257.


class Maze:
    """Represents a maze as a grid of cells with walls.

    Each cell is encoded as a 4-bit integer:
        - bit 0 (1): wall to the North
        - bit 1 (2): wall to the East
        - bit 2 (4): wall to the South
        - bit 3 (8): wall to the West

    Provides methods to access and modify cell walls and encode the
    maze for output. Validation is handled by MazeValidator.
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
        """Check if there is a wall in the given direction for cell (x, y)."""
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

    def remove_wall(self, x: int, y: int, direction: str) -> None:
        """Remove a wall in the specified direction for the cell at (x, y)."""
        if direction == 'E' and x < self.width - 1:
            self.grid[y][x] &= ~2
            self.grid[y][x + 1] &= ~8
        elif direction == 'W' and x > 0:
            self.grid[y][x] &= ~8
            self.grid[y][x - 1] &= ~2
        elif direction == 'N' and y > 0:
            self.grid[y][x] &= ~1
            self.grid[y - 1][x] &= ~4
        elif direction == 'S' and y < self.height - 1:
            self.grid[y][x] &= ~4
            self.grid[y + 1][x] &= ~1
        else:
            raise ValueError(f"Invalid direction: {direction}")

#          +------------+ +------------+ +------------+
#          |    N(1)    | |    N(1)    | |    N(1)    |
#          | W   y=0  E | | W   y=0  E | | W   y=0  E |
#          |(8)  x=0 (2)| |(8)  x=1 (2)| |(8)  x=2 (2)|
#          |   S(4)     | |   S(4)     | |   S(4)     |
#          +------------+ +------------+ +------------+
#          +------------+ +------------+ +------------+
#          |    N(1)    | |    N(1)    | |    N(1)    |
#          | W   y=1  E | | W   y=1  E | | W   y=1  E |
#          |(8)  x=0 (2)| |(8)  x=1 (2)| |(8)  x=2 (2)|
#          |   S(4)     | |   S(4)     | |   S(4)     |
#          +------------+ +------------+ +------------+
#          +------------+ +------------+ +------------+
#          |    N(1)    | |    N(1)    | |    N(1)    |
#          | W   y=2  E | | W   y=2  E | | W   y=2  E |
#          |(8)  x=0 (2)| |(8)  x=1 (2)| |(8)  x=2 (2)|
#          |   S(4)     | |   S(4)     | |   S(4)     |
#          +------------+ +------------+ +------------+

    def encode_hex(self) -> str:
        """Encode the maze grid as a hexadecimal string."""
        hex_string = ""
        for row in self.grid:
            for cell in row:
                hex_string += f"{cell:X}"
            hex_string += "\n"
        return hex_string

    def _cell_wall_count(self, x: int, y: int) -> int:
        """Return the number of walls surrounding cell (x, y) (0–4)."""
        return bin(self.grid[y][x]).count('1')

    def _get_neighbors_of_cell(self, x: int, y: int) -> list:
        directions = {
            'N': (0, -1),
            'E': (1, 0),
            'S': (0, 1),
            'W': (-1, 0),
        }
        neighbors = []
        for direction, (offset_x, offset_y) in directions.items():
            nx = x + offset_x
            ny = y + offset_y
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append((nx, ny, direction))
        return neighbors

    def _get_maze_boundaries(self):
        # Check top and bottom rows:
        boundaries = set()
        for x in range(self.width):
            boundaries.add((x, 0))
            boundaries.add((x, self.height - 1))
        # Check left and right columns:
        for y in range(self.height):
            boundaries.add((0, y))
            boundaries.add((self.width - 1, y))
        return boundaries

if __name__ == "__main__":
    maze = Maze(5, 5)
    for row in maze.grid:
        print(row)
