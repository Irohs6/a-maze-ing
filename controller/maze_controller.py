# controller/maze_controller.py — Orchestrateur central du programme.
# Contient la classe MazeController qui fait le lien entre le modèle et la vue.
# Responsabilités :
#   1. Recevoir le chemin du fichier de configuration depuis a_maze_ing.py
#   2. Instancier ConfigParser et lire la configuration
#   3. Instancier le générateur de labyrinthe (MazeGenerator depuis mazegen)
#      et déclencher la génération avec les paramètres de la config
#   4. Instancier PathFinder et calculer le chemin solution
#   5. Écrire le fichier de sortie au format hexadécimal requis
#   6. Instancier la vue appropriée (TerminalView ou MlxView) et lancer l'affichage
#   7. Gérer les actions utilisateur transmises par la vue (régénérer, afficher solution, etc.)
#   8. Propager les erreurs sous forme de messages clairs sans planter le programme.

from typing import Any
from model.config_parser import ConfigParser
from model.maze import Maze
from view.terminal_view import TerminalView


class MazeController:
    """Central orchestrator: loads config, generates maze, finds path, renders view."""

    def __init__(self, config_file: str) -> None:
        self._config_file: str = config_file
        self._config: dict[str, Any] = {}
        self._maze: Maze | None = None

    def _load_config(self) -> None:
        """Parse and validate the configuration file.

        Raises:
            FileNotFoundError: If the config file does not exist.
            ValueError: If a value is invalid or a key is missing.
            KeyError: If a required key is absent.
        """
        parser = ConfigParser(self._config_file)
        parser.parse()
        parser._validate_required_keys()
        parser._parse_coordinates()
        self._config = parser._get_config()

    def _build_maze(self) -> None:
        """Instantiate the Maze with dimensions from the config."""
        self._maze = Maze(self._config['WIDTH'], self._config['HEIGHT'])

    def run(self) -> None:
        """Execute the full maze pipeline."""
        self._load_config()
        self._build_maze()
        view = TerminalView(self._maze)
        view.print_unicode()
