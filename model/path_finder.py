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

from collections import deque, defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.maze import Maze


class PathFinder:
    """Trouve le(s) plus court(s) chemin(s) dans un labyrinthe via BFS.

    Opère sur une instance de Maze et utilise le parcours en largeur (BFS)
    pour trouver tous les plus courts chemins de l'entrée vers la sortie.

    Optimisations clés :
    - Élagage BFS : dès que la sortie est découverte, les nœuds dont la
      distance dépasse celle de la sortie sont ignorés (pas d'exploration
      inutile du labyrinthe entier).
    - Reconstruction itérative : évite la récursion profonde sur les grands
      labyrinthes (pas de risque de RecursionError).

    Attributes:
        maze  : Instance Maze sur laquelle le pathfinding est effectué.
        entry : Coordonnées (x, y) de la cellule d'entrée.
        exit  : Coordonnées (x, y) de la cellule de sortie.

    Example::

        path_finder = PathFinder(maze, entry=(0, 0), exit=(19, 14))
        paths = path_finder.find_k_shortest_paths(k=1)
    """

    # Les quatre directions cardinales et leur vecteur de déplacement (dx, dy)
    DIRECTIONS: dict[str, tuple[int, int]] = {
        'N': (0, -1),
        'E': (1, 0),
        'S': (0, 1),
        'W': (-1, 0),
    }

    # Directions opposées : pour enregistrer la provenance d'une cellule
    REVERSE: dict[str, str] = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    def __init__(
        self,
        maze: Maze,
        entry: tuple[int, int],
        exit: tuple[int, int],
    ) -> None:
        """Initialise le PathFinder avec un labyrinthe et ses bornes.

        Args:
            maze  : Le labyrinthe à résoudre.
            entry : Coordonnées (x, y) de la cellule de départ.
            exit  : Coordonnées (x, y) de la cellule d'arrivée.
        """
        self.maze = maze
        self.entry = entry
        self.exit = exit

    def _compute_distance_and_predecessors(
        self,
    ) -> tuple[
        dict[tuple[int, int], int],
        dict[tuple[int, int], list[tuple[tuple[int, int], str]]],
    ]:
        """Effectue un BFS depuis l'entrée et construit la carte des distances
        ainsi que la liste des prédécesseurs pour chaque cellule atteinte.

        Optimisation : dès que la sortie est découverte à une distance
        ``exit_dist``, on arrête d'explorer les nœuds dont la distance
        est supérieure ou égale à ``exit_dist``. Cela évite de parcourir
        la totalité du labyrinthe quand la sortie est proche.

        Returns:
            dist : Dictionnaire ``{cellule: distance_depuis_entrée}``.
            pred : Dictionnaire ``{cellule: [(prédécesseur, direction), ...]}``.
                   Contient tous les prédécesseurs à distance optimale,
                   ce qui permet de reconstruire l'ensemble des plus courts
                   chemins.
        """
        start = self.entry
        maze = self.maze

        # dist[cell] = distance minimale depuis l'entrée
        dist: dict[tuple[int, int], int] = {start: 0}
        # pred[cell] = liste de (cellule_précédente, direction_empruntée)
        pred: dict[
            tuple[int, int], list[tuple[tuple[int, int], str]]
        ] = defaultdict(list)
        queue: deque[tuple[int, int]] = deque([start])

        # Distance à laquelle la sortie a été découverte (float('inf') tant
        # qu'elle n'est pas encore atteinte)
        exit_dist: float = float('inf')

        while queue:
            x, y = queue.popleft()
            d = dist[(x, y)]

            # Élagage : inutile d'explorer au-delà de la distance de la sortie
            if d >= exit_dist:
                continue

            for direction, (dx, dy) in self.DIRECTIONS.items():
                # Ignorer les voisins bloqués par un mur
                if maze.has_wall(x, y, direction):
                    continue

                nx, ny = x + dx, y + dy

                # Ignorer les cellules hors des limites du labyrinthe
                if not (0 <= nx < maze.width and 0 <= ny < maze.height):
                    continue

                pos = (nx, ny)

                if pos not in dist:
                    # Première découverte : enregistrer distance et prédécesseur
                    dist[pos] = d + 1
                    pred[pos].append(((x, y), direction))
                    queue.append(pos)

                    # Mémoriser la distance de la sortie à sa 1ère découverte
                    if pos == self.exit:
                        exit_dist = d + 1

                elif dist[pos] == d + 1:
                    # Chemin alternatif de même longueur : prédécesseur
                    # supplémentaire pour reconstruire k chemins distincts
                    pred[pos].append(((x, y), direction))

        return dist, pred

    def _reconstruct_k_paths(
        self,
        pred: dict[tuple[int, int], list[tuple[tuple[int, int], str]]],
        k: int,
    ) -> list[list[str]]:
        """Reconstruit jusqu'à k plus courts chemins de la sortie à l'entrée
        en remontant le graphe des prédécesseurs (DFS itératif).

        L'approche itérative (pile explicite) remplace la récursion originale
        afin d'éviter tout risque de ``RecursionError`` sur des labyrinthes
        dont les chemins sont très longs.

        Args:
            pred : Graphe de prédécesseurs renvoyé par
                   ``_compute_distance_and_predecessors``.
            k    : Nombre maximal de chemins à retourner.

        Returns:
            Liste de chemins, chacun étant une liste de directions
            (ex. ``['E', 'E', 'S', 'S', 'W']``) allant de l'entrée à la sortie.
        """
        start = self.entry
        goal = self.exit
        result_paths: list[list[str]] = []

        # Chaque élément de la pile contient :
        #   - la cellule courante (on remonte depuis la sortie vers l'entrée)
        #   - le chemin accumulé en ordre inversé (sortie → cellule courante)
        stack: list[tuple[tuple[int, int], list[str]]] = [(goal, [])]

        while stack and len(result_paths) < k:
            cell, path_reversed = stack.pop()

            if cell == start:
                # Chemin complet trouvé : inverser pour obtenir entrée → sortie
                result_paths.append(path_reversed[::-1])
                continue

            # Remonter vers chaque prédécesseur (+ direction empruntée)
            for (px, py), direction in pred.get(cell, []):
                stack.append(((px, py), path_reversed + [direction]))

        return result_paths

    def _build_connections_dict(
        self, path: list[str]
    ) -> dict[tuple[int, int], tuple[str]]:
        """Convertit un chemin (liste de directions) en dict de connexions.

        Pour chaque cellule traversée, enregistre les directions ouvertes :
        la direction de sortie (vers la cellule suivante) et la direction
        d'entrée (depuis la cellule précédente, via REVERSE).

        Args:
            path : Liste de directions (ex. ``['E', 'S', 'S', 'W']``) de
                   l'entrée vers la sortie.

        Returns:
            Dictionnaire ``{(x, y): {directions ouvertes}}`` utilisé par la vue
            pour colorier les cellules du chemin solution.
        """
        connections: dict[tuple[int, int], tuple[str]] = {}
        x, y = self.entry

        # Initialiser la cellule d'entrée
        connections[(x, y)] = []

        for direction in path:
            # La cellule courante peut sortir dans cette direction
            connections[(x, y)].append(direction)

            dx, dy = self.DIRECTIONS[direction]
            x, y = x + dx, y + dy

            # Initialiser la cellule suivante si elle n'a pas encore été visitée
            if (x, y) not in connections:
                connections[(x, y)] = []

            # La cellule d'arrivée sait d'où elle vient (direction inverse)
            connections[(x, y)].append(self.REVERSE[direction])

        return connections

    def _bfs_with_forbidden_edge(
        self,
        forbidden_u: tuple[int, int],
        forbidden_v: tuple[int, int],
    ) -> list[str] | None:
        """BFS standard de entry à exit en interdisant l'arête u→v.

        Une arête du plus court chemin est temporairement ignorée, forçant
        le BFS à trouver un chemin de contournement s'il existe.

        Args:
            forbidden_u : Cellule source de l'arête à interdire.
            forbidden_v : Cellule destination de l'arête à interdire.

        Returns:
            Liste de directions si un chemin alternatif existe, None sinon.
        """
        maze = self.maze
        start = self.entry
        goal = self.exit

        dist: dict[tuple[int, int], int] = {start: 0}
        # pred[cell] = (cellule_précédente, direction_empruntée)
        pred: dict[
            tuple[int, int],
            tuple[tuple[int, int], str] | None
        ] = {start: None}
        queue: deque[tuple[int, int]] = deque([start])

        while queue:
            x, y = queue.popleft()
            if (x, y) == goal:
                break
            for direction, (dx, dy) in self.DIRECTIONS.items():
                if maze.has_wall(x, y, direction):
                    continue
                nx, ny = x + dx, y + dy
                if not (0 <= nx < maze.width and 0 <= ny < maze.height):
                    continue
                neighbor = (nx, ny)
                # Interdire l'arête forbidden_u → forbidden_v
                if (x, y) == forbidden_u and neighbor == forbidden_v:
                    continue
                if neighbor not in dist:
                    dist[neighbor] = dist[(x, y)] + 1
                    pred[neighbor] = ((x, y), direction)
                    queue.append(neighbor)

        if goal not in pred:
            return None

        # Reconstruction du chemin (de la sortie vers l'entrée)
        path: list[str] = []
        cell = goal
        while pred[cell] is not None:
            prev_cell, direction = pred[cell]
            path.append(direction)
            cell = prev_cell
        path.reverse()
        return path

    def _find_extra_paths(
        self,
        already_found: list[list[str]],
        max_extra: int,
    ) -> list[list[str]]:
        """Cherche jusqu'à max_extra chemins alternatifs en supprimant
        successivement chaque arête du plus court chemin (principe de Yen).

        Pour chaque arête (u→v) du plus court chemin, un BFS est relancé
        en interdisant cette arête. Si un chemin est trouvé, il prouve
        l'imperfection du labyrinthe (boucle détectée).

        Garantie : si le labyrinthe est imparfait, au moins une arête du
        plus court chemin appartient à un cycle, et le BFS sans cette arête
        trouvera un chemin de contournement — quelle que soit la taille du
        labyrinthe.

        Complexité : O(path_len × maze_cells) — très rapide en pratique
        puisque chaque BFS est O(maze_cells).

        Args:
            already_found : Chemins déjà connus (listes de directions).
            max_extra     : Nombre maximal de chemins alternatifs à retourner.

        Returns:
            Liste de chemins alternatifs (peut être vide si labyrinthe
            parfait).
        """
        if not already_found or max_extra <= 0:
            return []

        found_set: set[tuple[str, ...]] = {tuple(p) for p in already_found}
        extra: list[list[str]] = []

        # Reconstruire la séquence de cellules du premier plus court chemin
        cell_seq: list[tuple[int, int]] = [self.entry]
        x, y = self.entry
        for direction in already_found[0]:
            dx, dy = self.DIRECTIONS[direction]
            x, y = x + dx, y + dy
            cell_seq.append((x, y))

        # Pour chaque arête (u→v) du chemin, interdire cette arête et re-BFS
        for i in range(len(cell_seq) - 1):
            if len(extra) >= max_extra:
                break
            u, v = cell_seq[i], cell_seq[i + 1]
            path = self._bfs_with_forbidden_edge(u, v)
            if path is None:
                continue
            path_t = tuple(path)
            if path_t not in found_set:
                extra.append(path)
                found_set.add(path_t)

        return extra

    def find_k_shortest_paths(
        self, k: int = 1, n_extra: int = 2
    ) -> list[dict[tuple[int, int], list[str]]]:
        """Trouve le plus court chemin, puis jusqu'à n_extra
        chemins alternatifs.

        - Le 1er chemin (k=1 par défaut) est le plus court via BFS.
        - Les n_extra chemins suivants peuvent être plus longs ; ils servent
          à confirmer si le labyrinthe est parfait (0 alternatif trouvé)
          ou imparfait (au moins 1 alternatif trouvé).
        - Total retourné : au maximum k + n_extra (défaut : 3).

        Args:
            k       : Nombre max de plus courts chemins (défaut : 1).
            n_extra : Nombre max de chemins alternatifs supplémentaires
                      (défaut : 2). Passer 0 pour désactiver.

        Returns:
            Liste de dictionnaires de connexions ``[{(x,y): {dirs}}, ...]``.
            Retourne une liste vide si la sortie est inaccessible depuis
            l'entrée.
        """
        dist, pred = self._compute_distance_and_predecessors()

        # Sortie inaccessible : aucun chemin possible
        if self.exit not in dist:
            return []

        # 1. Plus courts chemins via BFS
        shortest_paths = self._reconstruct_k_paths(pred, k)

        # 2. Chemins alternatifs (longueur quelconque) via DFS borné
        extra_paths = self._find_extra_paths(shortest_paths, max_extra=n_extra)

        all_paths = shortest_paths + extra_paths
        return [self._build_connections_dict(path) for path in all_paths]
