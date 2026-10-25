"""Contrat de documentation : chaque module, classe et fonction du projet explique son utilité dans une docstring."""

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_FILES = [
    path for folder in ("", "battleships", "tests") for path in sorted((PROJECT_ROOT / folder).glob("*.py"))
]


def missing_docstrings(path: Path) -> list[str]:
    """Noms des éléments sans docstring dans un fichier source : le module lui-même, ses classes et ses fonctions."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    missing = [] if ast.get_docstring(tree) else ["(module)"]
    missing += [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and not ast.get_docstring(node)
    ]
    return missing


@pytest.mark.parametrize("path", SOURCE_FILES, ids=lambda path: path.relative_to(PROJECT_ROOT).as_posix())
def test_every_element_has_a_docstring(path):
    """Toute fonction, classe ou module du projet est documenté : la règle est vérifiée, pas seulement souhaitée."""
    missing = missing_docstrings(path)
    assert not missing, f"Sans docstring : {', '.join(missing)}"
