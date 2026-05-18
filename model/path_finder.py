# model/path_finder.py — Shortest path search algorithm.
# Contains the PathFinder class operating on a Maze instance.
# Implements a BFS (Breadth-First Search) algorithm to find
# the shortest valid path between entry and exit.
# Provides methods to:
#   - compute and return the path as a list of directions (N, E, S, W)
#   - find up to k shortest paths from entry to exit
#   - build a per-cell connections dictionary for rendering
# The result is used both for writing to the output file
# and for visual display of the solution.

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.maze import Maze


class PathFinder:
    """Finds the shortest path from entry to exit in a maze using BFS.
    """

    REVERSE: dict[str, str] = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    def __init__(
        self,
        maze: Maze,
        entry: tuple[int, int],
        exit: tuple[int, int],
    ) -> None:
        """Initializes the PathFinder with a maze and its boundaries.

        Args:
            maze  : The maze to solve.
            entry : Coordinates (x, y) of the starting cell.
            exit  : Coordinates (x, y) of the goal cell.
        """
        self.maze = maze
        self.entry = entry
        self.exit = exit

    def _build_connections(
        self, path: list[str]
    ) -> list[tuple[int, int, str]]:
        """Converts a path (list of directions)
            into a list of positioned moves.

        Args:
            path : List of directions (e.g., ``['E', 'S', 'S', 'W']``) from
                   the entry to the exit.

        Returns:
            List of tuples ``(x, y, direction)`` where each tuple represents
            the cell coordinates and the direction taken to leave that cell.
        """
        connections: list[tuple[int, int, str]] = []
        x, y = self.entry

        for direction in path:
            # The current cell can exit in this direction
            connections.append((x, y, direction))

            dx, dy = self.maze._DIRECTIONS[direction]
            x, y = x + dx, y + dy

        return connections

    def _shortest_path(self) -> list[str] | None:
        """Finds the shortest path from entry to exit via BFS.

        Returns:
            List of directions (e.g., ``['E', 'E', 'S', 'S', 'W']``) if a path
            exists, or None if the exit is inaccessible from the entry.
        """
        maze = self.maze
        start = self.entry
        goal = self.exit

        dist: dict[tuple[int, int], int] = {start: 0}
        # pred[cell] = (previous_cell, direction_taken)
        pred: dict[
            tuple[int, int],
            tuple[tuple[int, int], str] | None
        ] = {start: None}
        queue: deque[tuple[int, int]] = deque([start])

        while queue:
            x, y = queue.popleft()
            if (x, y) == goal:
                break
            for direction, (dx, dy) in self.maze._DIRECTIONS.items():
                if maze.has_wall(x, y, direction):
                    continue

                neighbor_x, neighbor_y = x + dx, y + dy
                if not (0 <= neighbor_x < maze.width
                        and 0 <= neighbor_y < maze.height):
                    continue

                neighbor = (neighbor_x, neighbor_y)

                if neighbor not in dist:
                    dist[neighbor] = dist[(x, y)] + 1
                    pred[neighbor] = ((x, y), direction)
                    queue.append(neighbor)

        if goal not in pred:
            return None

        # Reconstruct the path (from exit to entry)
        path: list[str] = []
        cell = goal
        if pred[cell] is None:
            return None
        while pred[cell] is not None:
            prev = pred[cell]
            if prev is None:
                break
            prev_cell, direction = prev
            path.append(direction)
            cell = prev_cell

        path.reverse()
        return path
