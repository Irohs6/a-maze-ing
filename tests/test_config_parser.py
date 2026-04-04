# tests/test_config_parser.py — Tests unitaires du parseur de configuration.
# Couvre tous les scénarios de lecture et de validation du fichier config :
#   - fichier valide avec toutes les clés obligatoires
#   - fichier avec commentaires et lignes vides (doivent être ignorés)
#   - clés obligatoires manquantes (doit lever une exception)
#   - valeurs de types incorrects (ex. : WIDTH=abc)
#   - coordonnées hors limites du labyrinthe
#   - fichier inexistant ou chemin invalide
#   - clés optionnelles absentes (vérification des valeurs par défaut)

import pytest
from pathlib import Path
from model.config_parser import ConfigParser


def test_valid_config(tmp_path: Path) -> None:
    config_content = """\
# Sample valid configuration
WIDTH=10
HEIGHT=5
ENTRY=0,0
EXIT=9,4
OUTPUT_FILE=maze_output.txt
PERFECT=True
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    parser.parse()
    parser._validate_required_keys()
    parser._parse_coordinates()
    config = parser._get_config()

    assert config['WIDTH'] == 10
    assert config['HEIGHT'] == 5
    assert config['ENTRY'] == (0, 0)
    assert config['EXIT'] == (9, 4)


def test_missing_required_keys(tmp_path: Path) -> None:
    config_content = """\
WIDTH=10
ENTRY=0,0
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    parser.parse()
    with pytest.raises(KeyError) as excinfo:
        parser._validate_required_keys()
    assert "has not properly been defined" in str(excinfo.value)


def test_invalid_value_types(tmp_path: Path) -> None:
    config_content = """\
WIDTH=abc
HEIGHT=5
ENTRY=0,0
EXIT=9,4
OUTPUT_FILE=maze_output.txt
PERFECT=True
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    parser.parse()
    parser._validate_required_keys()
    with pytest.raises(ValueError) as excinfo:
        parser._parse_coordinates()
    assert "invalid literal" in str(excinfo.value)


def test_coordinates_out_of_bounds(tmp_path: Path) -> None:
    config_content = """\
WIDTH=10
HEIGHT=5
ENTRY=0,0
EXIT=20,20
OUTPUT_FILE=maze_output.txt
PERFECT=True
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    parser.parse()
    parser._validate_required_keys()
    with pytest.raises(ValueError) as excinfo:
        parser._parse_coordinates()
    assert "needs 2 positive integers" in str(excinfo.value)


def test_file_not_found() -> None:
    parser = ConfigParser("non_existent_config.txt")
    with pytest.raises(FileNotFoundError) as excinfo:
        parser.parse()
    assert "not found" in str(excinfo.value)


def test_coordinates_at_exact_boundary(tmp_path: Path) -> None:
    """EXIT=10,0 avec WIDTH=10 doit être rejeté.

    Les index valides pour x sont 0..WIDTH-1 (soit 0..9).
    Bug actuel : la condition utilise '>' au lieu de '>=' —
    x=10 passe sans erreur alors qu'il est hors limites.
    Ce test DOIT ÉCHOUER jusqu'à ce que le bug soit corrigé.
    """
    config_content = """\
WIDTH=10
HEIGHT=5
ENTRY=0,0
EXIT=10,4
OUTPUT_FILE=maze_output.txt
PERFECT=True
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    parser.parse()
    parser._validate_required_keys()
    with pytest.raises(ValueError) as excinfo:
        parser._parse_coordinates()
    assert "needs 2 positive integers" in str(excinfo.value)


def test_optional_keys_defaults(tmp_path: Path) -> None:
    config_content = """\
WIDTH=10
HEIGHT=5
ENTRY=0,0
EXIT=9,4
OUTPUT_FILE=maze_output.txt
PERFECT=True
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    parser.parse()
    parser._validate_required_keys()
    parser._parse_coordinates()
    config = parser._get_config()

    # Les clés optionnelles SEED et ALGORITHM ne doivent pas être présentes
    assert 'SEED' not in config
    assert 'ALGORITHM' not in config


def test_line_missing_equals(tmp_path: Path) -> None:
    config_content = """\
WIDTH=10
INVALID_LINE
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    with pytest.raises(ValueError) as excinfo:
        parser.parse()
    assert "missing '='" in str(excinfo.value)


def test_empty_key(tmp_path: Path) -> None:
    config_content = """\
=some_value
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    with pytest.raises(ValueError) as excinfo:
        parser.parse()
    assert "Empty key" in str(excinfo.value)


def test_empty_value(tmp_path: Path) -> None:
    config_content = """\
WIDTH=
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    with pytest.raises(ValueError) as excinfo:
        parser.parse()
    assert "Empty value" in str(excinfo.value)


def test_width_zero(tmp_path: Path) -> None:
    config_content = """\
WIDTH=0
HEIGHT=5
ENTRY=0,0
EXIT=0,4
OUTPUT_FILE=maze.txt
PERFECT=True
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    parser.parse()
    parser._validate_required_keys()
    with pytest.raises(ValueError) as excinfo:
        parser._parse_coordinates()
    assert "value is invalid" in str(excinfo.value)


def test_negative_height(tmp_path: Path) -> None:
    config_content = """\
WIDTH=10
HEIGHT=-3
ENTRY=0,0
EXIT=9,4
OUTPUT_FILE=maze.txt
PERFECT=True
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    parser.parse()
    parser._validate_required_keys()
    with pytest.raises(ValueError) as excinfo:
        parser._parse_coordinates()
    assert "value is invalid" in str(excinfo.value)


def test_entry_negative_coordinates(tmp_path: Path) -> None:
    config_content = """\
WIDTH=10
HEIGHT=5
ENTRY=-1,0
EXIT=9,4
OUTPUT_FILE=maze.txt
PERFECT=True
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    parser.parse()
    parser._validate_required_keys()
    with pytest.raises(ValueError) as excinfo:
        parser._parse_coordinates()
    assert "needs 2 positive integers" in str(excinfo.value)


def test_entry_too_many_values(tmp_path: Path) -> None:
    config_content = """\
WIDTH=10
HEIGHT=5
ENTRY=0,0,99
EXIT=9,4
OUTPUT_FILE=maze.txt
PERFECT=True
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    parser.parse()
    parser._validate_required_keys()
    with pytest.raises(ValueError) as excinfo:
        parser._parse_coordinates()
    assert "needs 2 positive integers" in str(excinfo.value)


def test_blank_lines_and_comments_ignored(tmp_path: Path) -> None:
    config_content = """\
# comment line
WIDTH=10

# another comment
HEIGHT=5

ENTRY=0,0
EXIT=9,4
OUTPUT_FILE=maze.txt
PERFECT=True
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    parser.parse()
    parser._validate_required_keys()
    parser._parse_coordinates()
    config = parser._get_config()

    assert config['WIDTH'] == 10
    assert config['HEIGHT'] == 5


def test_optional_keys_present(tmp_path: Path) -> None:
    config_content = """\
WIDTH=10
HEIGHT=5
ENTRY=0,0
EXIT=9,4
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=recursive_backtracker
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config_content)

    parser = ConfigParser(str(config_file))
    parser.parse()
    parser._validate_required_keys()
    config = parser._get_config()

    assert config['SEED'] == '42'
    assert config['ALGORITHM'] == 'recursive_backtracker'
