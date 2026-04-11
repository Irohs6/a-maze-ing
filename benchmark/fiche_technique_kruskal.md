# Fiche Technique — Algorithme Kruskal (A-Maze-ing)

> Version : A-Maze-ing — `mazegen/kruksal.py`
> Benchmark réalisé le 11/04/2026 — 15 seeds × 14 tailles, 210 runs

---

## 1. Description générale

L'algorithme implémenté est une **version randomisée de l'algorithme de Kruskal**
adapté à la génération de labyrinthes **imparfaits** (non-parfaits) contenant
obligatoirement le motif picturel « 42 » figé au centre.

Un labyrinthe **imparfait** permet plusieurs chemins entre deux cellules
(contrairement au backtracker qui garantit un chemin unique).

---

## 2. Principe de fonctionnement

### Phase 1 — Premier passage aléatoire

Pour chaque cellule non-visitée (hors motif 42 et hors bordures), on choisit
aléatoirement **un mur abattable** et on l'ouvre.
Ce passage produit un labyrinthe partiellement connecté mais souvent invalide.

### Phase 2 — Correction itérative (`_second_loop`)

On identifie toutes les cellules intérieures ayant encore **plus de 2 murs**
(trop isolées). Pour chacune, on abat des murs supplémentaires jusqu'à ce
qu'elle ait ≤ 2 murs ou qu'il n'y ait plus de mur abattable.

### Phase 3 — Validation

Un `MazeValidator` vérifie :
- **Connectivité** : toutes les cellules non-isolées sont accessibles depuis (0,0)
- **Absence de zones 3×3 ouvertes** (couloirs trop larges interdits)

Si le labyrinthe est invalide, on **repart de la phase 2** (jusqu'à 50 fois).
Si après 50 itérations il est encore invalide, on lance une **nouvelle tentative
globale** (jusqu'à 30 tentatives).

---

## 3. Paramètres internes

| Paramètre | Valeur | Rôle |
|-----------|--------|------|
| `_MAX_GLOBAL_ATTEMPTS` | 30 | Nombre maximal de tentatives complètes avant abandon |
| Inner loop limit | 50 | Nombre maximal d'appels à `_second_loop` par tentative |
| Critère de mur abattable | ≤ 2 voisins 42 + non-bordure + non-mur 42 | Contraintes de sécurité du motif |
| Motif 42 | 18 cellules isolées (PATTERN_42 5×7) | Placé au centre, non traversable |

---

## 4. Résultats du benchmark

### 4.1 Tableau complet (15 seeds par taille)

| Taille   | Cellules | Taux succès | Temps moy (s) | Temps min (s) | Temps max (s) | StdDev (s) | Track moy | Loops moy |
|----------|----------|-------------|---------------|---------------|---------------|-----------|-----------|-----------|
| 5×5      | 25       | 100 %       | 0.0005        | 0.0001        | 0.0022        | 0.0008    | 26        | 20.4      |
| 7×7      | 49       | 100 %       | 0.0003        | 0.0002        | 0.0008        | 0.0002    | 56        | 1.6       |
| 9×9      | 81       | 100 %       | 0.0019        | 0.0003        | 0.0168        | 0.0044    | 94        | 14.5      |
| 11×9     | 99       | 100 %       | 0.0030        | 0.0003        | 0.0111        | 0.0034    | 86        | 35.6      |
| 11×11    | 121      | 100 %       | 0.0030        | 0.0004        | 0.0133        | 0.0041    | 114       | 21.3      |
| 15×15    | 225      | 100 %       | 0.0017        | 0.0008        | 0.0103        | 0.0024    | 241       | 5.4       |
| 21×21    | 441      | 100 %       | 0.0121        | 0.0016        | 0.0864        | 0.0230    | 515       | 19.1      |
| 31×31    | 961      | 100 %       | 0.0273        | 0.0037        | 0.2381        | 0.0599    | 1 181     | 21.1      |
| 41×41    | 1 681    | 100 %       | 0.0420        | 0.0066        | 0.1508        | 0.0473    | 2 101     | 15.7      |
| 51×51    | 2 601    | 100 %       | 0.0754        | 0.0114        | 0.2675        | 0.0841    | 3 285     | 17.5      |
| 61×61    | 3 721    | 100 %       | 0.178         | 0.018         | 0.632         | 0.193     | 4 732     | 30.9      |
| 71×71    | 5 041    | 100 %       | 0.660         | 0.021         | 1.568         | 0.532     | 6 435     | 81.9      |
| 81×81    | 6 561    | 100 %       | 0.669         | 0.060         | 2.059         | 0.620     | 8 409     | 63.1      |
| 101×101  | 10 201   | 100 %       | 4.006         | 0.325         | 10.385        | 2.811     | 13 132    | 244.9     |

### 4.2 Observations clés

- **Taux de succès : 100 %** sur toutes les tailles (0 à 101×101) avec 30 tentatives max.
- **La variance explose avec la taille** : à 101×101 le StdDev atteint 2.81s pour
  une moyenne de 4.0s — le pire cas observé est **10.4s**.
- **Le nombre de `_second_loop`** est le facteur dominant du temps de génération.
  À 101×101, on observe en moyenne **245 appels** contre 1.6 pour 7×7.
- La taille **11×9** (minimale pour le motif 42) est légèrement plus difficile que
  11×11 : 35.6 loops en moyenne vs 21.3, car les marges sont plus contraintes.

---

## 5. Complexité empirique

### Temps de génération vs surface

D'après les mesures, la relation entre le temps moyen et la surface N = w × h
est **super-linéaire**, entre O(N) et O(N²) selon la configuration :

| Rapport de surface | Rapport de temps moyen |
|--------------------|----------------------|
| 5×5 → 15×15 (×9)  | 0.0005s → 0.0017s (×3.4) |
| 15×15 → 51×51 (×11.6) | 0.0017s → 0.075s (×44) |
| 51×51 → 101×101 (×3.9) | 0.075s → 4.0s (×53) |

La complexité effective est approximativement **O(N · L)** où :
- N = nombre de cellules (w × h)
- L = nombre moyen d'itérations de `_second_loop` (variable, croît avec N)

---

## 6. Limites et zone d'utilisation recommandée

| Zone | Taille | Temps moy | Recommandation |
|------|--------|-----------|----------------|
| ✅ Idéale | ≤ 51×51 | < 80 ms | Interactif, animations, jeu |
| ⚠️ Acceptable | 61×61 – 71×71 | 180 ms – 660 ms | Usage ponctuel acceptable |
| 🔴 Lente | 81×81 – 101×101 | 670 ms – 4 s | Déconseillé interactif, pire cas > 10s |
| ❌ Critique | > 101×101 | > 10 s | Non recommandé — divergence observée à 151×151 |

**Limite pratique recommandée : ≤ 71×71**
(temps moyen < 1s, pire cas < 2s)

---

## 7. Comparaison avec Backtracker

| Critère | Kruskal (imparfait) | Backtracker (parfait) |
|---------|--------------------|-----------------------|
| Type de labyrinthe | Imparfait (multi-chemins) | Parfait (chemin unique) |
| Temps 51×51 | ~75 ms | < 5 ms |
| Temps 101×101 | ~4 s | < 50 ms |
| Variance | Très haute | Très basse |
| Taux succès | 100 % (≤ 30 tentatives) | 100 % (déterministe) |
| Motif 42 | Oui | Oui |
| Validité | Via `MazeValidator` | Via `MazeValidator` |

Le Backtracker est **~80× plus rapide** à 101×101 car il est déterministe —
pas de boucle de correction.

---

## 8. Points d'amélioration identifiés

1. **`_second_loop` est O(N²)** dans le pire cas — parcourt toutes les cellules
   intérieures à chaque itération.
2. **Pas d'union-find** : l'implémentation n'utilise pas la structure de données
   Kruskal classique (Union-Find / DSU), ce qui pénalise la vérification de
   connectivité  (BFS complet à chaque itération).
3. **`copy.copy` + `grid[:]`** : la copie peu profonde de la grille est correcte
   mais implique une réallocation O(N) à chaque tentative.
4. **Divergence sur grands labyrinthes** : à 151×151+, l'algorithme peut ne pas
   converger dans 30 tentatives × 50 loops, causant une `ValueError`.

---

## 9. Diagramme de flux simplifié

```
Maze(w, h) + Kruskal()
      │
      ▼
[Tentative globale #1..30]
      │
      ├─ Phase 1 : abattre 1 mur aléatoire par cellule non-42
      │
      ├─ [Boucle de correction #1..50]
      │     ├─ _second_loop() : abattre murs sur cellules sur-isolées
      │     └─ MazeValidator : connectivité OK + pas de zone 3×3 ?
      │              ├─ OUI → ✅ Succès, retourner track
      │              └─ NON → recommencer _second_loop
      │
      └─ après 50 loops sans succès → nouvelle tentative globale

Après 30 tentatives globales sans succès → raise ValueError
```
