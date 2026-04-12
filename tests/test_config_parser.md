# tests/test_config_parser.py

## Rôle
Tests unitaires du parser `ConfigFile.parse()`. Valide tous les cas de parsing et de validation du fichier de configuration.

## Ce qu'il fait
- Utilise `tmp_path` (pytest) pour créer des fichiers de config temporaires
- Cas valides : config minimale, commentaires ignorés, seed auto-généré, seed fourni, flag PLAYABLE
- Cas d'erreur : fichier absent, clé manquante, valeur invalide, ENTRY hors bornes, ENTRY == EXIT
- Couvre les conversions de types (int, tuple, bool)
- Vérifie les messages d'erreur pour les cas invalides

## Note globale : 9/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Moyenne | Ajouter des tests pour les valeurs limites : WIDTH=4 (minimum), coordonnées aux coins exacts |
| Moyenne | Tester les lignes malformées : pas de `=`, clé vide, valeur vide |
| Faible | Ajouter un test de performance : parsing d'un fichier avec beaucoup de commentaires/lignes vides |
| Faible | Paramétrer les cas d'erreur avec `@pytest.mark.parametrize` pour réduire la duplication |
