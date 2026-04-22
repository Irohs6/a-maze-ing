
import random
from .algorithm import Algorithm


class Kruksal(Algorithm):
    REVERSE: dict[str, str] = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
    # Maximum number of global attempts before giving up

    def _get_eligible_walls(self) -> list[tuple[int, int, str]]:
        self._eligible_walls = []
        directions = ["N", "E", "S", "W"]
        for y in range(self.height):
            for x in range(self.width):
                for direction in directions:
                    if (
                        not self.maze._is_border_wall(x, y, direction)
                        and not self._is_42_wall(x, y, direction)
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

        if len(indexes) == 2:
            self._union[indexes[0]] = self._union[indexes[0]].union(
                self._union[indexes[1]])
            self._union.pop(indexes[1])

    def generate(self) -> list[tuple[int, int, str]]:
        """Generates the maze using a randomized version
        of Kruskal's algorithm."""
        _eligible_walls = self._get_eligible_walls()

        random.shuffle(_eligible_walls)
        while len(self._union) > 1:
            if not _eligible_walls:
                break
            x, y, wall_direction = _eligible_walls.pop()
            neighbor = self._get_direction_neighbor(x, y, wall_direction)
            indexes: list[int] | bool = self._find_in_union((x, y), neighbor)
            if isinstance(indexes, list):
                self.maze.remove_wall(x, y, wall_direction)
                self._concatenate_in_union(indexes)
                self.tracks.append((x, y, wall_direction))
                nx, ny = neighbor
                opposite_direction = self.REVERSE[wall_direction]
                try:
                    _eligible_walls.remove((nx, ny, opposite_direction))
                except ValueError:
                    pass
        if self.is_perfect is False:
            # Call second loop to break a 15% additional
            # walls for an imperfect maze
            self.second_loop()

        return self.tracks
