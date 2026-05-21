# tests/test_config_parser.py — Unit tests for ConfigFile.parse().
import sys
try:
    import pytest
except ImportError:
    print("\033c", end="")
    print(
        "Pytest not found, try starting the program with 'make run' command."
    )
    sys.exit(7)
from pathlib import Path
from mazegen.model.config_file import ConfigFile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_config(tmp_path: Path, content: str) -> str:
    """Write *content* to a temporary config file and return its path."""
    f = tmp_path / "config.txt"
    f.write_text(content)
    return str(f)


VALID = """\
WIDTH=10
HEIGHT=5
ENTRY=0,0
EXIT=9,4
OUTPUT_FILE=maze_output.txt
PERFECT=True
ALGORITHM=backtracker
"""


# ---------------------------------------------------------------------------
# Valid configurations
# ---------------------------------------------------------------------------

def test_valid_config(tmp_path: Path) -> None:
    """A fully valid config file must parse without error."""
    config = ConfigFile.parse(make_config(tmp_path, VALID))
    assert config.WIDTH == 10
    assert config.HEIGHT == 5
    assert config.ENTRY == (0, 0)
    assert config.EXIT == (9, 4)
    assert config.OUTPUT_FILE == "maze_output.txt"
    assert config.PERFECT is True


def test_comments_and_blank_lines_ignored(tmp_path: Path) -> None:
    """Comments and blank lines must be silently ignored."""
    content = """\
# commentaire
WIDTH=10

# autre commentaire
HEIGHT=5

ENTRY=0,0
EXIT=9,4
OUTPUT_FILE=maze.txt
PERFECT=True
ALGORITHM=backtracker
"""
    config = ConfigFile.parse(make_config(tmp_path, content))
    assert config.WIDTH == 10
    assert config.HEIGHT == 5


def test_optional_seed_generated_if_absent(tmp_path: Path) -> None:
    """When SEED is absent, a non-None integer seed must be generated."""
    config = ConfigFile.parse(make_config(tmp_path, VALID))
    assert config.SEED is not None
    assert isinstance(config.SEED, int)


def test_optional_seed_used_if_present(tmp_path: Path) -> None:
    """When SEED is provided, the exact value must be used."""
    content = VALID + "SEED=42\n"
    config = ConfigFile.parse(make_config(tmp_path, content))
    assert config.SEED == 42


def test_perfect_false(tmp_path: Path) -> None:
    """PERFECT=False must be parsed as a False boolean."""
    content = VALID.replace("PERFECT=True", "PERFECT=False")
    config = ConfigFile.parse(make_config(tmp_path, content))
    assert config.PERFECT is False


# ---------------------------------------------------------------------------
# File not found
# ---------------------------------------------------------------------------

def test_file_not_found() -> None:
    """A non-existent path must raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="not found"):
        ConfigFile.parse("non_existent_config.txt")


# ---------------------------------------------------------------------------
# Missing required keys
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("missing_key", [
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
])
def test_missing_required_key(tmp_path: Path, missing_key: str) -> None:
    """Each required key, when removed, must raise KeyError."""
    lines = [line for line in VALID.splitlines()
             if not line.startswith(missing_key)]
    with pytest.raises(KeyError, match="has not properly been defined"):
        ConfigFile.parse(make_config(tmp_path, "\n".join(lines)))


# ---------------------------------------------------------------------------
# Syntaxe invalide
# ---------------------------------------------------------------------------

def test_line_missing_equals(tmp_path: Path) -> None:
    """A line without '=' must raise ValueError."""
    with pytest.raises(ValueError, match="missing '='"):
        ConfigFile.parse(make_config(tmp_path, "WIDTH=10\nINVALID_LINE\n"))


def test_empty_key(tmp_path: Path) -> None:
    """A line with an empty key must raise ValueError."""
    with pytest.raises(ValueError, match="Empty key"):
        ConfigFile.parse(make_config(tmp_path, "=some_value\n"))


def test_empty_value(tmp_path: Path) -> None:
    """A key with an empty value must raise ValueError."""
    with pytest.raises(ValueError, match="Empty value"):
        ConfigFile.parse(make_config(tmp_path, "WIDTH=\n"))


# ---------------------------------------------------------------------------
# Invalid values — wrong types
# ---------------------------------------------------------------------------

def test_width_not_integer(tmp_path: Path) -> None:
    """A non-integer WIDTH must raise ValueError."""
    content = VALID.replace("WIDTH=10", "WIDTH=abc")
    with pytest.raises(ValueError):
        ConfigFile.parse(make_config(tmp_path, content))


def test_height_not_integer(tmp_path: Path) -> None:
    """A non-integer HEIGHT must raise ValueError."""
    content = VALID.replace("HEIGHT=5", "HEIGHT=abc")
    with pytest.raises(ValueError):
        ConfigFile.parse(make_config(tmp_path, content))


# ---------------------------------------------------------------------------
# Invalid values — Pydantic constraints (Field ge=4)
# ---------------------------------------------------------------------------

def test_width_too_small(tmp_path: Path) -> None:
    """WIDTH below 4 must raise a Pydantic ValidationError."""
    content = VALID.replace("WIDTH=10", "WIDTH=3")
    with pytest.raises(Exception):  # Pydantic ValidationError
        ConfigFile.parse(make_config(tmp_path, content))


def test_height_too_small(tmp_path: Path) -> None:
    """HEIGHT below 4 must raise a Pydantic ValidationError."""
    content = VALID.replace("HEIGHT=5", "HEIGHT=2")
    with pytest.raises(Exception):
        ConfigFile.parse(make_config(tmp_path, content))


# ---------------------------------------------------------------------------
# Coordinates out of bounds - model_validator
# ---------------------------------------------------------------------------

def test_entry_out_of_bounds(tmp_path: Path) -> None:
    """An ENTRY coordinate outside the maze bounds must be rejected."""
    content = VALID.replace("ENTRY=0,0", "ENTRY=99,0")
    with pytest.raises(Exception, match="out of bounds"):
        ConfigFile.parse(make_config(tmp_path, content))


def test_exit_out_of_bounds(tmp_path: Path) -> None:
    """An EXIT coordinate outside the maze bounds must be rejected."""
    content = VALID.replace("EXIT=9,4", "EXIT=9,99")
    with pytest.raises(Exception, match="out of bounds"):
        ConfigFile.parse(make_config(tmp_path, content))


def test_exit_x_equals_width_rejected(tmp_path: Path) -> None:
    """x=WIDTH is out of bounds (valid indices: 0..WIDTH-1)."""
    content = VALID.replace("EXIT=9,4", "EXIT=10,4")
    with pytest.raises(Exception):
        ConfigFile.parse(make_config(tmp_path, content))


def test_entry_negative_coordinate(tmp_path: Path) -> None:
    """A negative ENTRY coordinate must be rejected."""
    content = VALID.replace("ENTRY=0,0", "ENTRY=-1,0")
    with pytest.raises(Exception):
        ConfigFile.parse(make_config(tmp_path, content))


# ---------------------------------------------------------------------------
# ENTRY == EXIT must be rejected
# ---------------------------------------------------------------------------

def test_entry_equals_exit(tmp_path: Path) -> None:
    """ENTRY and EXIT at the same position must raise ValueError."""
    content = VALID.replace("EXIT=9,4", "EXIT=0,0")
    with pytest.raises(Exception, match="cannot be the same"):
        ConfigFile.parse(make_config(tmp_path, content))


# ---------------------------------------------------------------------------
# validate_assignment=True — modification post-construction
# ---------------------------------------------------------------------------

def test_validate_assignment_rejects_invalid_width(tmp_path: Path) -> None:
    config = ConfigFile.parse(make_config(tmp_path, VALID))
    with pytest.raises(Exception):
        config.WIDTH = 1
