"""Contrat d'architecture hexagonale : chaque couche n'importe que les couches qui lui sont permises."""

import ast
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).parent.parent / "battleships"

# Couches que chaque couche n'a PAS le droit d'importer : le domaine ne dépend de rien, l'application que du domaine
FORBIDDEN_IMPORTS = {
    "domain": ("battleships.application", "battleships.clients"),
    "application": ("battleships.clients",),
}


def imported_modules(path: Path) -> list[str]:
    """Noms complets de tous les modules importés par un fichier source (import x et from x import y)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


LAYER_FILES = [(layer, path) for layer in FORBIDDEN_IMPORTS for path in sorted((PACKAGE_ROOT / layer).rglob("*.py"))]


@pytest.mark.parametrize(("layer", "path"), LAYER_FILES, ids=lambda item: getattr(item, "name", item))
def test_layer_only_imports_what_it_is_allowed_to(layer, path):
    """Le cœur ne connaît jamais ses clients : sans quoi changer d'interface obligerait à toucher au jeu."""
    forbidden = [module for module in imported_modules(path) if module.startswith(FORBIDDEN_IMPORTS[layer])]
    assert not forbidden, f"{layer}/{path.name} importe une couche interdite : {', '.join(forbidden)}"
