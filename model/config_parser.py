# model/config_parser.py — Parseur du fichier de configuration.
# Contient la classe ConfigParser responsable
# de lire et valider le fichier config.
# Elle gère :
#   - la lecture ligne par ligne en ignorant les commentaires (#)
#   - l'extraction des paires CLE=VALEUR
#   - la validation de la présence de toutes les clés obligatoires
#   - la conversion et la validation des types (entiers, booléen, coordonnées)
#   - la vérification que les coordonnées d'entrée/sortie
#  sont dans les limites du labyrinthe
#   - les clés optionnelles (SEED, ALGORITHM) avec leurs valeurs par défaut
# Lève des exceptions descriptives pour chaque type d'erreur rencontré.
from typing import Any
from model.config_file import ConfigFile
import time


class ConfigParser:
    """Parse and validate a maze configuration file.

    Reads KEY=VALUE pairs, ignores comments (#) and blank lines,
    validates all mandatory keys and converts values to proper types.

    Example usage:
        config = ConfigParser('config.txt').parse()
    """

    REQUIRED_KEYS: list[str] = [
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    ]
    OPTIONAL_KEYS: list[str] = ["SEED", "PLAYABLE"]

    def __init__(self, config_file: str) -> None:
        self.config_file: str = config_file
        self.config_file_model: ConfigFile | None = None
        self.__config: dict[str, Any] = {}

    def parse(self) -> ConfigFile:
        """Parse and validate the configuration file.

        Reads the file, validates required keys, converts types, and
        applies defaults for optional keys. Returns a ConfigFile instance.

        Raises:
            FileNotFoundError: If the config file does not exist.
            KeyError: If a required key is missing.
            ValueError: If the file contains invalid syntax or values.
        """
        self._read_file()
        self._validate_required_keys()
        self._parse_types()
        self._parse_optionals()
        self.config_file_model = ConfigFile(**self.__config)
        return self.config_file_model

    # ------------------------------------------------------------------
    # Private steps
    # ------------------------------------------------------------------

    def _read_file(self) -> None:
        """Read KEY=VALUE pairs from the config file into __config."""
        try:
            with open(self.config_file, "r") as file:
                for line in file:
                    if line.startswith("#") or not line.strip():
                        continue
                    self._parse_line(line)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file '{self.config_file}' not found."
            )

    def _parse_line(self, line: str) -> None:
        if "=" not in line:
            raise ValueError(
                f"Invalid line in config: '{line.strip()}' (missing '=')"
            )
        key, value = line.split("=", 1)
        key = key.strip().upper()
        value = value.strip()
        if not key:
            raise ValueError(f"Empty key in line: '{line.strip()}'")
        if not value:
            raise ValueError(
                f"Empty value for key '{key}' in line: '{line.strip()}'"
            )
        if key == "VIEW":
            value = value.lower()
            if value not in ("terminal", "curse"):
                raise ValueError(
                    "VIEW must be 'terminal' or 'curse'," f" got '{value}'"
                )
        if key == "ALGORITHM":
            value = value.lower()
            if value not in (
                "backtracker",
                "recursive_backtracker",
                "kruksal",
            ):
                raise ValueError(
                    "ALGORITHM must be 'backtracker' or 'kruksal',"
                    f" got '{value}'"
                )
        self.__config[key] = value

    def _validate_required_keys(self) -> None:
        for key in self.REQUIRED_KEYS:
            if key not in self.__config:
                raise KeyError(
                    f"'{key}' has not properly been defined in "
                    "the config.txt file"
                )

    def _parse_types(self) -> None:
        """Convert string values to their proper Python types."""
        try:
            for key in ["WIDTH", "HEIGHT"]:
                self.__config[key] = int(self.__config[key])
                self._validate_dimensions(key)
            for key in ["ENTRY", "EXIT"]:
                self.__config[key] = tuple(
                    int(v) for v in self.__config[key].split(",")
                )
                self._validate_position(key)
            self.__config["PERFECT"] = (
                self.__config["PERFECT"].strip().lower() == "true"
            )
        except ValueError as error:
            raise ValueError(error)

    def _validate_dimensions(self, key: str) -> None:
        if self.__config[key] <= 0:
            raise ValueError(f"{key} value is invalid ({self.__config[key]})")

    def _validate_position(self, key: str) -> None:
        coords = self.__config[key]
        if (
            len(coords) != 2
            or coords[0] < 0
            or coords[0] >= self.__config["WIDTH"]
            or coords[1] < 0
            or coords[1] >= self.__config["HEIGHT"]
        ):
            raise ValueError(
                f"'{key}' needs 2 positive integers that "
                "fit within 'WIDTH' and 'HEIGHT', separated by ','"
            )

    def _parse_optionals(self) -> None:
        try:
            for key in self.OPTIONAL_KEYS:
                if key == "SEED":
                    if key in self.__config:
                        self.__config[key] = int(self.__config[key])
                    else:
                        seed = time.time_ns()
                        self.__config[key] = seed
                else:
                    if key not in self.__config:
                        self.__config[key] = False
                    else:
                        self.__config[key] = (
                            self.__config[key].strip().lower() == "true"
                        )
        except ValueError as error:
            raise ValueError(error)
