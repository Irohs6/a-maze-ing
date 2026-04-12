# tests/test_config_parser.py

## Rôle
Tests unitaires du parser `ConfigFile.parse()`. Valide tous les cas de parsing et de validation du fichier de configuration.

## Ce qu'il fait
- Utilise `tmp_path` (pytest) pour créer des fichiers de config temporaires
- Cas valides : config minimale, commentaires ignorés, seed auto-généré, seed fourni, flag PLAYABLE, PERFECT=True/False
- Cas d'erreur : fichier absent, clé manquante (paramétrisé sur toutes les clés requises), valeur invalide, ENTRY hors bornes, ENTRY == EXIT
- Lignes malformées : pas de `=`, clé vide, valeur vide
- Conversions de types : int (WIDTH/HEIGHT), tuple (ENTRY/EXIT), bool (PERFECT/PLAYABLE)
- Vérifie les messages d'erreur (`match=`) pour les cas invalides

## Note globale : 9.5/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Faible | Ajouter des tests pour les valeurs limites exactes : WIDTH/HEIGHT=4 (minimum accepté), coordonnées aux coins exacts |
| Faible | Ajouter un test de performance : parsing d'un fichier avec beaucoup de commentaires/lignes vides |
| Faible | Tester le comportement avec des espaces autour du `=` ou des valeurs avec espaces internes |
