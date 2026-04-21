# model/path_finder.py — Algorithme de recherche du chemin le plus court.
# Contient la classe PathFinder qui opère sur une instance de Maze.
# Implémente un algorithme BFS (Breadth-First Search) pour trouver
# le chemin valide le plus court entre l'entrée et la sortie.
# Fournit des méthodes pour :
#   - calculer et retourner le chemin sous forme de liste de directions
#     (N, E, S, W)
#   - retrouver jusqu'à k plus courts chemins depuis l'entrée vers la sortie
#   - construire un dictionnaire de connexions par cellule pour l'affichage
# Le résultat est utilisé à la fois pour l'écriture dans le fichier de sortie
# et pour l'affichage visuel de la solution.

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

    def _build_connections_dict(
        self, path: list[str]
    ) -> dict[tuple[int, int], list[str]]:
        """Converts a path (list of directions) into a connections dictionary.

        For each traversed cell, records the open directions:
        the exit direction (towards the next cell) and the entry direction
        (from the previous cell, via REVERSE).

        Args:
            path : List of directions (e.g., ``['E', 'S', 'S', 'W']``) from
                   the entry to the exit.

        Returns:
            Dictionary ``{(x, y): {open directions}}`` used by the view
            to color the cells of the solution path.
        """
        connections: dict[tuple[int, int], list[str]] = {}
        x, y = self.entry

        # Initialize the entry cell
        connections[(x, y)] = []

        for direction in path:
            # The current cell can exit in this direction
            connections[(x, y)].append(direction)

            dx, dy = self.maze._DIRECTIONS[direction]
            x, y = x + dx, y + dy

            # Initialize the next cell if it hasn't been visited yet
            if (x, y) not in connections:
                connections[(x, y)] = []

            # The destination cell knows where it came from (reverse direction)
            connections[(x, y)].append(self.REVERSE[direction])

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

    def find(self) -> list[dict[tuple[int, int], list[str]]]:
        """Finds the shortest path from entry to exit and
        returns a connections dictionary.

        Returns:
            List containing a single dictionary ``{(x, y): [directions]}``
            representing the shortest path found, or an empty list if
            no path exists.
        """

        path = self._shortest_path()
        if path is None:
            return []

        connections = self._build_connections_dict(path)

        return [connections]
