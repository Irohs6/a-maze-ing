import random
from .algorithm import Algorithm

class Kruksal(Algorithm):
    perfect: bool = False
    REVERSE: dict[str, str] = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
    # Maximum number of global attempts before giving up

    def _is_42_wall(self, x: int, y: int, wall_direction: str) -> bool:
        if (
            self._get_direction_neighbor(x, y, wall_direction)
            not in self.forty_two_cells
        ):
            return False
        else:
            return True

    def _breakable_walls(self, x: int, y: int) -> list[str]:
        eligible_walls: list[str] = []
        for direction in ["N", "E", "S", "W"]:
            if (
                self.maze.has_wall(x, y, direction)
                and self._get_direction_neighbor(x, y, direction)
                not in self.forty_two_cells
                and not self.maze._is_border_wall(x, y, direction)
                and not self._is_42_wall(x, y, direction)
                and (x, y) not in self._union[0]
                and self._cell_wall_count(x, y) > 2
            ):
                eligible_walls.append(direction)
        return eligible_walls

    def _get_eligible_walls(self) -> list[tuple[int, int, str]]:
        self._eligible_walls = []
        directions = ["N", "E", "S", "W"]
        for y in range(self.height):
            for x in range(self.width):
                for direction in directions:
                    if (
                        self._get_direction_neighbor(x, y, direction)
                        not in self.forty_two_cells
                        and not self.maze._is_border_wall(x, y, direction)
                        and (x, y) not in self.forty_two_cells
                    ):
                        self._eligible_walls.append((x, y, direction))
        return self._eligible_walls

    def _find_in_union(
        self, coordinates: tuple[int, int], neighbor: tuple[int, int]
    ) -> list[int] | bool:
        """Return the indexes of the sets in the union list that
            contain the given coordinates and neighbor."""

        indexes: list[int] = []

        for index, set in enumerate(self._union):

            if coordinates in set and neighbor in set:

                return False

            elif coordinates in set or neighbor in set:

                indexes.append(index)

        return indexes

    def _concatenate_in_union(self, indexes: list[int]) -> None:
        """Merge the two sets at the given indexes in the union list."""

        self._union[indexes[0]] = self._union[indexes[0]].union(
            self._union[indexes[1]])

        self._union.pop(indexes[1])

    def _cell_wall_count(self, x: int, y: int) -> int:
        """Return the number of walls surrounding cell (x, y) (0–4)."""
        return self.maze.grid[y][x].bit_count()

    def generate(self) -> list[tuple[int, int, str]]:
        """Generates the maze using a randomized version
        of Kruskal's algorithm."""
        _eligible_walls = self._get_eligible_walls()

        random.shuffle(_eligible_walls)
        while len(self._union) > 1:
            x, y, wall_direction = _eligible_walls.pop()
            neighbor = self._get_direction_neighbor(x, y, wall_direction)
            indexes = self._find_in_union((x, y), neighbor)
            if indexes:
                self.maze.remove_wall(x, y, wall_direction)
                self._concatenate_in_union(indexes)
                self.tracks.append((x, y, wall_direction))
        return self.tracks
