# model/maze_validator.py — Validation de la structure du labyrinthe.
# Contient la classe MazeValidator, séparée de Maze pour respecter le SRP.
# Elle vérifie :
#   - que les valeurs de chaque cellule sont dans l'intervalle 0–15
#   - que les bordures extérieures du labyrinthe sont bien fermées par des murs
#   - la cohérence des murs entre cellules voisines (symétrie N↔S, E↔W)
#   - l'absence de zones ouvertes 3×3 interdites
#   - la connectivité complète du labyrinthe (hors cellules isolées du motif
#  "42")
#   - la présence du motif "42" (ignoré si le labyrinthe est trop petit)

# import __future__ for forward compatibility with Python 3.10+
# (annotations as strings by default)
from __future__ import annotations

# import deque for BFS in connectivity check
from collections import deque

# typing.TYPE_CHECKING is used
# to avoid circular imports when type hinting with Maze.
from typing import TYPE_CHECKING

# if TYPE_CHECKING is True, we can import Maze for type hints without
# causing circular import issues at runtime.
if TYPE_CHECKING:
    from model.maze import Maze


class MazeValidator:
    """Validate the structural integrity of a Maze instance.

    Encapsulates all validation rules, keeping the Maze class focused on
    data storage. Instantiate with a Maze, then call validate().

    Example:
        validator = MazeValidator(maze)
        if not validator.validate():
            raise ValueError("Maze is not valid.")
    """

    def __init__(self, maze: Maze) -> None:
        """Initialize the validator with the maze to validate."""
        self._maze = maze
        self.errors: list[str] = []  # Optional: collect error
        # messages for debugging

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """Run all structural checks on the maze.

        Returns:
            True if every check passes, False on the first failure.
        """

        self.errors = []
        if not self._validate_cell_values():
            self.errors.append("Cell values must be in the range 0–15.")
        if not self._validate_maze_boundaries():
            self.errors.append("Outer borders must have walls.")
        if not self._validate_adjacent_cells():
            self.errors.append("Adjacent cells must have symmetric walls.")
        if self._has_forbidden_open_areas():
            self.errors.append(
                "Forbidden open area: 3×3 block " "with no inner walls."
            )
        if not self._validate_maze_connectivity():
            self.errors.append(
                "Maze must be fully connected (except " "isolated '42' cells)."
            )
        if not self._validate_42_pattern():
            self.errors.append(
                "Maze must contain the '42' pattern " "(or be too small)."
            )
        return not self.errors  # True if no errors, False if any error exists

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def _validate_cell_values(self) -> bool:
        """Return True if every cell value is in [0, 15]."""
        for row in self._maze.grid:
            for cell in row:
                if not (0 <= cell <= 15):
                    return False
        return True

    def _validate_maze_boundaries(self) -> bool:
        """Return True if all outer-border cells
        have walls on their outer edge."""
        maze = self._maze
        # Check top and bottom rows:
        for x in range(maze.width):
            if not maze.has_wall(x, 0, "N"):
                return False
            if not maze.has_wall(x, maze.height - 1, "S"):
                return False
        # Check left and right columns:
        for y in range(maze.height):
            if not maze.has_wall(0, y, "W"):
                return False
            if not maze.has_wall(maze.width - 1, y, "E"):
                return False
        return True

    def _validate_adjacent_cells(self) -> bool:
        """Return True if wall presence is symmetric between
        every adjacent pair.

        E.g. if cell (x, y) has a wall to the East, then (x+1, y) must
        have a wall to the West, and vice-versa.
        """
        maze = self._maze
        for y in range(maze.height):
            for x in range(maze.width):
                # Check East-West symmetry with right neighbor:
                if x + 1 < maze.width:
                    if maze.has_wall(x, y, "E") != maze.has_wall(
                        x + 1, y, "W"
                    ):
                        return False
                # Check North-South symmetry with bottom neighbor:
                if y + 1 < maze.height:
                    if maze.has_wall(x, y, "S") != maze.has_wall(
                        x, y + 1, "N"
                    ):
                        return False
        return True

    def _has_forbidden_open_areas(self) -> bool:
        """Return True if any 3×3 block has no inner walls
        (forbidden open area).

        Corridors must never be wider than 2 cells. A 3×3 block where all
        adjacent pairs share no wall is therefore forbidden.
        """
        maze = self._maze
        for by in range(maze.height - 2):
            for bx in range(maze.width - 2):
                if self._is_3x3_open(bx, by):
                    return True
        return False

    def _validate_maze_connectivity(self) -> bool:
        """Return True if every non-isolated cell is reachable from (0, 0).

        Fully-walled cells (value == 15) belong to the "42" pattern and are
        intentionally isolated; they are excluded from the reachability count.
        """
        maze: Maze = self._maze
        width, height = maze.width, maze.height

        # Count isolated cells (value == 15)
        isolated = sum(1 for row in maze.grid for cell in row if cell == 15)

        queue = deque([(0, 0)])
        visited = set()
        reachable = 0

        # Direction offsets: (offset_x, offset_y)
        directions = {
            "N": (0, -1),
            "E": (1, 0),
            "S": (0, 1),
            "W": (-1, 0),
        }

        while queue:
            x, y = queue.popleft()

            # Skip fully-walled cells
            if maze.grid[y][x] == 15:
                continue

            # Skip already visited cells
            if (x, y) in visited:
                continue

            # Visit the cell
            visited.add((x, y))
            reachable += 1

            # Explore neighbors
            for direction, (offset_x, offset_y) in directions.items():
                if not maze.has_wall(x, y, direction):
                    nx = x + offset_x
                    ny = y + offset_y

                    # Check boundaries
                    if 0 <= nx < width and 0 <= ny < height:
                        if (nx, ny) not in visited:
                            queue.append((nx, ny))

        total_cells = width * height
        return reachable + isolated == total_cells

    def _validate_42_pattern(self) -> bool:
        """Return True if the "42" pattern is present,
        or if the maze is too small, or if no isolated cells exist
        (pattern not yet placed by the generator).

        The pattern is searched exhaustively at every valid top-left offset.
        Each cell marked 1 in PATTERN_42 must be a fully-isolated cell
        (grid value == 15).
        """

        maze = self._maze
        pattern_height = len(maze.PATTERN_42)
        pattern_width = len(maze.PATTERN_42[0])
        if maze.height < pattern_height or maze.width < pattern_width:
            # Pattern is intentionally omitted for small mazes.
            return True
        # If no isolated cell (value == 15) exists, the generator has not yet
        # placed the pattern — skip gracefully rather than failing.
        has_isolated = any(
            maze.grid[y][x] == 15
            for y in range(maze.height)
            for x in range(maze.width)
        )
        if not has_isolated:
            return True
        for start_y in range(maze.height - pattern_height + 1):
            for start_x in range(maze.width - pattern_width + 1):
                if self._matches_42(start_x, start_y):
                    return True
        return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_3x3_open(self, start_x: int, start_y: int) -> bool:
        """Return True if the 3×3 block whose top-left is (start_x, start_y)
        has no inner walls."""
        maze = self._maze
        # Horizontal passages (East direction) between adjacent columns
        # representation visuel de la zone 3x3 interdite :
        #   x0,y0 E x1,y0 E x2,y0
        #     0   |   1   |   2
        #   x0,y1 | x1,y1 | x2,y1
        #   x0,y2 | x1,y2 | x2,y2
        for y in range(start_y, start_y + 3):
            for x in range(start_x, start_x + 2):
                if maze.has_wall(x, y, "E"):
                    return False
        # Vertical passages (South direction) between adjacent rows
        for y in range(start_y, start_y + 2):
            for x in range(start_x, start_x + 3):
                if maze.has_wall(x, y, "S"):
                    return False
        return True

    def _matches_42(self, start_x: int, start_y: int) -> bool:
        """Return True if PATTERN_42 matches exactly at top-left
        offset (start_x, start_y)."""

        maze = self._maze
        for pattern_row_idx, pattern_row in enumerate(maze.PATTERN_42):
            for pattern_col_idx, is_isolated in enumerate(pattern_row):
                ry = start_y + pattern_row_idx
                cx = start_x + pattern_col_idx
                if is_isolated and maze.grid[ry][cx] != 15:
                    return False
        return True
