"""Contrat de documentation : chaque module, classe et fonction du projet explique son utilité dans une docstring."""

import ast

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_FILES = sorted(PROJECT_ROOT.glob("*.py")) + sorted((PROJECT_ROOT / "tests").glob("*.py"))


def missing_docstrings(path: Path) -> list[str]:
    """Noms des éléments sans docstring dans un fichier source : le module lui-même, ses classes et ses fonctions."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    missing = [] if ast.get_docstring(tree) else ["(module)"]
    missing += [node.name for node in ast.walk(tree) if isinstance(node, (ast.ClassDef, ast.FunctionDef))
                and not ast.get_docstring(node)]
    return missing


@pytest.mark.parametrize("path", SOURCE_FILES, ids=lambda path: path.relative_to(PROJECT_ROOT).as_posix())
def test_every_element_has_a_docstring(path):
    """Toute fonction, classe ou module du projet est documenté : la règle est vérifiée, pas seulement souhaitée."""
    missing = missing_docstrings(path)
    assert not missing, f"Sans docstring : {', '.join(missing)}"
