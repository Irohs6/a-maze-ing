from pydantic import (BaseModel, ConfigDict, Field,
                      model_validator, field_validator)
from typing import Annotated, Any, ClassVar

from time import time_ns

NonNegativeInt = Annotated[int, Field(ge=0)]


class ConfigFile(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    REQUIRED_KEYS: ClassVar[list[str]] = [
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT",
    ]
    OPTIONAL_KEYS: ClassVar[list[str]] = ["SEED", "PLAYABLE"]

    WIDTH: int = Field(ge=4)
    HEIGHT: int = Field(ge=4)
    ENTRY: tuple[NonNegativeInt, NonNegativeInt]
    EXIT: tuple[NonNegativeInt, NonNegativeInt]
    OUTPUT_FILE: str
    PERFECT: bool
    SEED: int | None = None
    PLAYABLE: bool = False

    ALGORITHM: str = Field(..., pattern="^(?i)(backtracker|kruksal)$")

    @field_validator("ALGORITHM")
    @classmethod
    def normalize_algorithm(cls, v):
        return v.lower()

    @model_validator(mode="after")
    def validate_entry_exit_bounds(self) -> "ConfigFile":
        """Ensure ENTRY and EXIT positions are within the maze dimensions."""
        for key in ["ENTRY", "EXIT"]:
            x, y = getattr(self, key)
            if not (0 <= x < self.WIDTH) or not (0 <= y < self.HEIGHT):
                raise ValueError(
                    f"{key} position {getattr(self, key)} is out of bounds "
                    f"for maze dimensions ({self.WIDTH}x{self.HEIGHT})"
                )
        return self

    @model_validator(mode="after")
    def validate_entry_exit_different(self) -> "ConfigFile":
        """Check that ENTRY and EXIT positions are not the same."""
        if self.ENTRY == self.EXIT:
            raise ValueError("ENTRY and EXIT positions cannot be the same")
        return self

    # ------------------------------------------------------------------
    # Public factory
    # ------------------------------------------------------------------

    @classmethod
    def parse(cls, config_file_path: str) -> "ConfigFile":
        """Parse and validate a config file, return a ConfigFile instance.

        Raises:
            FileNotFoundError: If the config file does not exist.
            KeyError: If a required key is missing.
            ValueError: If the file contains invalid syntax or values.
        """
        raw: dict[str, Any] = {}
        cls._read_file(config_file_path, raw)
        cls._validate_required_keys(raw)
        cls._parse_types(raw)
        cls._parse_optionals(raw)
        return cls(**raw)

    # ------------------------------------------------------------------
    # Private static parsing steps
    # ------------------------------------------------------------------

    @staticmethod
    def _read_file(config_file_path: str, config: dict[str, Any]) -> None:
        """Read KEY=VALUE pairs from the file into *config*."""
        try:
            with open(config_file_path, "r") as file:
                for line in file:
                    if line.startswith("#") or not line.strip():
                        continue
                    ConfigFile._parse_line(line, config)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file '{config_file_path}' not found."
            )

    @staticmethod
    def _parse_line(line: str, config: dict[str, Any]) -> None:
        """Parse a single line of the config file and update *config*."""
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
        config[key] = value

    @staticmethod
    def _validate_required_keys(config: dict[str, Any]) -> None:
        """Check that all required keys are present in the config."""
        for key in ConfigFile.REQUIRED_KEYS:
            if key not in config:
                raise KeyError(
                    f"'{key}' has not properly been defined in "
                    "the config.txt file"
                )

    @staticmethod
    def _parse_types(config: dict[str, Any]) -> None:
        """Convert string values to their proper Python types."""
        try:
            for key in ["WIDTH", "HEIGHT"]:
                config[key] = int(config[key])
            for key in ["ENTRY", "EXIT"]:
                config[key] = tuple(
                    int(v) for v in config[key].split(",")
                )
            config["PERFECT"] = config["PERFECT"].strip().lower() == "true"
        except ValueError as error:
            raise ValueError(error)

    @staticmethod
    def _parse_optionals(config: dict[str, Any]) -> None:
        try:
            for key in ConfigFile.OPTIONAL_KEYS:
                if key == "SEED":
                    if key in config:
                        config[key] = int(config[key])
                    else:
                        config[key] = time_ns()
                else:
                    if key not in config:
                        config[key] = False
                    else:
                        config[key] = config[key].strip().lower() == "true"
        except ValueError as error:
            raise ValueError(error)
