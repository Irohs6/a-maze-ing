# tests/test_config_parser.py — Tests unitaires de ConfigFile.parse().
import pytest
from pathlib import Path
from model.config_file import ConfigFile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_config(tmp_path: Path, content: str) -> str:
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
"""


# ---------------------------------------------------------------------------
# Cas valides
# ---------------------------------------------------------------------------

def test_valid_config(tmp_path: Path) -> None:
    config = ConfigFile.parse(make_config(tmp_path, VALID))
    assert config.WIDTH == 10
    assert config.HEIGHT == 5
    assert config.ENTRY == (0, 0)
    assert config.EXIT == (9, 4)
    assert config.OUTPUT_FILE == "maze_output.txt"
    assert config.PERFECT is True


def test_comments_and_blank_lines_ignored(tmp_path: Path) -> None:
    content = """\
# commentaire
WIDTH=10

# autre commentaire
HEIGHT=5

ENTRY=0,0
EXIT=9,4
OUTPUT_FILE=maze.txt
PERFECT=True
"""
    config = ConfigFile.parse(make_config(tmp_path, content))
    assert config.WIDTH == 10
    assert config.HEIGHT == 5


def test_optional_seed_generated_if_absent(tmp_path: Path) -> None:
    config = ConfigFile.parse(make_config(tmp_path, VALID))
    assert config.SEED is not None
    assert isinstance(config.SEED, int)


def test_optional_seed_used_if_present(tmp_path: Path) -> None:
    content = VALID + "SEED=42\n"
    config = ConfigFile.parse(make_config(tmp_path, content))
    assert config.SEED == 42


def test_optional_playable_default_false(tmp_path: Path) -> None:
    config = ConfigFile.parse(make_config(tmp_path, VALID))
    assert config.PLAYABLE is False


def test_optional_playable_true(tmp_path: Path) -> None:
    content = VALID + "PLAYABLE=True\n"
    config = ConfigFile.parse(make_config(tmp_path, content))
    assert config.PLAYABLE is True


def test_perfect_false(tmp_path: Path) -> None:
    content = VALID.replace("PERFECT=True", "PERFECT=False")
    config = ConfigFile.parse(make_config(tmp_path, content))
    assert config.PERFECT is False


# ---------------------------------------------------------------------------
# Fichier introuvable
# ---------------------------------------------------------------------------

def test_file_not_found() -> None:
    with pytest.raises(FileNotFoundError, match="not found"):
        ConfigFile.parse("non_existent_config.txt")


# ---------------------------------------------------------------------------
# Clés obligatoires manquantes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("missing_key", [
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
])
def test_missing_required_key(tmp_path: Path, missing_key: str) -> None:
    lines = [line for line in VALID.splitlines()
             if not line.startswith(missing_key)]
    with pytest.raises(KeyError, match="has not properly been defined"):
        ConfigFile.parse(make_config(tmp_path, "\n".join(lines)))


# ---------------------------------------------------------------------------
# Syntaxe invalide
# ---------------------------------------------------------------------------

def test_line_missing_equals(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="missing '='"):
        ConfigFile.parse(make_config(tmp_path, "WIDTH=10\nINVALID_LINE\n"))


def test_empty_key(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Empty key"):
        ConfigFile.parse(make_config(tmp_path, "=some_value\n"))


def test_empty_value(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Empty value"):
        ConfigFile.parse(make_config(tmp_path, "WIDTH=\n"))


# ---------------------------------------------------------------------------
# Valeurs invalides — types
# ---------------------------------------------------------------------------

def test_width_not_integer(tmp_path: Path) -> None:
    content = VALID.replace("WIDTH=10", "WIDTH=abc")
    with pytest.raises(ValueError):
        ConfigFile.parse(make_config(tmp_path, content))


def test_height_not_integer(tmp_path: Path) -> None:
    content = VALID.replace("HEIGHT=5", "HEIGHT=abc")
    with pytest.raises(ValueError):
        ConfigFile.parse(make_config(tmp_path, content))


# ---------------------------------------------------------------------------
# Valeurs invalides — contraintes Pydantic (Field ge=4)
# ---------------------------------------------------------------------------

def test_width_too_small(tmp_path: Path) -> None:
    content = VALID.replace("WIDTH=10", "WIDTH=3")
    with pytest.raises(Exception):  # ValidationError de Pydantic
        ConfigFile.parse(make_config(tmp_path, content))


def test_height_too_small(tmp_path: Path) -> None:
    content = VALID.replace("HEIGHT=5", "HEIGHT=2")
    with pytest.raises(Exception):
        ConfigFile.parse(make_config(tmp_path, content))


# ---------------------------------------------------------------------------
# Coordonnées hors limites — model_validator
# ---------------------------------------------------------------------------

def test_entry_out_of_bounds(tmp_path: Path) -> None:
    content = VALID.replace("ENTRY=0,0", "ENTRY=99,0")
    with pytest.raises(Exception, match="out of bounds"):
        ConfigFile.parse(make_config(tmp_path, content))


def test_exit_out_of_bounds(tmp_path: Path) -> None:
    content = VALID.replace("EXIT=9,4", "EXIT=9,99")
    with pytest.raises(Exception, match="out of bounds"):
        ConfigFile.parse(make_config(tmp_path, content))


def test_exit_x_equals_width_rejected(tmp_path: Path) -> None:
    """x=WIDTH est hors limites (indices valides : 0..WIDTH-1)."""
    content = VALID.replace("EXIT=9,4", "EXIT=10,4")
    with pytest.raises(Exception):
        ConfigFile.parse(make_config(tmp_path, content))


def test_entry_negative_coordinate(tmp_path: Path) -> None:
    content = VALID.replace("ENTRY=0,0", "ENTRY=-1,0")
    with pytest.raises(Exception):
        ConfigFile.parse(make_config(tmp_path, content))


# ---------------------------------------------------------------------------
# ENTRY == EXIT interdit
# ---------------------------------------------------------------------------

def test_entry_equals_exit(tmp_path: Path) -> None:
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
