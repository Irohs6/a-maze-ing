# utils/logger.py

## Rôle
Module utilitaire destiné à centraliser la journalisation du projet.

## Ce qu'il fait
- Fichier actuellement **vide** — aucune implémentation présente

## Note globale : 0/10 *(non implémenté)*

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | Implémenter un logger basé sur le module standard `logging` de Python |
| Haute | Configurer les niveaux (DEBUG, INFO, WARNING, ERROR) et le format de sortie |
| Haute | Permettre d'activer/désactiver les logs via une variable d'environnement ou un flag CLI |
| Moyenne | Ajouter un handler fichier pour sauvegarder les logs en cas de débogage |
| Faible | Exposer un singleton `logger = get_logger(__name__)` importable dans tous les modules |
