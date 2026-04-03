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
# import random


class ConfigParser:
    """Parse and validate a maze configuration file.

    Reads KEY=VALUE pairs, ignores comments (#) and blank lines,
    validates all mandatory keys and converts values to proper types.
    """

    REQUIRED_KEYS: list[str] = [
        'WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE', 'PERFECT'
    ]
    OPTIONAL_KEYS: list[str] = [
        'SEED', 'ALGORITHM', 'VIEW'
    ]

    def __init__(self, config_file: str) -> None:
        self.config_file: str = config_file
        self.__config: dict[str, Any] = {}

    def parse(self) -> None:
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
            # Ajout des valeurs par défaut pour les clés optionnelles manquantes
            for key in self.OPTIONAL_KEYS:
                if key not in self.__config:
                    if key == 'VIEW':
                        self.__config[key] = 'terminal'
                    elif key == 'ALGORITHM':
                        self.__config[key] = 'backtracker'
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file '{self.config_file}' not found."
            )

    def _parse_line(self, line: str) -> None:
        if '=' not in line:
            raise ValueError(
                f"Invalid line in config: '{line.strip()}' (missing '=')"
            )
        key, value = line.split('=', 1)
        key = key.strip().upper()
        value = value.strip()
        if not key:
            raise ValueError(f"Empty key in line: '{line.strip()}'")
        if not value:
            raise ValueError(
                f"Empty value for key '{key}' in line: '{line.strip()}'"
            )
        # Normalisation et validation pour VIEW et ALGORITHM
        if key == 'VIEW':
            value = value.lower()
            if value not in ('terminal', 'curse'):
                raise ValueError(f"VIEW must be 'terminal' or 'curse', got '{value}'")
        if key == 'ALGORITHM':
            value = value.lower()
            if value not in ('backtracker', 'kruskal'):
                raise ValueError(f"ALGORITHM must be 'backtracker' ou 'kruskal', got '{value}'")
        self.__config[key] = value

    def _validate_required_keys(self) -> None:
        for key in self.REQUIRED_KEYS:
            if key in self.__config.keys():
                continue
            else:
                raise KeyError(f"'{key}' has not properly been defined in "
                               "the config.txt file")

    def _parse_coordinates(self) -> None:
        try:
            for key in ['WIDTH', 'HEIGHT']:
                self.__config[key] = int(self.__config[key])
                self._validate_coordinates(key)
            for key in ['ENTRY', 'EXIT']:
                self.__config[key] = tuple(int(value) for value in
                                           self.__config[key].split(','))
                self._validate_coordinates(key)
            self.__config['PERFECT'] = (
                self.__config['PERFECT'].lower() == 'true'
            )
            if 'SEED' in self.__config:
                self.__config['SEED'] = int(self.__config['SEED'])
        except ValueError as error:
            raise ValueError(error)

    def _validate_coordinates(self, key: str) -> None:
        if key in ['WIDTH', 'HEIGHT']:
            if self.__config[key] <= 0:
                raise ValueError(f"{key} value is invalid ("
                                 f"{self.__config[key]})")
        else:
            if (len(self.__config[key]) != 2 or self.__config[key][0] < 0
               or self.__config[key][0] > self.__config['WIDTH']
               or self.__config[key][1] < 0 or
               self.__config[key][1] > self.__config['HEIGHT']):
                raise ValueError(f"'{key}' needs 2 positive integers that "
                                 "fits within 'WIDTH' and 'HEIGTH' and "
                                 "separated by ','")

    # def _parse_optionals(self) -> None:
    #     for key in self.OPTIONAL_KEYS:
    #         if not key in self.__config.keys():

    def _get_config(self) -> dict[str, Any]:
        return self.__config
