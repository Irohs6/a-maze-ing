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
    PATTERN_42: list[list[int]] = [
        [15, 0, 15, 0, 15, 15, 15],
        [15, 0, 15, 0, 0, 0, 15],
        [15, 15, 15, 0, 15, 15, 15],
        [0, 0, 15, 0, 15, 0, 0],
        [0, 0, 15, 0, 15, 15, 15],
        ]

    _DIRECTIONS: dict[str, tuple[int, int]] = {
        'N': (0, -1),
        'E': (1, 0),
        'S': (0, 1),
        'W': (-1, 0),
    }

    def __init__(self, width: int, height: int) -> None:
        """Initialize an empty maze with given dimensions."""
        self.width: int = width
        self.height: int = height

        FULL_WALL = 1 | 2 | 4 | 8  # = 15
        self.grid = [[FULL_WALL for _ in range(width)] for _ in range(height)]
        self.forty_two_cells: set[tuple[int, int]] = set()
        self.forty_two_cells = self.place_42_center()

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

    def _is_border_wall(self, x: int, y: int, wall_direction: str) -> bool:
        """Return True if all outer-border cells
        have walls on their outer edge."""
        # Check top and bottom rows:
        if y == 0 and wall_direction == 'N':
            return True
        elif y == self.height - 1 and wall_direction == 'S':
            return True
        elif x == 0 and wall_direction == 'W':
            return True
        elif x == self.width - 1 and wall_direction == 'E':
            return True
        return False

    def place_42_center(self) -> set[tuple[int, int]]:
        """Place le motif '42' au centre du labyrinthe.

        Retourne le set des cellules occupées par le motif.
        Retourne un set vide si la taille du labyrinthe est insuffisante
        (le motif requiert au minimum pw+4 colonnes et ph+4 lignes pour
        laisser une marge de 2 cellules de chaque côté).
        """
        ph = len(self.PATTERN_42)
        pw = len(self.PATTERN_42[0])

        # Marge minimale de 2 cellules de chaque côté
        if self.width < pw + 4 or self.height < ph + 4:
            return set()

        start_x = (self.width - pw) // 2
        start_y = (self.height - ph) // 2

        for dy in range(ph):
            for dx in range(pw):
                if self.PATTERN_42[dy][dx] == 15:
                    x = start_x + dx
                    y = start_y + dy
                    self.grid[y][x] = 15
                    self.forty_two_cells.add((x, y))

        return self.forty_two_cells
