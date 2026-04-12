# Pistes d'amélioration — Algorithme Kruskal (A-Maze-ing)

> Objectif : dépasser le cap des **150×150** tout en restant < 1 s en moyenne.
> Actuellement : 101×101 ≈ 4 s (moy.), 151×151 → divergence / > 44 s.

---

## 1. Union-Find (Disjoint Set Union) — gain estimé ×10 à ×50

### Problème actuel

La vérification de connectivité utilise un **BFS complet** (`MazeValidator._validate_maze_connectivity`) à chaque itération de `_second_loop`. Sur un 101×101, cela représente 10 201 cellules × 245 appels = **~2.5 millions de visites BFS** par génération.

### Solution

Implémenter une structure **Union-Find avec union par rang et path compression** pour maintenir la connectivité **incrémentalement** : quand on abat un mur, on fusionne deux composantes en O(α(N)) ≈ O(1) amorti.

```python
# utils/union_find.py
class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank   = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        """Retourne True si a et b étaient dans des composantes différentes."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True

    def connected(self, a: int, b: int) -> bool:
        return self.find(a) == self.find(b)

    def component_count(self) -> int:
        return sum(1 for i in range(len(self.parent)) if self.find(i) == i)
```

### Intégration dans Kruskal

```python
# Dans Kruksal.generate() :
uf = UnionFind(self.width * self.height)
# Encoder chaque cellule (x, y) → x + y * width

def cell_id(x, y): return x + y * self.width

# Lors de remove_wall :
uf.union(cell_id(x, y), cell_id(nx, ny))

# Vérification de connectivité O(1) :
if uf.component_count() - len(pattern_cells) == 1:
    # labyrinthe connexe !
```

**Gain attendu** : suppression du BFS O(N) → O(α(N)) ≈ O(1), soit un gain de ×10 à ×50 sur les grandes tailles.

---

## 2. Vrai algorithme de Kruskal avec liste de murs — gain estimé ×5

### Problème actuel

L'implémentation actuelle ne suit **pas** le vrai algorithme de Kruskal :
- Elle itère cellule par cellule et abat un mur aléatoire par cellule
- Le résultat est un labyrinthe partiellement connecté qu'il faut ensuite corriger

### Solution : Kruskal classique

1. Construire la liste de **tous les murs intérieurs**
2. La **mélanger** (`random.shuffle`)
3. Pour chaque mur, si les deux cellules sont dans des composantes différentes, abattre le mur (union-find)
4. S'arrêter quand toutes les cellules non-42 sont dans la même composante

```python
import random

def generate_true_kruskal(self) -> list:
    uf = UnionFind(self.width * self.height)
    
    # Exclure les cellules du motif 42
    pattern_ids = {x + y * self.width for x, y in self.maze.forty_two_cells}
    
    # Construire tous les murs intérieurs horizontaux et verticaux
    walls = []
    for y in range(self.height):
        for x in range(self.width):
            if (x + y * self.width) in pattern_ids:
                continue
            if x + 1 < self.width and ((x+1) + y * self.width) not in pattern_ids:
                walls.append((x, y, 'E'))
            if y + 1 < self.height and (x + (y+1) * self.width) not in pattern_ids:
                walls.append((x, y, 'S'))
    
    random.shuffle(walls)
    track = []
    
    for x, y, direction in walls:
        dx, dy = self.maze._DIRECTIONS[direction]
        nx, ny = x + dx, y + dy
        a = x + y * self.width
        b = nx + ny * self.width
        if uf.union(a, b):  # composantes différentes → abattre le mur
            self.maze.remove_wall(x, y, direction)
            track.append((x, y, direction))
    
    return track
```

**Avantage** : génère un labyrinthe **parfaitement connexe** dès la première passe — plus besoin de `_second_loop` ni de BFS de correction. La `_second_loop` peut rester pour les labyrinthes imparfaits (abattre des murs supplémentaires).

---

## 3. Éviter la copie profonde à chaque tentative — gain estimé ×2

### Problème actuel

```python
# Dans generate() — copie O(N) à chaque tentative
maze_attempt = copy.copy(self.maze)
maze_attempt.grid = [row[:] for row in self.maze.grid]
potential_maze = copy.copy(maze_attempt)
potential_maze.grid = [row[:] for row in maze_attempt.grid]
```

Ce double `copy.copy` + `[row[:]]` alloue deux nouvelles grilles complètes par tentative.

### Solution : snapshot/restore avec numpy ou bytearray

```python
import numpy as np

# Stocker la grille initiale comme snapshot plat
snapshot = np.array(self.maze.grid, dtype=np.uint8)

# Restauration instantanée O(N) sans réallocation :
np.copyto(working_grid, snapshot)
```

Ou, sans numpy, utiliser un `bytearray` plat :

```python
snapshot = bytearray(cell for row in self.maze.grid for cell in row)
# Restaurer :
for i, cell in enumerate(snapshot):
    self.maze.grid[i // self.width][i % self.width] = cell
```

**Gain** : réduit les allocations mémoire de ~50 % sur les grandes tailles.

---

## 4. Rendre _second_loop incrémentale — gain estimé ×3 à ×5

### Problème actuel

```python
# _second_loop recalcule _to_destroy à chaque appel complet
_to_destroy = {
    (x, y)
    for x in range(self.width)
    for y in range(self.height)
    if maze._cell_wall_count(x, y) > 2 ...
}
```

Ce set comprehension parcourt toute la grille O(N) à chaque itération.

### Solution : file de mise à jour incrémentale

Maintenir un `set` de cellules "à corriger" mis à jour au fur et à mesure des abattements :

```python
to_fix: set[tuple[int, int]] = set()

def on_wall_removed(x, y, direction):
    """Appelé après chaque remove_wall — met to_fix à jour."""
    for cell in [(x, y), get_neighbor(x, y, direction)]:
        if maze._cell_wall_count(*cell) > 2:
            to_fix.add(cell)
        else:
            to_fix.discard(cell)

# _second_loop ne parcourt que to_fix (souvent << N)
while to_fix:
    x, y = to_fix.pop()
    ...
```

---

## 5. Parallélisation des tentatives — gain dépend du CPU

### Problème actuel

Les 30 tentatives globales sont séquentielles.

### Solution : `concurrent.futures.ProcessPoolExecutor`

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

def _single_attempt(width, height, seed):
    """Fonction picklable pour un sous-processus."""
    import random
    random.seed(seed)
    maze = Maze(width, height)
    # ... tentative Kruskal ...
    return grid_result if success else None

with ProcessPoolExecutor(max_workers=4) as ex:
    futures = [ex.submit(_single_attempt, w, h, seed) for seed in seeds]
    for f in as_completed(futures):
        result = f.result()
        if result:
            # Premier succès → annuler les autres
            break
```

**Limite** : overhead de pickle/IPC — efficace seulement au-delà de 81×81.

---

## 6. Cache de `_cell_wall_count` — gain modeste ×1.2

### Problème actuel

`_cell_wall_count(x, y)` appelle `bin(grid[y][x]).count('0')` à chaque appel (O(1) mais constant élevé).

### Solution

Maintenir un `dict` ou `array` de compteurs de murs, mis à jour incrémentalement :

```python
# Dans Kruskal.__init__ :
self._wall_count = {
    (x, y): maze._cell_wall_count(x, y)
    for x in range(self.width)
    for y in range(self.height)
}

# Après remove_wall(x, y, direction) :
self._wall_count[(x, y)] -= 1
nx, ny = self._get_direction_neighbor(x, y, direction)
self._wall_count[(nx, ny)] -= 1
```

---

## 7. Résumé des priorités

| Priorité | Amélioration | Complexité impl. | Gain estimé | Débloque 150×150 ? |
|----------|-------------|-----------------|-------------|---------------------|
| 🔴 1 | Union-Find (DSU) | Moyenne | ×10 à ×50 | ✅ Oui |
| 🔴 2 | Vrai Kruskal + liste de murs | Moyenne | ×5 | ✅ Oui |
| 🟠 3 | `_second_loop` incrémentale | Faible | ×3 à ×5 | ⚠️ Partiel |
| 🟡 4 | Éviter double copie (numpy) | Faible | ×2 | ❌ Non seul |
| 🟡 5 | Cache `_cell_wall_count` | Très faible | ×1.2 | ❌ Non |
| 🟢 6 | Parallélisation | Élevée | ×CPU | ✅ Oui (si ×4) |

**Recommandation** : implémenter **1 + 3** en priorité → suppression du BFS
complet + `_second_loop` incrémentale. Combinés, ils devraient ramener
151×151 sous la barre des 500 ms.
