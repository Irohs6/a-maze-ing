# view/menu.py

## Rôle
Interface de menu interactif en terminal. Permet à l'utilisateur de naviguer entre les options, modifier les paramètres du labyrinthe et lancer la génération.

## Ce qu'il fait
- Affiche un menu vertical naviguable (flèches haut/bas + Entrée) avec 3 options : Générer, Paramètres, Quitter
- Mode "Paramètres" : demande interactivement WIDTH, HEIGHT, ENTRY, EXIT, PERFECT, SEED via `click.prompt`
- Valide les nouvelles valeurs avec Pydantic (`ConfigFile`) avant application — affiche les erreurs sans crasher
- Rappelle `MazeController._create_gen()` / `_create_view()` / `_create_pathfinder()` lors d'une nouvelle génération
- Gère les touches spéciales (flèches, Entrée, Ctrl+C) en mode raw terminal

## Note globale : 7.5/10

## Améliorations possibles
| Priorité | Amélioration |
|----------|-------------|
| Haute | Le mode raw `tty.setraw` n'est pas restauré proprement en cas d'exception dans `_run()` — risque de terminal cassé |
| Haute | Le menu est limité à 3 options hardcodées — rendre la liste d'options configurable/extensible |
| Moyenne | Mélange de responsabilités : lecture d'input + affichage + logique de navigation dans la même classe |
| Moyenne | La saisie des paramètres un à un est longue pour l'utilisateur — proposer un formulaire groupé ou un fichier config rechargeable |
| Faible | Ajouter une confirmation « Êtes-vous sûr ? » avant de quitter |
