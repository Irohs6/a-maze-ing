# model/config_file.py

## Rôle
Parser et validateur du fichier de configuration `config.txt`. Utilise **Pydantic v2** pour garantir la cohérence des types et des contraintes métier.

## Ce qu'il fait
- Lit le fichier ligne par ligne au format `KEY=VALUE` (ignore les commentaires `#` et lignes vides)
- Convertit les valeurs brutes (strings) vers leurs types Python : `int`, `tuple[int,int]`, `bool`
- Valide les clés requises (`WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`, `OUTPUT_FILE`, `PERFECT`)
- Assigne un SEED aléatoire (nanoseconde) si absent
- Vérifie via des `model_validator` Pydantic que :
  - `ENTRY` et `EXIT` sont dans les bornes du labyrinthe
  - `ENTRY ≠ EXIT`
- Retourne une instance `ConfigFile` immuable et validée

## Note globale : 9/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Moyenne | Ajouter la validation que `OUTPUT_FILE` n'est pas vide et que le chemin parent est accessible en écriture |
| Moyenne | Le parsing `ENTRY`/`EXIT` suppose exactement deux entiers séparés par une virgule — ajouter un message d'erreur explicite si le format est invalide |
| Faible | Exposer une méthode `to_dict()` ou `__repr__` plus lisible pour le débogage |
| Faible | Supporter un format JSON ou YAML en plus du format `KEY=VALUE` |
