from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Annotated

NonNegativeInt = Annotated[int, Field(ge=0)]


class ConfigFile(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    WIDTH: int = Field(ge=4)
    HEIGHT: int = Field(ge=4)
    ENTRY: tuple[NonNegativeInt, NonNegativeInt]
    EXIT: tuple[NonNegativeInt, NonNegativeInt]
    OUTPUT_FILE: str
    PERFECT: bool
    SEED: int | None = None
    PLAYABLE: bool = False

    @model_validator(mode="after")
    def validate_entry_exit(cls, config: "ConfigFile") -> "ConfigFile":
        """Ensure ENTRY and EXIT positions are within the maze dimensions."""
        for key in ["ENTRY", "EXIT"]:
            x, y = getattr(config, key)
            if not (0 <= x < config.WIDTH) or not (0 <= y < config.HEIGHT):
                raise ValueError(
                    f"{key} position {getattr(config, key)} is out of bounds "
                    f"for maze dimensions ({config.WIDTH}x{config.HEIGHT})"
                )
        return config

    @model_validator(mode="after")
    def entry_and_exit_are_different(cls, config: "ConfigFile") -> "ConfigFile":
        """Check that ENTRY and EXIT positions are not the same."""
        if config.ENTRY == config.EXIT:
            raise ValueError("ENTRY and EXIT positions cannot be the same")
        return config
