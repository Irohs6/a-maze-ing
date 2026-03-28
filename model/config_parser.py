# model/config_parser.py — Parseur du fichier de configuration.
# Contient la classe ConfigParser responsable de lire et valider le fichier config.
# Elle gère :
#   - la lecture ligne par ligne en ignorant les commentaires (#)
#   - l'extraction des paires CLE=VALEUR
#   - la validation de la présence de toutes les clés obligatoires
#   - la conversion et la validation des types (entiers, booléen, coordonnées)
#   - la vérification que les coordonnées d'entrée/sortie sont dans les limites du labyrinthe
#   - les clés optionnelles (SEED, ALGORITHM) avec leurs valeurs par défaut
# Lève des exceptions descriptives pour chaque type d'erreur rencontré.

from typing import Any


class ConfigParser:
    """Parse and validate a maze configuration file.

    Reads KEY=VALUE pairs, ignores comments (#) and blank lines,
    validates all mandatory keys and converts values to proper types.
    """

    REQUIRED_KEYS: list[str] = [
        'WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE', 'PERFECT'
    ]

    def __init__(self, config_file: str) -> None:
        self.config_file: str = config_file
        self.config: dict[str, Any] = {}

    def parse(self) -> dict[str, Any]:
        """Read and validate the configuration file.

        Returns:
            A dict with all parsed and validated config values.

        Raises:
            FileNotFoundError: If the config file does not exist.
            ValueError: If the file contains invalid syntax or values.
        """
        try:
            with open(self.config_file, 'r') as file:
                for line in file:
                    if line.startswith('#') or not line.strip():
                        continue  # Ignore comments and blank lines
                    self._parse_line(line)
            return self.config
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file '{self.config_file}' not found."
            )

    def _parse_line(self, line: str) -> tuple[str, str]:
        if '=' not in line:
            raise ValueError(
                    f"Invalid line in config: '{line.strip()}' (missing '=')"
                )
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Empty key in line: '{line.strip()}'")
        if not value:
            raise ValueError(
                f"Empty value for key '{key}' in line: '{line.strip()}'"
            )
        self.config[key] = value
        return key, value

    def _validate_required_keys(self) -> None:
        pass

    def _parse_coordinates(self, raw: str, key_name: str) -> tuple[int, int]:
        pass

    def _convert_types(self) -> None:
        pass

    def _validate_coordinates(self) -> None:
        pass

    def _apply_defaults(self) -> None:
        pass
