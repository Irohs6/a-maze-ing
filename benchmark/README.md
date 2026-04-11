# Benchmark — Kruskal (A-Maze-ing)

Dossier contenant les outils pour mesurer les performances de l'algorithme **Kruskal** implémenté dans `mazegen/kruksal.py`.

## Structure

```
benchmark/
├── run_benchmark.py          ← script principal
├── fiche_technique_kruskal.md ← fiche technique avec résultats du benchmark
├── README.md                 ← ce fichier
└── results/                  ← résultats générés automatiquement
    ├── benchmark_YYYYMMDD_HHMMSS.csv
    └── benchmark_YYYYMMDD_HHMMSS.md
```

## Prérequis

Être à la **racine du projet** et avoir activé le venv :

```bash
cd /chemin/vers/a-maze-ing
source .venv/bin/activate
```

## Lancer le benchmark

### Benchmark standard (10 seeds, tailles jusqu'à 101×101)

```bash
python3 benchmark/run_benchmark.py
```

### Options disponibles

```
--seeds N       Nombre de seeds par taille        (défaut : 10)
--max N         Taille maximale à tester (côté)   (défaut : 101)
--timeout N     Timeout par run en secondes        (défaut : 5.0)
--no-csv        Ne pas exporter les résultats CSV
```

### Exemples

```bash
# Benchmark rapide : 5 seeds, tailles jusqu'à 51×51
python3 benchmark/run_benchmark.py --seeds 5 --max 51

# Benchmark complet haute précision : 30 seeds
python3 benchmark/run_benchmark.py --seeds 30

# Tester uniquement les petites tailles (< 1 s)
python3 benchmark/run_benchmark.py --seeds 20 --max 71

# Limiter le timeout à 3s par run
python3 benchmark/run_benchmark.py --timeout 3.0
```

## Résultats produits

Chaque exécution crée deux fichiers dans `benchmark/results/` :

| Fichier | Contenu |
|---------|---------|
| `benchmark_TIMESTAMP.csv` | Un run par ligne — toutes les métriques brutes |
| `benchmark_TIMESTAMP.md`  | Tableau Markdown agrégé par taille |

### Colonnes du CSV

| Colonne | Description |
|---------|-------------|
| `width`, `height` | Dimensions du labyrinthe |
| `cells` | Nombre total de cellules (width × height) |
| `seed` | Seed utilisée |
| `success` | `True` si génération réussie |
| `valid` | `True` si le labyrinthe passe `MazeValidator.validate()` |
| `elapsed_s` | Temps de génération en secondes |
| `track_len` | Nombre total d'ouvertures de murs dans le track |
| `second_loop_calls` | Nombre d'appels à `_second_loop` |
| `global_attempts` | Numéro de la tentative globale qui a réussi |
| `walls_opened` | Nombre de murs effectivement ouverts dans la grille finale |
| `error` | Message d'erreur si `success=False` |

## Résultats de référence (11/04/2026)

| Taille | Taux succès | Temps moy | Temps max | Loops moy |
|--------|-------------|-----------|-----------|-----------|
| ≤ 51×51 | 100 % | < 80 ms | < 270 ms | < 20 |
| 71×71  | 100 % | 660 ms  | 1 568 ms | 82 |
| 101×101 | 100 % | 4 000 ms | 10 385 ms | 245 |

> ⚠️ Au-delà de **71×71**, les temps et la variance deviennent imprévisibles.
> Au-delà de **101×101**, des `ValueError` peuvent survenir (divergence).

Voir [fiche_technique_kruskal.md](fiche_technique_kruskal.md) pour l'analyse complète.
