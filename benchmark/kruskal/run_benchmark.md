# benchmark/run_benchmark.py

## Rôle
Script de benchmark complet pour mesurer les performances de l'algorithme Kruskal (et Backtracker) sur différentes tailles de labyrinthes.

## Ce qu'il fait
- Teste une liste de tailles prédéfinies (de 5×5 à 101×101) avec N seeds chacune
- Mesure pour chaque taille : temps moyen / min / max de génération, taux de succès, nombre de cellules/murs ouverts, itérations de `_second_loop`
- Implémente un `InstrumentedKruskal` qui étend `Kruksal` pour compter les itérations internes
- Applique un **timeout** par tentative (défaut : 5 s)
- Exporte les résultats dans `benchmark/results/` en **CSV** et **Markdown**
- Supporte des arguments CLI : `--seeds`, `--no-csv`, `--max`

## Note globale : 8.5/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Moyenne | Ajouter le benchmark pour `Backtracker` pour permettre une comparaison directe des deux algorithmes |
| Moyenne | Le timeout est implémenté via `time.time()` dans une boucle — sur les très grandes grilles, le check peut arriver trop tard. Utiliser `signal.alarm` ou un thread pour un timeout dur |
| Faible | Ajouter un graphique automatique (matplotlib) des résultats temps/taille |
| Faible | Permettre de spécifier une liste de tailles custom en argument CLI |
